from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """Centralized Application Configuration managed via environment variables."""
    PROJECT_NAME: str = "Tool Permission Enforcer Proxy"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # SQLite Database Connection URL
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # CORS Origins allowed to talk to the backend
    ALLOWED_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

# Instantiated settings object to be imported across the application
settings = Settings()
