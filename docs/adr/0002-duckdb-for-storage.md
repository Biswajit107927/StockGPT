# ADR 0002: DuckDB for analytical storage

## Status
Accepted

## Context
StockGPT needs to store and query daily prices, fundamentals, insider
transactions, and 13F filings. We considered Postgres, SQLite, DuckDB,
and a cloud warehouse like Snowflake or BigQuery.

## Decision
Use DuckDB embedded in the backend process, with the database file
stored locally at `data/stockgpt.duckdb`.

## Consequences
**Positive**
- No separate database server to run, configure, or pay for
- Columnar storage is 10-100x faster than Postgres for analytical
  queries (ranking, aggregations, screens) which is most of our workload
- Native Parquet support for cheap data-lake patterns later
- Pandas integration is first-class — query results land as DataFrames
- Single file is trivially backed up and shared

**Negative**
- Single-writer constraint: ingestion and serving must coordinate access
- Not a transactional OLTP store — fine for our read-heavy workload
- Less mature ecosystem than Postgres for ORMs and migrations
- Memory pressure on very large datasets, though our universe is <10K
  tickers and a few years of daily data fits comfortably

**Why not Postgres**
Great for OLTP but slow for the columnar scans this project needs.
Adding pg_analytics or Citus would be overkill for a personal project.

**Why not SQLite**
Row-oriented, slow for analytical queries, no native columnar formats.

**Why not Snowflake or BigQuery**
Cost and operational overhead for a learning project. Free tiers exist
but credit limits would become a distraction.

**Migration path**
If StockGPT grows to need multi-writer access or distributed scale, the
schemas and SQL transfer cleanly to Postgres (with some syntax tweaks)
or to a managed warehouse.
