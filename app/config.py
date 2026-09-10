"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str = "TaskFlow"
    database_path: str = "data/taskflow.db"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "TaskFlow"),
        database_path=os.getenv("DATABASE_PATH", "data/taskflow.db"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
