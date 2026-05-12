"""Universe ingestion: fetch S&P 500 constituents and load into DuckDB."""
import time
from datetime import datetime, timezone
from io import StringIO
from typing import Optional

import httpx
import pandas as pd
import yfinance as yf

from app.storage.db import db_connection


SP500_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
USER_AGENT = "StockGPT/0.1 (https://github.com/Biswajit107927/StockGPT; educational project)"


def fetch_sp500_constituents() -> pd.DataFrame:
    """Scrape the current S&P 500 list from Wikipedia."""
    response = httpx.get(
        SP500_WIKI_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
        follow_redirects=True,
    )
    response.raise_for_status()

    tables = pd.read_html(StringIO(response.text))
    df = tables[0]

    df = df.rename(columns={
        "Symbol": "ticker",
        "Security": "company_name",
        "GICS Sector": "sector",
        "GICS Sub-Industry": "industry",
    })

    df["ticker"] = df["ticker"].str.replace(".", "-", regex=False)
    df["exchange"] = "US"
    df["index_membership"] = "SP500"

    return df[["ticker", "company_name", "sector", "industry", "exchange", "index_membership"]]


def fetch_market_cap(ticker: str) -> Optional[int]:
    """Get the current market cap for a single ticker from yfinance.

    Returns None on rate limit or other error.
    """
    try:
        info = yf.Ticker(ticker).info
        return info.get("marketCap")
    except Exception as e:
        print(f"  warn: could not fetch market cap for {ticker}: {e}")
        return None


def enrich_with_market_caps(
    df: pd.DataFrame,
    limit: Optional[int] = None,
    sleep_seconds: float = 1.0,
) -> pd.DataFrame:
    """Add market_cap column to the DataFrame.

    All rows get a market_cap column. Rows beyond `limit` get None.
    `sleep_seconds` adds a delay between yfinance calls to dodge rate limits.
    """
    df = df.copy()
    df["market_cap"] = None

    if limit is None:
        target_indices = df.index
    else:
        target_indices = df.index[:limit]

    print(f"Fetching market caps for {len(target_indices)} tickers "
          f"(out of {len(df)} total)...")

    for i, idx in enumerate(target_indices, 1):
        ticker = df.at[idx, "ticker"]
        mc = fetch_market_cap(ticker)
        df.at[idx, "market_cap"] = mc

        if i % 25 == 0:
            print(f"  progress: {i}/{len(target_indices)}")

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    return df


def upsert_universe(df: pd.DataFrame) -> int:
    """Insert or update rows in the universe table. Returns row count."""
    df = df.copy()
    df["last_updated"] = datetime.now(timezone.utc)

    with db_connection() as conn:
        conn.register("staging_universe", df)
        conn.execute("""
            INSERT OR REPLACE INTO universe
            SELECT
                ticker,
                company_name,
                sector,
                industry,
                CAST(market_cap AS BIGINT) AS market_cap,
                exchange,
                index_membership,
                last_updated
            FROM staging_universe
        """)
        result = conn.execute("SELECT COUNT(*) FROM universe").fetchone()
        return result[0] if result else 0


def run(limit: Optional[int] = None, sleep_seconds: float = 1.0) -> None:
    """End-to-end universe ingestion.

    All 503 tickers are always loaded. `limit` only controls how many
    get market cap enrichment from yfinance.
    """
    print("Fetching S&P 500 constituents from Wikipedia...")
    df = fetch_sp500_constituents()
    print(f"  found {len(df)} tickers")

    df = enrich_with_market_caps(df, limit=limit, sleep_seconds=sleep_seconds)

    print("Upserting into DuckDB...")
    count = upsert_universe(df)
    print(f"  universe table now has {count} rows")

    with db_connection() as conn:
        enriched = conn.execute(
            "SELECT COUNT(*) FROM universe WHERE market_cap IS NOT NULL"
        ).fetchone()[0]
    print(f"  of which {enriched} have market cap data")


if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(limit=limit)