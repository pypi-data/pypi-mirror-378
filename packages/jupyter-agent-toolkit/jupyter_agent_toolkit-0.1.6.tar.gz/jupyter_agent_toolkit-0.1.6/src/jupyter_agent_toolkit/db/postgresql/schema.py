from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Mapping

from .connection import ConnectionManager
from .sql import (
    LIST_TABLES_ALL,
    LIST_TABLES_BY_SCHEMA,
    LIST_MATVIEWS_ALL,
    LIST_MATVIEWS_BY_SCHEMA,
    LIST_COLUMNS,
    LIST_INDEXES,
    LIST_CONSTRAINTS,
    EXPLAIN,
    EXPLAIN_ANALYZE,
    EXPLAIN_JSON,
    EXPLAIN_ANALYZE_JSON,
)

_LOG = logging.getLogger("jupyter_agent_toolkit.db.postgresql.schema")


def list_tables(manager: ConnectionManager, schema_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List base tables and views, optionally filtered by schema.

    Args:
        manager: ConnectionManager instance.
        schema_name: If provided, restrict results to this schema; otherwise list all.

    Returns:
        List of dict rows with: table_schema, table_name, table_type.
    """
    try:
        with manager.connection() as conn, conn.cursor() as cur:
            if schema_name:
                _LOG.debug("Listing tables for schema=%s", schema_name)
                cur.execute(LIST_TABLES_BY_SCHEMA, {"schema": schema_name})
            else:
                _LOG.debug("Listing tables (all schemas)")
                cur.execute(LIST_TABLES_ALL)
            return list(cur.fetchall())
    except Exception as e:
        _LOG.error("Failed to list tables: %s", str(e))
        raise RuntimeError(f"Failed to list tables: {e}") from e


def list_columns(manager: ConnectionManager, schema_name: str, table: str) -> List[Dict[str, Any]]:
    """
    List columns for a (schema, table).

    Args:
        manager: ConnectionManager instance.
        schema_name: Schema name.
        table: Table name.

    Returns:
        List of dict rows (column_name, data_type, is_nullable, column_default, ordinal_position).
    """
    if not schema_name or not table:
        raise ValueError("Both schema_name and table are required.")
    try:
        with manager.connection() as conn, conn.cursor() as cur:
            _LOG.debug("Listing columns for %s.%s", schema_name, table)
            cur.execute(LIST_COLUMNS, {"schema": schema_name, "table": table})
            return list(cur.fetchall())
    except Exception as e:
        _LOG.error("Failed to list columns for %s.%s: %s", schema_name, table, str(e))
        raise RuntimeError(f"Failed to list columns for {schema_name}.{table}: {e}") from e


def schema(
    manager: ConnectionManager,
    *,
    schema_name: Optional[str] = None,
    table: Optional[str] = None,
    include_indexes: bool = True,
    include_constraints: bool = True,
    include_matviews: bool = False,
) -> Dict[str, Any]:
    """
    Return schema information:
      - always: a table list (optionally including materialized views)
      - optionally: columns, constraints, indexes for a specific (schema, table)

    Args:
        manager: ConnectionManager instance.
        schema_name: Optional schema filter; REQUIRED when `table` is provided.
        table: Optional table name for detailed info.
        include_indexes: Include index metadata for (schema, table).
        include_constraints: Include constraints for (schema, table).
        include_matviews: Include materialized views alongside tables/views.

    Returns:
        Dict with keys: 'tables', and optionally 'columns', 'constraints', 'indexes'.
    """
    if table and not schema_name:
        raise ValueError("When requesting table details, schema_name must be provided.")

    out: Dict[str, Any] = {}

    # Base tables/views
    out["tables"] = list_tables(manager, schema_name)

    # Optionally add materialized views
    if include_matviews:
        try:
            with manager.connection() as conn, conn.cursor() as cur:
                if schema_name:
                    _LOG.debug("Listing materialized views for schema=%s", schema_name)
                    cur.execute(LIST_MATVIEWS_BY_SCHEMA, {"schema": schema_name})
                else:
                    _LOG.debug("Listing materialized views (all schemas)")
                    cur.execute(LIST_MATVIEWS_ALL)
                out["tables"].extend(list(cur.fetchall()))
        except Exception as e:
            _LOG.warning("Failed to list materialized views (continuing): %s", str(e))

    # Detailed table info
    if schema_name and table:
        out["columns"] = list_columns(manager, schema_name, table)

        if include_constraints:
            try:
                with manager.connection() as conn, conn.cursor() as cur:
                    _LOG.debug("Fetching constraints for %s.%s", schema_name, table)
                    cur.execute(LIST_CONSTRAINTS, {"schema": schema_name, "table": table})
                    out["constraints"] = list(cur.fetchall())
            except Exception as e:
                _LOG.error("Failed to fetch constraints for %s.%s: %s", schema_name, table, str(e))
                raise RuntimeError(f"Failed to fetch constraints for {schema_name}.{table}: {e}") from e

        if include_indexes:
            try:
                with manager.connection() as conn, conn.cursor() as cur:
                    _LOG.debug("Fetching indexes for %s.%s", schema_name, table)
                    cur.execute(LIST_INDEXES, {"schema": schema_name, "table": table})
                    out["indexes"] = list(cur.fetchall())
            except Exception as e:
                _LOG.error("Failed to fetch indexes for %s.%s: %s", schema_name, table, str(e))
                raise RuntimeError(f"Failed to fetch indexes for {schema_name}.{table}: {e}") from e

    return out


def explain(
    manager: ConnectionManager,
    sql: str,
    *,
    analyze: bool = False,
    params: Optional[Mapping[str, Any]] = None,
    fmt: str = "text",  # "text" | "json"
) -> Dict[str, Any]:
    """
    Return EXPLAIN (or EXPLAIN ANALYZE) for a given query.

    Args:
        manager: ConnectionManager instance.
        sql: SQL statement to explain (trusted text).
        analyze: If True, use EXPLAIN ANALYZE.
        params: Mapping of parameters for the inner statement.
        fmt: "text" (default) for classic plan lines, or "json" for structured plan.

    Returns:
        If fmt="text": {"analyze": bool, "format": "text", "plan": List[str]}
        If fmt="json": {"analyze": bool, "format": "json", "plan": Any}  # parsed JSON plan
    """
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("SQL to EXPLAIN must be a non-empty string.")
    fmt_norm = fmt.lower()
    if fmt_norm not in ("text", "json"):
        raise ValueError("fmt must be 'text' or 'json'.")

    try:
        template = (
            EXPLAIN_ANALYZE_JSON if (fmt_norm == "json" and analyze) else
            EXPLAIN_JSON        if (fmt_norm == "json")                 else
            EXPLAIN_ANALYZE     if analyze                              else
            EXPLAIN
        )
        stmt = template.format(sql=sql)

        with manager.connection() as conn, conn.cursor() as cur:
            _LOG.debug(
                "EXPLAIN%s %s (first 120 chars): %s",
                " ANALYZE" if analyze else "",
                fmt_norm.upper(),
                sql[:120].replace("\n", " "),
            )
            cur.execute(stmt, params or {})
            if not cur.description:
                return {"analyze": analyze, "format": fmt_norm, "plan": []}
            rows = list(cur.fetchall())

        if fmt_norm == "text":
            # One column "QUERY PLAN", one row per printed line.
            lines = [r["QUERY PLAN"] for r in rows]
            return {"analyze": analyze, "format": "text", "plan": lines}

        # JSON format is typically a single row with a single "QUERY PLAN" JSON value (list).
        plan_cell = rows[0]["QUERY PLAN"] if rows else []
        return {"analyze": analyze, "format": "json", "plan": plan_cell}

    except Exception as e:
        _LOG.error("EXPLAIN failed: %s", str(e))
        raise RuntimeError(f"EXPLAIN failed: {e}") from e