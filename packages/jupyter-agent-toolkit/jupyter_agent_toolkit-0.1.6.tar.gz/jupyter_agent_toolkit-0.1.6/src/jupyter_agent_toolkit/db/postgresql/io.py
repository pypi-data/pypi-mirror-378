from __future__ import annotations

import logging
import tempfile
import contextlib
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

_LOG = logging.getLogger("jupyter_agent_toolkit.db.postgresql.io")


def rows_to_dataframe(rows: Iterable[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert an iterable of row dictionaries into a pandas DataFrame.
    Returns an empty DataFrame when the iterable is empty.
    """
    data = list(rows)
    return pd.DataFrame(data) if data else pd.DataFrame()


def dataframe_to_arrow(df: pd.DataFrame, schema: Optional[pa.Schema] = None) -> pa.Table:
    """
    Convert a pandas DataFrame to a PyArrow Table.

    Args:
        df: Input DataFrame.
        schema: Optional explicit Arrow schema (recommended for all-null or mixed-type columns).
                Example:
                    >>> import pyarrow as pa
                    >>> sch = pa.schema([("id", pa.int64()), ("payload", pa.string())])
                    >>> table = dataframe_to_arrow(df, schema=sch)

    Returns:
        pyarrow.Table
    """
    return pa.Table.from_pandas(df, schema=schema, preserve_index=False)


def write_parquet(
    df: pd.DataFrame,
    path: str | Path,
    *,
    compression: str = "zstd",
    overwrite: bool = True,
    schema: Optional[pa.Schema] = None,
    file_mode: Optional[int] = None,
) -> str:
    """
    Write a DataFrame to a Parquet file atomically.

    Args:
        df: DataFrame to write.
        path: Target file path.
        compression: Compression codec ("zstd", "snappy", "gzip", "brotli", "none").
        overwrite: If False and file exists, raises FileExistsError.
        schema: Optional Arrow schema to enforce column types.
        file_mode: Optional chmod mode to apply after write (e.g., 0o640).
                   Note: may have no effect on Windows filesystems.

    Returns:
        Absolute path to the written file.

    Raises:
        FileExistsError: if overwrite=False and file already exists.
        ValueError: for unsupported compression values.
        RuntimeError: if writing fails.
    """
    p = Path(path)
    if p.exists() and not overwrite:
        raise FileExistsError(str(p))

    # Normalize compression
    comp = compression.lower()
    allowed = {"zstd", "snappy", "gzip", "brotli", "none"}
    if comp not in allowed:
        raise ValueError(f"Unsupported compression codec: {compression!r}. Allowed: {sorted(allowed)}")

    p.parent.mkdir(parents=True, exist_ok=True)

    try:
        table = dataframe_to_arrow(df, schema=schema)

        # Atomic write: temp file in same directory, then replace
        with tempfile.NamedTemporaryFile(dir=p.parent, delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            pq.write_table(table, tmp_path, compression=None if comp == "none" else comp)
            if file_mode is not None:
                tmp_path.chmod(file_mode)
            tmp_path.replace(p)  # atomic on POSIX
        except Exception:
            with contextlib.suppress(Exception):
                tmp_path.unlink(missing_ok=True)  # cleanup temp file if something goes wrong
            raise

        if df.empty:
            _LOG.debug("Wrote empty parquet file: %s", str(p.resolve()))
        else:
            _LOG.debug("Wrote parquet file (%d rows, %d cols): %s", len(df), df.shape[1], str(p.resolve()))

        return str(p.resolve())

    except FileExistsError:
        raise
    except Exception as e:
        _LOG.error("Failed to write parquet file: %s", str(e))
        raise RuntimeError(f"Failed to write parquet file: {e}") from e