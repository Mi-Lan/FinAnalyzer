from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Optional


class ProviderSettings(BaseModel):
    """Settings for a single data provider."""
    api_key: str
    rate_limit: int = 300
    requests_per_minute: int = 300
    max_data_points: int = 1500  # Maximum number of data records to fetch per operation


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
    )

    data_providers: Dict[str, ProviderSettings] = {}
    database: Optional[DatabaseSettings] = None
    
    # Support flat FMP_API_KEY from environment
    fmp_api_key: Optional[str] = Field(None, alias='FMP_API_KEY')
    
    # Database URL from environment variable
    database_url: Optional[str] = None
    
    def __init__(self, **values):
        super().__init__(**values)
        # Manually populate fmp provider settings if fmp_api_key is present
        if self.fmp_api_key and 'fmp' not in self.data_providers:
            self.data_providers['fmp'] = ProviderSettings(api_key=self.fmp_api_key)

    def get_database_url(self) -> str:
        """Get the database URL from configuration."""
        if self.database and self.database.url:
            return self.database.url
        elif self.database_url:
            return self.database_url
        else:
            raise ValueError("Database URL not configured. Set DATABASE_URL environment variable or database.url in config.")


settings = Settings() 