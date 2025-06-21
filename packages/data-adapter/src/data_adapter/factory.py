from typing import Dict, Tuple, Type

import httpx
import redis.asyncio as redis

from data_adapter.abc import BaseParser, DataSourceAdapter
from data_adapter.config import settings
from data_adapter.exceptions import ConfigurationError
from data_adapter.providers.fmp.adapter import FMPAdapter
from data_adapter.providers.fmp.parser import FMPParser
from data_adapter.rate_limiter import RateLimiter
from data_adapter.transports import CachingTransport, RateLimitingTransport

# The registry now holds a tuple of the Adapter and its Parser
ADAPTER_REGISTRY: Dict[str, Tuple[Type[DataSourceAdapter], Type[BaseParser]]] = {
    "fmp": (FMPAdapter, FMPParser),
}


def get_adapter(provider_name: str) -> DataSourceAdapter:
    """
    Factory function to get a data source adapter instance.
    This function composes the httpx client with caching and rate limiting transports.
    """
    registry_entry = ADAPTER_REGISTRY.get(provider_name)
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
    return adapter_class(client, provider_settings, parser) 