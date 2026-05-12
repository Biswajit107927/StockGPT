
"""Universe API: query the ticker universe."""
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.storage.db import db_connection


router = APIRouter(prefix="/universe", tags=["universe"])


class UniverseRow(BaseModel):
    ticker: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None
    index_membership: Optional[str] = None


class UniverseResponse(BaseModel):
    count: int
    rows: list[UniverseRow]


@router.get("", response_model=UniverseResponse)
async def list_universe(
    sector: Optional[str] = Query(None, description="Filter by GICS sector"),
    limit: int = Query(50, ge=1, le=1000, description="Max rows to return"),
    min_market_cap: Optional[int] = Query(None, description="Minimum market cap in USD"),
) -> UniverseResponse:
    """List tickers in the universe with optional filters."""
    where_clauses = ["1=1"]
    params: list = []

    if sector:
        where_clauses.append("sector = ?")
        params.append(sector)

    if min_market_cap is not None:
        where_clauses.append("market_cap >= ?")
        params.append(min_market_cap)

    where_sql = " AND ".join(where_clauses)
    query = f"""
        SELECT ticker, company_name, sector, industry, market_cap, index_membership
        FROM universe
        WHERE {where_sql}
        ORDER BY market_cap DESC NULLS LAST
        LIMIT ?
    """
    params.append(limit)

    with db_connection() as conn:
        results = conn.execute(query, params).fetchall()

    rows = [
        UniverseRow(
            ticker=r[0],
            company_name=r[1],
            sector=r[2],
            industry=r[3],
            market_cap=r[4],
            index_membership=r[5],
        )
        for r in results
    ]
    return UniverseResponse(count=len(rows), rows=rows)


@router.get("/sectors")
async def list_sectors() -> dict:
    """List all distinct sectors with ticker counts."""
    with db_connection() as conn:
        results = conn.execute("""
            SELECT sector, COUNT(*) AS ticker_count
            FROM universe
            WHERE sector IS NOT NULL
            GROUP BY sector
            ORDER BY ticker_count DESC
        """).fetchall()
    return {"sectors": [{"sector": r[0], "count": r[1]} for r in results]}
