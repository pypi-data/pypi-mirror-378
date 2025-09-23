from __future__ import annotations

from typing import Any, Mapping, Optional

from .connection import ConnectionInfo, ConnectionManager
from .queries import query_rows, query_df, stream_to_parquet
from .schema import list_tables, list_columns, schema as schema_info, explain as explain_plan

__all__ = [
    # Connection primitives
    "ConnectionInfo",
    "ConnectionManager",
    # High-level client
    "PostgresClient",
    # Functional API (re-exported)
    "query_rows",
    "query_df",
    "stream_to_parquet",
    "list_tables",
    "list_columns",
    "schema",
    "explain",
]


class PostgresClient:
    """
    Kernel-side façade for PostgreSQL that wraps a :class:`ConnectionManager`
    and exposes ergonomic query/schema helpers.

    This class is intended to be used *inside a Jupyter kernel* (e.g., called
    by tools injected via your MCP server). It does not manage secrets; provide
    a DSN explicitly or via environment variables in the kernel.

    Typical usage:
        >>> pg = PostgresClient.from_env()
        >>> rows = pg.query_rows("SELECT 1 AS x")
        >>> df = pg.query_df("SELECT * FROM my_table", limit=10)
        >>> pg.close()

    You can also use it as a context manager to auto-close pooled connections:
        >>> with PostgresClient.from_env() as pg:
        ...     print(pg.list_tables())
    """

    def __init__(self, manager: ConnectionManager):
        """
        Initialize the client with a preconfigured :class:`ConnectionManager`.

        Args:
            manager: ConnectionManager instance controlling connections/pool.
        """
        self._m = manager

    # --------- constructors ---------

    @classmethod
    def from_env(cls, **kwargs) -> "PostgresClient":
        """
        Create a client using DSN from PG_DSN / POSTGRES_DSN / DATABASE_URL
        environment variables in the *kernel* process.

        Any keyword args are forwarded to :class:`ConnectionManager` (e.g.
        `use_pool=True`, pool sizes, etc.).
        """
        return cls(ConnectionManager.from_env(**kwargs))

    @classmethod
    def from_dsn(cls, dsn: str, **kwargs) -> "PostgresClient":
        """
        Create a client from an explicit DSN string.

        Args:
            dsn: PostgreSQL connection string.
            **kwargs: forwarded to :class:`ConnectionManager`.
        """
        return cls(ConnectionManager(ConnectionInfo(dsn=dsn), **kwargs))

    @classmethod
    def from_info(cls, info: ConnectionInfo, **kwargs) -> "PostgresClient":
        """
        Create a client from a prebuilt :class:`ConnectionInfo`.

        Args:
            info: ConnectionInfo with DSN and session settings.
            **kwargs: forwarded to :class:`ConnectionManager`.
        """
        return cls(ConnectionManager(info, **kwargs))

    # --------- context manager support ---------

    def __enter__(self) -> "PostgresClient":
        """Enable `with PostgresClient(...) as pg:` usage."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Close underlying pool (if any) when leaving a context."""
        self.close()

       # -------------------- querying --------------------

    def query_rows(
        self,
        sql: str | None = None,
        *,
        # table-mode (identifier-safe)
        schema_name: str | None = None,
        table_name: str | None = None,
        columns: list[str] | str = "*",
        where: str | None = None,
        order_by: str | None = None,
        # common
        limit: int | None = None,
        params: Mapping[str, Any] | None = None,
    ):
        """
        Execute a query and return rows.

        Two modes:
        - Raw SQL mode: provide `sql="SELECT ..."` (+ optional params/limit).
        - Table mode (identifier-safe): provide `schema_name` and `table_name`
          (+ optional columns/where/order_by/limit/params).
        """
        return query_rows(
            self._m,
            sql,
            schema_name=schema_name,
            table_name=table_name,
            columns=columns,
            where=where,
            order_by=order_by,
            limit=limit,
            params=params,
        )

    def query_df(
        self,
        sql: str | None = None,
        *,
        schema_name: str | None = None,
        table_name: str | None = None,
        columns: list[str] | str = "*",
        where: str | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        params: Mapping[str, Any] | None = None,
    ):
        """DataFrame variant of `query_rows` (same two modes)."""
        return query_df(
            self._m,
            sql,
            schema_name=schema_name,
            table_name=table_name,
            columns=columns,
            where=where,
            order_by=order_by,
            limit=limit,
            params=params,
        )

    def stream_to_parquet(
        self,
        sql: str,
        path: str,
        params: Mapping[str, Any] | None = None,
        *,
        chunk_rows: int = 50_000,
        progress_every: int = 10,
    ) -> str:
        """
        Stream a large SELECT result to a Parquet file atomically.
        """
        return stream_to_parquet(
            self._m,
            sql,
            path,
            params=params,
            chunk_rows=chunk_rows,
            progress_every=progress_every,
        )

    # --------------------- schema ---------------------

    def list_tables(self, schema_name: Optional[str] = None):
        """
        List base tables and views, optionally filtered by schema.

        Returns a list of dict rows with keys:
        - table_schema, table_name, table_type
        """
        return list_tables(self._m, schema_name)

    def list_columns(self, schema_name: str, table: str):
        """
        List columns for a (schema, table).

        Returns dict rows:
        - column_name, data_type, is_nullable, column_default, ordinal_position
        """
        return list_columns(self._m, schema_name, table)

    def schema(
        self,
        *,
        schema_name: Optional[str] = None,
        table: Optional[str] = None,
        include_indexes: bool = True,
        include_constraints: bool = True,
        include_matviews: bool = False,
    ):
        """
        Return tables and, if specified, details (columns/indexes/constraints)
        for a specific (schema, table).

        See :func:`schema_info` for details on keys in the returned dict.
        """
        return schema_info(
            self._m,
            schema_name=schema_name,
            table=table,
            include_indexes=include_indexes,
            include_constraints=include_constraints,
            include_matviews=include_matviews,
        )

    # --------------------- explain --------------------

    def explain(
        self,
        sql: str,
        *,
        analyze: bool = False,
        params: Optional[Mapping[str, Any]] = None,
        fmt: str = "text",  # "text" | "json"
    ):
        """
        Return EXPLAIN/EXPLAIN ANALYZE plan in text or JSON format.

        See :func:`explain_plan` for result structure.
        """
        return explain_plan(self._m, sql, analyze=analyze, params=params, fmt=fmt)

    # ------------------ lifecycle / misc ---------------------

    def close(self) -> None:
        """Close underlying pool (if any)."""
        self._m.close()

    def pool_health(self) -> dict:
        """Expose pool health from the underlying ConnectionManager."""
        return self._m.pool_health()


# Back-compat functional exports (nice to import directly from the package)
schema = schema_info
explain = explain_plan