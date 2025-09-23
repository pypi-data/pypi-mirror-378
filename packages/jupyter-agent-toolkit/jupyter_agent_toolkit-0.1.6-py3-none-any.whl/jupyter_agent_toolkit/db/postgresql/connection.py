from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Iterator, Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# ───────────────────────── internals / utils ─────────────────────────

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


def _with_query_param(dsn: str, key: str, value: Optional[str]) -> str:
    """
    Return DSN with a specific query parameter set (or removed if value is None).
    Silently returns input on parse errors or when DSN has no URI scheme.
    """
    try:
        u = urlparse(dsn)
        if not u.scheme:
            return dsn
        q = dict(parse_qsl(u.query))
        if value is None:
            q.pop(key, None)
        else:
            q[key] = value
        return urlunparse((u.scheme, u.netloc, u.path, u.params, urlencode(q), u.fragment))
    except Exception:
        return dsn


def _ensure_sslmode(dsn: str, default: str = "require", *, enforce_minimum: bool = False) -> str:
    """
    Ensure DSN contains an sslmode. If missing, add ?sslmode=<default>.
    If enforce_minimum=True and sslmode is present but weak (disable/allow/prefer),
    replace it with <default>. Never raises on parse errors; returns original DSN if parsing fails.
    """
    try:
        u = urlparse(dsn)
        if not u.scheme:
            return dsn  # don't touch opaque/raw DSN
        q = dict(parse_qsl(u.query))
        if "sslmode" not in q:
            q["sslmode"] = default
            return urlunparse((u.scheme, u.netloc, u.path, u.params, urlencode(q), u.fragment))
        if enforce_minimum:
            insecure = {"disable", "allow", "prefer"}
            if str(q.get("sslmode", "")).lower() in insecure:
                q["sslmode"] = default
                return urlunparse((u.scheme, u.netloc, u.path, u.params, urlencode(q), u.fragment))
        return dsn
    except Exception:
        return dsn


def _override_sslmode(dsn: str, new_mode: str) -> str:
    """Force-override sslmode to new_mode; returns original DSN on parse errors."""
    return _with_query_param(dsn, "sslmode", new_mode)


def _is_localhost_host(dsn: str) -> bool:
    """Heuristic: treat DSN host as localhost/loopback when safe to fall back to non-SSL."""
    try:
        u = urlparse(dsn)
        host = (u.hostname or "").lower()
        return host in {"", "localhost", "127.0.0.1", "::1"}
    except Exception:
        return False


def dsn_from_env(*, require_ssl: bool = False, default_sslmode: str = "require") -> str:
    """
    Resolve DSN from kernel environment variables in this order:
      - PG_DSN
      - POSTGRES_DSN
      - DATABASE_URL

    Args:
        require_ssl: If True, ensure DSN has sslmode>=<default_sslmode>.
        default_sslmode: sslmode to use when require_ssl=True and DSN has none (or is weak).

    Raises:
        RuntimeError: if no DSN env var is set.
    """
    dsn = os.environ.get("PG_DSN") or os.environ.get("POSTGRES_DSN") or os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("Set PG_DSN / POSTGRES_DSN / DATABASE_URL in the kernel environment.")
    return _ensure_sslmode(dsn, default_sslmode, enforce_minimum=require_ssl) if require_ssl else dsn


# ───────────────────────── public config types ─────────────────────────

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


# ───────────────────────── manager ─────────────────────────

class ConnectionManager:
    """
    Manages PostgreSQL connections for the kernel, with optional pooling.

    - Applies session settings (statement_timeout, search_path, application_name, extra session_settings).
    - Uses dict_row row factory for dict results.
    - Adds logging for connection attempts and errors.
    - Provides health-check for connection pool.

    Security defaults:
        - SSL is ON by default when building from env (see from_env()).
        - You may optionally enable a guarded fallback to non-SSL on SSL errors.

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
        # transient failure handling
        connect_retries: int = 0,
        connect_backoff_base: float = 0.5,
        # SSL fallback policy
        ssl_fallback_on_error: bool = False,
        ssl_fallback_allow_any_host: bool = False,
    ):
        """
        Args:
            info: ConnectionInfo (includes DSN).
            use_pool: Enable psycopg_pool if available.
            pool_min_size / pool_max_size / pool_timeout: Pool settings.
            connect_retries: Additional attempts after the first try (defaults to 0).
            connect_backoff_base: Initial sleep in seconds; doubles each retry. 0 disables sleeping.
            ssl_fallback_on_error: If True, and a connect attempt fails, try again once with sslmode=disable.
                                   This is **insecure** and should be used for local dev only.
            ssl_fallback_allow_any_host: By default, fallback is allowed only for localhost/127.0.0.1.
                                         Set True to allow fallback for any host (NOT recommended).
        """
        self.info = info
        self._pool = None
        self.logger = logging.getLogger("jupyter_agent_toolkit.db.postgresql.ConnectionManager")
        self._connect_retries = max(0, int(connect_retries))
        self._connect_backoff_base = max(0.0, float(connect_backoff_base))
        self._ssl_fallback_on_error = bool(ssl_fallback_on_error)
        self._ssl_fallback_allow_any_host = bool(ssl_fallback_allow_any_host)

        if use_pool:
            ConnectionPool = _maybe_pool()
            if ConnectionPool is None:
                raise RuntimeError("psycopg_pool is required for pooling. pip install psycopg_pool")
            try:
                # Try to initialize pool with the primary DSN
                self._pool = ConnectionPool(
                    info.dsn, min_size=pool_min_size, max_size=pool_max_size, timeout=pool_timeout
                )
                self.logger.info("Initialized connection pool (min=%d, max=%d)", pool_min_size, pool_max_size)
            except Exception as e:
                # Optional fallback: recreate pool with non-SSL DSN if allowed
                if self._should_attempt_ssl_fallback(info.dsn):
                    try:
                        insecure_dsn = _override_sslmode(info.dsn, "disable")
                        self._pool = ConnectionPool(
                            insecure_dsn, min_size=pool_min_size, max_size=pool_max_size, timeout=pool_timeout
                        )
                        self.logger.warning(
                            "Initialized connection pool WITHOUT SSL after failure. Host is local and "
                            "ssl_fallback_on_error=True. DSN=%s",
                            _redact_dsn(insecure_dsn),
                        )
                    except Exception as e2:
                        self.logger.error("Failed to initialize connection pool (fallback also failed): %s", e2)
                        raise
                else:
                    self.logger.error("Failed to initialize connection pool: %s", str(e))
                    raise

    @classmethod
    def from_env(
        cls,
        *,
        force_ssl: bool = True,
        **kwargs,
    ) -> "ConnectionManager":
        """
        Create a ConnectionManager using DSN from kernel env vars.

        Args:
            force_ssl: When True (default), ensure sslmode is present and at least 'require'.
            **kwargs: Forwarded to the constructor (e.g., use_pool=True, connect_retries=2,
                      ssl_fallback_on_error=True).
        """
        dsn = dsn_from_env(require_ssl=force_ssl)
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

    def _should_attempt_ssl_fallback(self, dsn: str) -> bool:
        """Policy gate for insecure fallback."""
        if not self._ssl_fallback_on_error:
            return False
        if self._ssl_fallback_allow_any_host:
            return True
        return _is_localhost_host(dsn)

    def _try_connect_once(self, dsn: str):
        psycopg, dict_row = _import_psycopg()
        self.logger.info("Attempting to connect to PostgreSQL server (%s).", _redact_dsn(dsn))
        conn = psycopg.connect(
            dsn,
            connect_timeout=self.info.connect_timeout,
            row_factory=dict_row,
            application_name=self.info.application_name,
        )
        conn.autocommit = self.info.autocommit
        self._apply_session_settings(conn)
        self.logger.info("Connection established successfully.")
        return conn

    def _new_connection(self):
        """
        Open and configure a new psycopg connection.

        Behavior:
          - Attempt primary DSN with optional retries/backoff.
          - If all attempts fail and policy allows, try once more with sslmode=disable.
        """
        attempts = self._connect_retries + 1
        delay = self._connect_backoff_base
        last_exc = None

        # Primary attempts with the configured DSN
        for i in range(1, attempts + 1):
            try:
                return self._try_connect_once(self.info.dsn)
            except Exception as e:
                last_exc = e
                self.logger.error("Failed to connect to PostgreSQL (attempt %d/%d): %s", i, attempts, str(e))
                if i < attempts and delay > 0:
                    time.sleep(delay)
                    delay *= 2.0

        # Optional: insecure fallback
        if self._should_attempt_ssl_fallback(self.info.dsn):
            insecure_dsn = _override_sslmode(self.info.dsn, "disable")
            try:
                self.logger.warning(
                    "SSL connection failed; attempting NON-SSL fallback (development only). DSN=%s",
                    _redact_dsn(insecure_dsn),
                )
                return self._try_connect_once(insecure_dsn)
            except Exception as e2:
                last_exc = e2
                self.logger.error("NON-SSL fallback also failed: %s", str(e2))

        raise RuntimeError(f"Failed to connect to PostgreSQL: {last_exc}") from last_exc

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
        """
        Return health status of the connection pool if pooling is enabled.

        Notes:
            Fields present depend on the pool implementation/version. Common keys include:
            min_size, max_size, used, free, max_waiting, current_size. Additional keys may
            be returned when the pool exposes get_stats().
        """
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