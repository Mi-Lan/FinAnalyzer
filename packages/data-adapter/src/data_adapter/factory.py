from typing import Dict, Tuple, Type, Optional

import httpx
import redis.asyncio as redis

from data_adapter.abc import BaseParser, DataSourceAdapter
from data_adapter.config import settings
from data_adapter.database import DatabaseManager
from data_adapter.exceptions import ConfigurationError
from data_adapter.providers.fmp.adapter import FMPAdapter
from data_adapter.providers.fmp.parser import FMPParser
from data_adapter.providers.fmp.storage_adapter import StorageEnabledFMPAdapter
from data_adapter.rate_limiter import RateLimiter
from data_adapter.transports import CachingTransport, RateLimitingTransport

# The registry now holds a tuple of the Adapter and its Parser
ADAPTER_REGISTRY: Dict[str, Tuple[Type[DataSourceAdapter], Type[BaseParser]]] = {
    "fmp": (FMPAdapter, FMPParser),
}

# Storage-enabled adapter registry
STORAGE_ADAPTER_REGISTRY: Dict[str, Tuple[Type[DataSourceAdapter], Type[BaseParser]]] = {
    "fmp": (StorageEnabledFMPAdapter, FMPParser),
}


def get_adapter(provider_name: str, enable_storage: bool = False) -> DataSourceAdapter:
    """
    Factory function to get a data source adapter instance.
    This function composes the httpx client with caching and rate limiting transports.
    
    Args:
        provider_name: Name of the data provider (e.g., 'fmp')
        enable_storage: Whether to create a storage-enabled adapter
    """
    if enable_storage:
        registry = STORAGE_ADAPTER_REGISTRY
    else:
        registry = ADAPTER_REGISTRY
        
    registry_entry = registry.get(provider_name)
    if not registry_entry:
        raise ConfigurationError(f"No adapter found for provider: {provider_name}")

    adapter_class, parser_class = registry_entry

    provider_settings = settings.data_providers.get(provider_name)
    if not provider_settings:
        raise ConfigurationError(f"No settings found for provider: {provider_name}")

    # 1. Create Redis client
    redis_client = redis.Redis(host="localhost", port=6379, db=0)

    # 2. Create caching transport (using our own class)
    cache_transport = CachingTransport(
        transport=httpx.AsyncHTTPTransport(),
        redis_client=redis_client,
        ttl=3600  # 1 hour TTL
    )

    # 3. Create rate limiting transport
    rate_limiter = RateLimiter(
        redis_client=redis_client,
        max_tokens=provider_settings.rate_limit,
        refill_interval=60,
        refill_amount=provider_settings.requests_per_minute,
    )
    
    rate_limiting_transport = RateLimitingTransport(
        transport=cache_transport, rate_limiter=rate_limiter
    )

    # 4. Create httpx client with composed transports
    client = httpx.AsyncClient(transport=rate_limiting_transport)

    # 5. Instantiate parser and adapter
    parser = parser_class()
    
    if enable_storage:
        # Create database manager for storage-enabled adapters
        database_url = settings.get_database_url()
        database_manager = DatabaseManager(database_url)
        return adapter_class(client, provider_settings, parser, database_manager)
    else:
        return adapter_class(client, provider_settings, parser)


def get_database_manager() -> DatabaseManager:
    """
    Factory function to get a database manager instance.
    """
    database_url = settings.get_database_url()
    return DatabaseManager(database_url) 