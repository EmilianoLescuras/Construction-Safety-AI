"""Backend settings — read from environment / .env.

``DATABASE_URL`` defaults to a SQLite file in the project root so the API
runs without Docker. Override with a Postgres URL via ``.env`` when the
docker-compose Postgres service is up.
"""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = f"sqlite:///{PROJECT_ROOT / 'outputs' / 'construction_safety.db'}"
    api_title: str = "Construction Safety AI"
    api_version: str = "0.9.0"
    cors_origins: list[str] = ["*"]
    evidence_root: Path = PROJECT_ROOT / "outputs" / "images" / "evidence"


settings = Settings()
