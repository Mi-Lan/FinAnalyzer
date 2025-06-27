import asyncio
import json

import httpx
import redis.asyncio as redis

from .logging import get_logger
from .rate_limiter import RateLimiter

logger = get_logger(__name__)


class CachingTransport(httpx.AsyncBaseTransport):
    """
    An httpx transport that adds Redis caching to requests.
    """

    def __init__(self, transport: httpx.AsyncBaseTransport, redis_client: redis.Redis, ttl: int):
        self.transport = transport
        self.redis = redis_client
        self.ttl = ttl

    def _get_cache_key(self, request: httpx.Request) -> str:
        return f"fmp_cache:{request.method}:{str(request.url)}"

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if request.method not in ("GET",):
            return await self.transport.handle_async_request(request)

        cache_key = self._get_cache_key(request)
        
        # Try to get the cached response
        cached_response = await self.redis.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for {cache_key}")
            return httpx.Response(200, content=cached_response, request=request)

        logger.info(f"Cache miss for {cache_key}")
        
        # If not in cache, make the actual request
        response = await self.transport.handle_async_request(request)
        
        # Read the content to make it available for caching
        await response.aread()

        # Cache the new response if it was successful
        if 200 <= response.status_code < 300:
            try:
                await self.redis.set(cache_key, response.content, ex=self.ttl)
            except Exception as e:
                logger.warning(f"Redis cache write failed for key {cache_key}: {e}")

        return response


class RateLimitingTransport(httpx.AsyncBaseTransport):
    """
    An httpx transport that adds rate limiting to requests.
    """

    def __init__(self, transport: httpx.AsyncBaseTransport, rate_limiter: RateLimiter):
        self.transport = transport
        self.rate_limiter = rate_limiter

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """
        Handle the request, waiting for a rate limit token before proceeding.
        """
        while not await self.rate_limiter.acquire("fmp_api"):
            logger.info("Rate limit reached, waiting for token...")
            await asyncio.sleep(1)

        return await self.transport.handle_async_request(request) 