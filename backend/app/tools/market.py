"""Market-data tools that the agent can call.

Each function here is designed to be called by the LLM via tool use.
Design principles:
- Narrow scope: each function does one thing
- Typed parameters and return values (Pydantic for the schema)
- Deterministic: same inputs produce same outputs
- Read-only: tools query, they don't mutate

The function docstrings are the interface contract with the LLM.
Be specific. The LLM reads them to decide when to call each tool.
"""
from typing import Optional

from pydantic import BaseModel, Field

from app.storage.db import db_connection


class SectorSummary(BaseModel):
    """Summary of a single GICS sector in the universe."""

    sector: str = Field(description="The GICS sector name")
    ticker_count: int = Field(description="Number of tickers in the sector")
    sample_tickers: list[str] = Field(
        description="Up to 10 sample ticker symbols from the sector"
    )
    sample_companies: list[str] = Field(
        description="Up to 10 sample company names from the sector"
    )


def get_sector_summary(sector_name: str) -> SectorSummary:
    """Get a summary of a GICS sector: ticker count and sample companies.

    Use this to answer questions like:
    - "How many companies are in the Information Technology sector?"
    - "What companies are in the Health Care sector?"
    - "Show me some examples from Industrials."

    The sector_name must be a valid GICS sector name. Valid sectors:
    Information Technology, Health Care, Financials, Consumer Discretionary,
    Communication Services, Industrials, Consumer Staples, Energy,
    Utilities, Real Estate, Materials.

    Args:
        sector_name: The exact GICS sector name (case-sensitive)

    Returns:
        SectorSummary with ticker count and sample tickers/companies.
        Returns ticker_count=0 if the sector name is not found.
    """
    with db_connection() as conn:
        count_result = conn.execute(
            "SELECT COUNT(*) FROM universe WHERE sector = ?",
            [sector_name],
        ).fetchone()
        ticker_count = count_result[0] if count_result else 0

        sample_results = conn.execute(
            """
            SELECT ticker, company_name
            FROM universe
            WHERE sector = ?
            ORDER BY ticker
            LIMIT 10
            """,
            [sector_name],
        ).fetchall()

    return SectorSummary(
        sector=sector_name,
        ticker_count=ticker_count,
        sample_tickers=[row[0] for row in sample_results],
        sample_companies=[row[1] for row in sample_results],
    )


def list_sectors() -> list[str]:
    """Get the list of all valid GICS sector names in the universe.

    Use this when the user asks about sectors broadly, or when you need
    to know which sectors exist before querying for a specific one.

    Returns:
        Sorted list of unique sector names found in the universe.
    """
    with db_connection() as conn:
        results = conn.execute(
            """
            SELECT DISTINCT sector
            FROM universe
            WHERE sector IS NOT NULL
            ORDER BY sector
            """
        ).fetchall()
    return [row[0] for row in results]
