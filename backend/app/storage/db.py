"""DuckDB connection management and schema initialization."""
from contextlib import contextmanager
from typing import Iterator

import duckdb

from app.config import settings


def get_connection() -> duckdb.DuckDBPyConnection:
    """Get a DuckDB connection. Creates the data directory if needed."""
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(settings.duckdb_path))


@contextmanager
def db_connection() -> Iterator[duckdb.DuckDBPyConnection]:
    """Context manager for a DuckDB connection. Auto-closes."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_schema() -> None:
    """Create all tables if they do not exist. Idempotent."""
    with db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS universe (
                ticker VARCHAR PRIMARY KEY,
                company_name VARCHAR NOT NULL,
                sector VARCHAR,
                industry VARCHAR,
                market_cap BIGINT,
                exchange VARCHAR,
                index_membership VARCHAR,
                last_updated TIMESTAMP NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_universe_sector ON universe(sector)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_universe_mktcap ON universe(market_cap)")


if __name__ == "__main__":
    init_schema()
    print(f"Schema initialized at {settings.duckdb_path}")
