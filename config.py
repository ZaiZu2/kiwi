import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.resolve() / '.env', env_file_encoding='utf-8'
    )

    DATABASE_URI: str = "sqlite+aiosqlite:///internal.db"
    ENVIRONMENT: Literal['development', 'production'] = 'production'


@lru_cache
def get_config() -> Config:
    return Config()  # type: ignore


with open(Path(__file__).parent / 'logging_config.json') as f:
    LOGGING_CONFIG = json.load(f)
