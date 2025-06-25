from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Optional


class ProviderSettings(BaseModel):
    """Settings for a single data provider."""
    api_key: str
    rate_limit: int = 300
    requests_per_minute: int = 300


class DatabaseSettings(BaseModel):
    """Database connection settings."""
    url: str
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_pre_ping: bool = True
    pool_recycle: int = 3600  # 1 hour


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    data_providers: Dict[str, ProviderSettings] = {}
    database: Optional[DatabaseSettings] = None
    
    # Database URL from environment variable
    database_url: Optional[str] = None
    
    def get_database_url(self) -> str:
        """Get the database URL from configuration."""
        if self.database and self.database.url:
            return self.database.url
        elif self.database_url:
            return self.database_url
        else:
            raise ValueError("Database URL not configured. Set DATABASE_URL environment variable or database.url in config.")


settings = Settings() 