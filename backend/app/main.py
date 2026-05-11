"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.storage.db import init_schema, db_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_schema()
    print(f"Database ready at {settings.duckdb_path}")
    yield


app = FastAPI(
    title="StockGPT API",
    description="Agentic AI for stock market research",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    """Liveness check. Confirms server and database are reachable."""
    try:
        with db_connection() as conn:
            result = conn.execute("SELECT 1 AS ok").fetchone()
            db_ok = result is not None and result[0] == 1
        return {
            "status": "ok" if db_ok else "degraded",
            "database": "ok" if db_ok else "unreachable",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "0.1.0",
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "unreachable",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


@app.get("/")
async def root() -> dict:
    return {
        "name": "StockGPT API",
        "version": "0.1.0",
        "docs": "/docs",
    }
