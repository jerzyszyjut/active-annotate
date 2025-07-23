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
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    PROJECT_NAME: str = "Active Annotate API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Backend API for managing active learning annotation projects"
    BACKEND_CORS_ORIGINS: Optional[List[str]] = None


settings = Settings()
