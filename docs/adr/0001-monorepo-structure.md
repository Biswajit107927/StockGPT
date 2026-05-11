# ADR 0001: Monorepo structure

## Status
Accepted

## Context
StockGPT has a Python backend (FastAPI + DuckDB + agent logic) and a React
frontend. We needed to decide between a monorepo and two separate repos.

## Decision
Use a single monorepo with `backend/` and `frontend/` as siblings.

## Consequences
**Positive**
- Single source of truth, single PR for cross-cutting changes
- Simpler CI setup for a personal project
- Easier onboarding for anyone reading the project

**Negative**
- Cannot independently version frontend and backend
- Single repo size grows over time

**Why not separate repos**
For a personal project this size, separate repos add coordination overhead
without benefit. If StockGPT ever needs independent deployment cadence
for frontend and backend, we can split later — git history is preserved
via `git filter-repo`.
