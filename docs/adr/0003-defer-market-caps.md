# ADR 0003: Defer market cap data to a paid free-tier source

## Status
Accepted

## Context
The universe ingestion pipeline needs market cap data for ranking and
filtering (e.g., "top 100 by market cap"). yfinance was the V1 default
because it requires no API key. In practice yfinance hits Yahoo's
unauthenticated rate limit (HTTP 429) within ~10-20 requests, making
it unusable for loading all 503 S&P 500 tickers in a single pass.

## Decision
Skip market cap enrichment in the V1 universe ingestion. Tickers,
company names, and GICS sector data load reliably from Wikipedia
without authentication or rate limits. Market caps will be backfilled
via Financial Modeling Prep (free tier, 250 calls/day, sufficient for
daily refresh of S&P 500) when we add fundamental data in Week 3.

## Consequences
**Positive**
- Universe ingestion is fast (~2 seconds) and reliable
- No dependency on a flaky upstream source for V1
- Forces us to confront API key management earlier rather than later

**Negative**
- Ranking tools that need market cap (e.g., "top 100 by size") cannot
  function until Week 3
- The `market_cap` column is null for all rows initially

**Why not switch ingestion to FMP entirely**
FMP's free-tier sector and constituent endpoints are paywalled.
Wikipedia is the most reliable free source for the constituent list
itself. FMP is best used for per-ticker fundamental enrichment.

**Why not paid Yahoo via yfinance-with-key**
No supported path; Yahoo has actively deprecated unauthenticated
access since 2024.