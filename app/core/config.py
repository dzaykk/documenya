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
    DATABASE_URL: str = Field(...)

    # Authentication
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Storage
    UPLOAD_DIR: str = Field(...)
    MAX_FILE_SIZE: int = Field(...)

    # CORS
    CORS_ORIGINS: list[str] = Field(...)

    # Redis
    REDIS_URL: str = Field(...)
    REDIS_DB_CACHE: int = 0
    REDIS_DB_MEMORY: int = 1

    # Celery
    CELERY_BROKER_URL: str = Field(...)
    CELERY_RESULT_BACKEND: str = Field(...)

    # Embeddings
    DEFAULT_EMBEDDING_PROVIDER: str = "huggingface"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIMENSION: int = 1024
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DEVICE: str = "auto"
    EMBEDDING_TIMEOUT: int = 60

    # LLM
    DEFAULT_LLM_PROVIDER: str = Field(...)

    # OpenRouter
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_BASE_URL: str = Field(...)
    OPENROUTER_MODEL: str = Field(...)
    OPENROUTER_MAX_RETRIES: int = 3

    # Ollama
    OLLAMA_URL: str = Field(...)
    OLLAMA_MODEL: str = Field(...)

    # Generation

    LLM_TIMEOUT: int = 120
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_DELAY: float = 2.0

    DEFAULT_TEMPERATURE: float = 0.1
    DEFAULT_TOP_P: float = 0.95
    DEFAULT_MAX_TOKENS: int = 1024

    DEFAULT_FREQUENCY_PENALTY: float = 0.0
    DEFAULT_PRESENCE_PENALTY: float = 0.0

    # Qdrant
    QDRANT_URL: str = Field(...)
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = Field(...)
    QDRANT_VECTOR_SIZE: int = 1024
    QDRANT_TIMEOUT: int = 30

    # Retrieval
    TOP_K: int = Field(...)
    SIMILARITY_THRESHOLD: float = Field(...)
    MAX_CONTEXT_TOKENS: int = Field(...)

    # HTTP
    REQUEST_TIMEOUT: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()