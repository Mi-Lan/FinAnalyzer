import time
from typing import Optional

import redis.asyncio as redis


class RateLimiter:
    """
    A token bucket rate limiter implemented with Redis.
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        max_tokens: int,
        refill_interval: float,
        refill_amount: int,
    ):
        self.redis = redis_client
        self.max_tokens = max_tokens
        self.refill_interval = refill_interval
        self.refill_amount = refill_amount

    async def _get_current_tokens(self, key: str) -> float:
        """Get the current number of tokens in the bucket."""
        tokens = await self.redis.get(f"{key}:tokens")
        if tokens is None:
            await self.redis.set(f"{key}:tokens", self.max_tokens)
            return float(self.max_tokens)
        return float(tokens)

    async def _get_last_refill(self, key: str) -> float:
        """Get the timestamp of the last refill."""
        last_refill = await self.redis.get(f"{key}:last_refill")
        if last_refill is None:
            now = time.time()
            await self.redis.set(f"{key}:last_refill", now)
            return now
        return float(last_refill)

    async def _refill_tokens(self, key: str):
        """Refill the token bucket if necessary."""
        now = time.time()
        last_refill = await self._get_last_refill(key)
        time_since_refill = now - last_refill

        if time_since_refill > self.refill_interval:
            tokens_to_add = (
                (time_since_refill // self.refill_interval) * self.refill_amount
            )
            current_tokens = await self._get_current_tokens(key)
            new_tokens = min(current_tokens + tokens_to_add, self.max_tokens)
            
            pipe = self.redis.pipeline()
            pipe.set(f"{key}:tokens", new_tokens)
            pipe.set(f"{key}:last_refill", now)
            await pipe.execute()


    async def acquire(self, key: str, cost: int = 1) -> bool:
        """Acquire a token from the bucket."""
        await self._refill_tokens(key)

        current_tokens = await self._get_current_tokens(key)
        if current_tokens >= cost:
            await self.redis.decrby(f"{key}:tokens", cost)
            return True
        return False 