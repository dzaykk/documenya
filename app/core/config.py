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
    CORS_ORIGINS: list[str] = Field(
        default=["*"],
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()