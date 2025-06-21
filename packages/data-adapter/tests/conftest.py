import pytest
import redis.asyncio as redis


@pytest.fixture
async def redis_client():
    """
    Fixture to provide a mock Redis client.
    In a real scenario, this could be fakeredis or a connection to a test Redis instance.
    For now, we'll mock the methods we need.
    """
    # This is a simple mock. For real tests, consider using fakeredis.
    class MockRedis:
        def __init__(self):
            self._data = {}

        async def get(self, key):
            return self._data.get(key)

        async def set(self, key, value, ex=None):
            self._data[key] = value
            return True

        async def decrby(self, key, amount):
            current = int(self._data.get(key, 0))
            self._data[key] = str(current - amount)
            return current - amount
        
        def pipeline(self):
            return self

        async def execute(self):
            return []


    client = MockRedis()
    yield client 