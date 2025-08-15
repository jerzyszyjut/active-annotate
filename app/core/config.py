from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings and configuration.

    This class manages all configuration settings for the Active Annotate API.
    Settings are loaded from environment variables and have sensible defaults.

    Attributes:
        PROJECT_NAME (str): The name of the project/API.
        VERSION (str): The current version of the API.
        DESCRIPTION (str): A description of what the API does.
        BACKEND_CORS_ORIGINS (Optional[List[str]]): List of allowed CORS origins.
            If None, CORS middleware is not added.
        POSTGRES_SERVER (str): PostgreSQL server hostname.
        POSTGRES_USER (str): PostgreSQL username.
        POSTGRES_PASSWORD (str): PostgreSQL password.
        POSTGRES_DB (str): PostgreSQL database name.
        POSTGRES_PORT (int): PostgreSQL server port.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "Active Annotate API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Backend API for managing active learning annotation projects"
    BACKEND_CORS_ORIGINS: Optional[List[str]] = None

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "active_annotate"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
