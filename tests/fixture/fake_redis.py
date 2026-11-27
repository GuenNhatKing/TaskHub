import pytest_asyncio
from fakeredis.aioredis import FakeRedis


@pytest_asyncio.fixture(scope="function")
async def fake_redis():
    redis = FakeRedis(decode_responses=True)
    yield redis
    await redis.flushall()
    await redis.aclose()
