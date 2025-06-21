from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Optional


class ProviderSettings(BaseModel):
    """Settings for a single data provider."""
    api_key: str
    rate_limit: int = 300
    requests_per_minute: int = 300


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    data_providers: Dict[str, ProviderSettings] = {}


settings = Settings() 