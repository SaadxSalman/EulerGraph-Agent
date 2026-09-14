from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EulerGraph-Agent"
    environment: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "claude-3-5-sonnet-latest"
    data_dir: Path = Path("data")
    max_retrieval_results: int = 6
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
