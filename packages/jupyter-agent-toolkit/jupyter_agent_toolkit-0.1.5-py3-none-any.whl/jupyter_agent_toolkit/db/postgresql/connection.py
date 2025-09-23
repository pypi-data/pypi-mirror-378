from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Optional, Tuple, Any, Iterator, Dict
from contextlib import contextmanager
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


def _import_psycopg() -> Tuple[Any, Any]:
    """
    Lazy-import psycopg so modules can import before the kernel has drivers installed.

    Returns:
        (psycopg, dict_row)

    Raises:
        RuntimeError: if psycopg isn't available in the kernel env.
    """
    try:
        import psycopg  # type: ignore
        from psycopg.rows import dict_row  # type: ignore
        return psycopg, dict_row
    except Exception as e:
        raise RuntimeError(
            "psycopg is required in the Jupyter kernel. Install with: pip install 'psycopg[binary]'"
        ) from e


def _maybe_pool():
    """Return psycopg_pool.ConnectionPool if available, else None."""
    try:
        from psycopg_pool import ConnectionPool  # type: ignore
        return ConnectionPool
    except Exception:
        return None

def _redact_dsn(dsn: str) -> str:
    """
    Produce a redacted, log-safe view of a DSN (no password).
    Never raises: falls back to a generic string on parse errors.
    """
    try:
        u = urlparse(dsn)
        # If urlparse couldn't recognize a scheme, treat as raw DSN string (space-separated)
        if not u.scheme:
            return "dsn=<raw>; (unable to parse safely for redaction)"
        user = u.username or ""
        host = u.hostname or ""
        db = (u.path or "").lstrip("/")
        q = dict(parse_qsl(u.query))
        return f"driver={u.scheme} user={user} host={host} port={u.port} db={db} sslmode={q.get('sslmode')!r}"
    except Exception:
        return "dsn=<unparsed>; (redaction parse failed)"

def _ensure_sslmode(dsn: str, default: str = "require") -> str:
    """
    Ensure DSN contains an sslmode. If missing, add ?sslmode=<default>.
    Never raises on parse errors; returns original DSN if parsing fails.
    """
    try:
        u = urlparse(dsn)
        if not u.scheme:
            return dsn  # don't touch opaque/raw DSN
        q = dict(parse_qsl(u.query))
        if "sslmode" not in q:
            q["sslmode"] = default
            return urlunparse((u.scheme, u.netloc, u.path, u.params, urlencode(q), u.fragment))
        return dsn
    except Exception:
        return dsn

def dsn_from_env(*, require_ssl: bool = False, default_sslmode: str = "require") -> str:
    """
    Resolve DSN from kernel environment variables in this order:
      - PG_DSN
      - POSTGRES_DSN
      - DATABASE_URL

    Args:
        require_ssl: If True, add sslmode=<default_sslmode> when absent.
        default_sslmode: sslmode to use when require_ssl=True and DSN has none.

    Raises:
        RuntimeError: if no DSN env var is set.
    """
    dsn = os.environ.get("PG_DSN") or os.environ.get("POSTGRES_DSN") or os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("Set PG_DSN / POSTGRES_DSN / DATABASE_URL in the kernel environment.")
    return _ensure_sslmode(dsn, default_sslmode) if require_ssl else dsn


@dataclass(frozen=True)
class ConnectionInfo:
    """
    Connection configuration used by ConnectionManager.

    Attributes:
        dsn: PostgreSQL connection string (can include ?sslmode=...).
        connect_timeout: TCP/connection timeout (seconds).
        application_name: Appears in pg_stat_activity for observability.
        statement_timeout_ms: Per-session statement timeout (ms). None = don't set.
        search_path: Optional schema search_path to set after connect. May be str or list[str].
        autocommit: Enable autocommit (default True for notebook workflows).
        session_settings: Extra key/value pairs applied via `SET <key> = <value>`.
                          Keys are treated as identifiers; values are bound as parameters.
    """
    dsn: str
    connect_timeout: int = 10
    application_name: str = "jupyter-agent-toolkit"
    statement_timeout_ms: Optional[int] = 30_000
    search_path: Optional[str | list[str]] = None
    autocommit: bool = True
    session_settings: Optional[Dict[str, str | int]] = None


class ConnectionManager:
    """
    Manages PostgreSQL connections for the kernel, with optional pooling.

    - Applies session settings (statement_timeout, search_path, application_name, extra session_settings).
    - Uses dict_row row factory for dict results.
    - Adds logging for connection attempts and errors.
    - Provides health-check for connection pool.

    Note:
        autocommit=True by default because notebook workflows are typically read-heavy,
        avoid dangling transactions, and need immediate effect for session SETs.
    """

    def __init__(
        self,
        info: ConnectionInfo,
        *,
        use_pool: bool = False,
        pool_min_size: int = 1,
        pool_max_size: int = 5,
        pool_timeout: int = 30,
    ):
        self.info = info
        self._pool = None
        self.logger = logging.getLogger("jupyter_agent_toolkit.db.postgresql.ConnectionManager")
        if use_pool:
            ConnectionPool = _maybe_pool()
            if ConnectionPool is None:
                raise RuntimeError("psycopg_pool is required for pooling. pip install psycopg_pool")
            try:
                self._pool = ConnectionPool(
                    info.dsn, min_size=pool_min_size, max_size=pool_max_size, timeout=pool_timeout
                )
                self.logger.info("Initialized connection pool (min=%d, max=%d)", pool_min_size, pool_max_size)
            except Exception as e:
                self.logger.error("Failed to initialize connection pool: %s", str(e))
                raise

    @classmethod
    def from_env(cls, **kwargs) -> "ConnectionManager":
        """
        Create a ConnectionManager using DSN from kernel env vars.

        Kwargs are forwarded to the constructor (e.g., use_pool=True).
        """
        # If you want to force SSL when users rely on env vars, flip require_ssl=True here:
        # dsn = dsn_from_env(require_ssl=True)
        dsn = dsn_from_env()
        return cls(ConnectionInfo(dsn=dsn), **kwargs)

    # ---- internals ----

    def _apply_session_settings(self, conn) -> None:
        """
        Apply session-level settings on a connection.

        Uses SET (not SET LOCAL) so changes persist for the session even when autocommit=True.
        """
        st = self.info.statement_timeout_ms
        sp = self.info.search_path
        extra = self.info.session_settings or {}

        with conn.cursor() as cur:
            if st is not None:
                cur.execute(f"SET statement_timeout = {int(st)}")

            if sp:
                # Accept either "public, analytics" or ["public", "analytics"]
                if isinstance(sp, str):
                    cur.execute("SET search_path = %s", (sp,))
                else:
                    psycopg, _ = _import_psycopg()
                    SQL, Identifier = psycopg.sql.SQL, psycopg.sql.Identifier  # type: ignore[attr-defined]
                    parts = [Identifier(s) for s in sp]
                    query = SQL("SET search_path TO {}").format(SQL(", ").join(parts))
                    cur.execute(query)

            # Additional arbitrary session settings, e.g. {"work_mem": "64MB", "timezone": "UTC"}
            for key, value in extra.items():
                psycopg, _ = _import_psycopg()
                SQL, Identifier = psycopg.sql.SQL, psycopg.sql.Identifier  # type: ignore[attr-defined]
                stmt = SQL("SET {} = %s").format(Identifier(str(key)))
                cur.execute(stmt, (value,))

    def _new_connection(self):
        """
        Open and configure a new psycopg connection.

        Logs a redacted DSN (no secrets) on connect attempts.
        """
        psycopg, dict_row = _import_psycopg()
        try:
            self.logger.info("Attempting to connect to PostgreSQL server (%s).", _redact_dsn(self.info.dsn))
            conn = psycopg.connect(
                self.info.dsn,
                connect_timeout=self.info.connect_timeout,
                row_factory=dict_row,
                application_name=self.info.application_name,
            )
            conn.autocommit = self.info.autocommit
            self._apply_session_settings(conn)
            self.logger.info("Connection established successfully.")
            return conn
        except Exception as e:
            self.logger.error("Failed to connect to PostgreSQL: %s", str(e))
            raise RuntimeError(f"Failed to connect to PostgreSQL: {e}") from e

    @contextmanager
    def connection(self) -> Iterator[Any]:
        """
        Context manager yielding a connection (new or from pool).
        Ensures settings are applied and connections are properly closed/returned.
        """
        if self._pool is None:
            conn = self._new_connection()
            try:
                yield conn
            finally:
                try:
                    conn.close()
                except Exception as e:
                    self.logger.warning("Error closing connection: %s", str(e))
        else:
            conn = self._pool.connection()  # type: ignore[assignment]
            try:
                # Re-apply settings on checkout, because pooled connections are reused.
                self._apply_session_settings(conn)
                yield conn
            finally:
                try:
                    conn.close()
                except Exception as e:
                    self.logger.warning("Error closing pooled connection: %s", str(e))

    def close(self) -> None:
        """Close the connection pool (if any)."""
        try:
            if self._pool:
                self._pool.close()
                self.logger.info("Connection pool closed.")
        except Exception as e:
            self.logger.warning("Error closing connection pool: %s", str(e))

    def pool_health(self) -> dict:
        """Return health status of the connection pool if pooling is enabled."""
        if not self._pool:
            return {"pool": False, "status": "No pool"}
        try:
            stats = {"pool": True, "status": "ok"}
            for attr in ("min_size", "max_size", "used", "free", "max_waiting", "current_size"):
                if hasattr(self._pool, attr):
                    stats[attr] = getattr(self._pool, attr)
            if hasattr(self._pool, "get_stats"):
                stats.update(self._pool.get_stats())  # type: ignore[attr-defined]
            return stats
        except Exception as e:
            self.logger.warning("Error checking pool health: %s", str(e))
            return {"pool": True, "status": f"error: {e}"}