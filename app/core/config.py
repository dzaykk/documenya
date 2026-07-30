from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Documenya"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # API
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Storage
    UPLOAD_DIR: str = "app/storage/uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # CELERY
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Embeddings
    DEFAULT_EMBEDDING_PROVIDER: str = "fastembed"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DIMENSION: int = 1024
    EMBEDDING_TIMEOUT: int = 60

    # LLM
    DEFAULT_LLM_PROVIDER: str = "openrouter"
    OPENAI_API_KEY: str | None = None
    OPENROUTER_API_KEY: str | None = None
    COHERE_API_KEY: str | None = None
    LLM_TIMEOUT: int = 120

    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "documents"
    QDRANT_TIMEOUT: int = 30
    VECTOR_SEARCH_TIMEOUT: int = 15

    # Redis Memory
    REDIS_URL: str = "redis://localhost:6379/1"

    # Retrieval
    TOP_K: int = 10
    MAX_CONTEXT_TOKENS: int = 8000
    SIMILARITY_THRESHOLD: float = 0.35

    # Networking
    REQUEST_TIMEOUT: int = 60
    RETRY_ATTEMPTS: int = 3
    RETRY_BACKOFF: float = 2.0

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()