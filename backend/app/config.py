"""Application configuration loaded from environment variables."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central config. Reads from .env in the project root."""

    anthropic_api_key: str = ""
    fmp_api_key: str = ""
    finnhub_api_key: str = ""

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    data_dir: Path = Path("./data")
    duckdb_path: Path = Path("./data/stockgpt.duckdb")

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
