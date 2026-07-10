from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Document Q&A RAG Assistant"
    APP_VERSION: str = "0.0.0"
    DEBUG: bool = False

    # API
    API_PREFIX: str = "/api"

    # LLM - Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"

    # Embedding
    EMBEDDING_PROVIDER: str = "bge-m3"  # "bge-m3" | "gemini"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # SQLite
    DATABASE_URL: str = "sqlite:///./app_data.db"

    # RAG Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5
    RELEVANCE_THRESHOLD: float = 0.3

    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding='utf-8',
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
