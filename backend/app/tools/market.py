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


# ============================================================================
# Day 4: Additional tools — search, details, comparison
# ============================================================================


class CompanyMatch(BaseModel):
    """A single ticker match from a name search."""

    ticker: str = Field(description="Ticker symbol")
    company_name: str = Field(description="Full company name")
    sector: Optional[str] = Field(default=None, description="GICS sector")


class CompanySearchResults(BaseModel):
    """Results of searching the universe by company name fragment."""

    query: str = Field(description="The search term used")
    match_count: int = Field(description="Number of matches found")
    matches: list[CompanyMatch] = Field(description="Matching companies")


def search_companies_by_name(name_fragment: str, limit: int = 20) -> CompanySearchResults:
    """Search the S&P 500 universe for companies whose names contain the given fragment.

    Use this to answer questions like:
    - "Find companies with 'energy' in their name."
    - "Which companies have 'bank' in the name?"
    - "Show me ticker symbols for companies named like 'Apple'."

    The search is case-insensitive substring matching against the full company name.
    Returns up to `limit` matches (default 20), sorted alphabetically by ticker.

    Args:
        name_fragment: Substring to search for in company names
        limit: Maximum number of results to return (default 20, max 100)

    Returns:
        CompanySearchResults with the query, match count, and list of matches.
        Returns match_count=0 if no companies match.
    """
    # Clamp limit to a reasonable max to prevent runaway queries
    limit = max(1, min(limit, 100))

    with db_connection() as conn:
        results = conn.execute(
            """
            SELECT ticker, company_name, sector
            FROM universe
            WHERE LOWER(company_name) LIKE LOWER(?)
            ORDER BY ticker
            LIMIT ?
            """,
            [f"%{name_fragment}%", limit],
        ).fetchall()

    matches = [
        CompanyMatch(ticker=r[0], company_name=r[1], sector=r[2])
        for r in results
    ]
    return CompanySearchResults(
        query=name_fragment,
        match_count=len(matches),
        matches=matches,
    )


class TickerDetails(BaseModel):
    """Detailed info for a single ticker."""

    ticker: str = Field(description="Ticker symbol")
    found: bool = Field(description="Whether the ticker exists in the universe")
    company_name: str = Field(default="", description="Full company name")
    sector: Optional[str] = Field(default=None, description="GICS sector")
    industry: Optional[str] = Field(default=None, description="GICS sub-industry")
    exchange: Optional[str] = Field(default=None, description="Exchange")
    index_membership: Optional[str] = Field(default=None, description="Index this ticker belongs to")


def get_ticker_details(ticker: str) -> TickerDetails:
    """Look up full details for a specific ticker symbol.

    Use this to answer questions like:
    - "Tell me about AAPL."
    - "What sector is NVDA in?"
    - "What does JPM stand for?"

    The lookup is case-insensitive — both 'aapl' and 'AAPL' will find Apple Inc.

    Args:
        ticker: The ticker symbol to look up (e.g., 'AAPL', 'NVDA', 'JPM')

    Returns:
        TickerDetails with the company info. If the ticker is not in the
        universe, returns TickerDetails with found=False and empty fields.
        Do not raise — gracefully indicate not-found via the found flag.
    """
    with db_connection() as conn:
        result = conn.execute(
            """
            SELECT ticker, company_name, sector, industry, exchange, index_membership
            FROM universe
            WHERE UPPER(ticker) = UPPER(?)
            """,
            [ticker],
        ).fetchone()

    if result is None:
        return TickerDetails(ticker=ticker.upper(), found=False)

    return TickerDetails(
        ticker=result[0],
        found=True,
        company_name=result[1],
        sector=result[2],
        industry=result[3],
        exchange=result[4],
        index_membership=result[5],
    )


class SectorCount(BaseModel):
    """Ticker count for a single sector."""

    sector: str
    ticker_count: int


class SectorComparison(BaseModel):
    """Side-by-side ticker counts for multiple sectors."""

    comparisons: list[SectorCount] = Field(description="Counts for each requested sector")
    not_found: list[str] = Field(
        default_factory=list,
        description="Sector names that don't exist in the universe (for agent error recovery)",
    )


def compare_sectors(sector_names: list[str]) -> SectorComparison:
    """Compare ticker counts across multiple GICS sectors side by side.

    Use this to answer questions like:
    - "Which sector has more companies — Technology or Healthcare?"
    - "Compare the size of Energy, Materials, and Utilities."
    - "How does Financials compare to Industrials?"

    Sector names must be exact GICS sector names (case-sensitive). Valid sectors:
    Information Technology, Health Care, Financials, Consumer Discretionary,
    Communication Services, Industrials, Consumer Staples, Energy,
    Utilities, Real Estate, Materials.

    Args:
        sector_names: List of GICS sector names to compare. Must have at least 2.

    Returns:
        SectorComparison with ticker counts for each requested sector that exists.
        Sectors not found in the universe are listed in the `not_found` field so
        the agent can recover (e.g., try list_sectors to find correct names).
    """
    if len(sector_names) < 1:
        return SectorComparison(comparisons=[], not_found=[])

    # Build dynamic IN clause with proper placeholders
    placeholders = ", ".join(["?"] * len(sector_names))

    with db_connection() as conn:
        results = conn.execute(
            f"""
            SELECT sector, COUNT(*) AS ticker_count
            FROM universe
            WHERE sector IN ({placeholders})
            GROUP BY sector
            ORDER BY ticker_count DESC
            """,
            sector_names,
        ).fetchall()

    found_sectors = {row[0] for row in results}
    not_found = [s for s in sector_names if s not in found_sectors]

    return SectorComparison(
        comparisons=[SectorCount(sector=r[0], ticker_count=r[1]) for r in results],
        not_found=not_found,
    )
