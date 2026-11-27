import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from taskhub.core.dependencies import get_db
from taskhub.core.redis import get_redis
from taskhub.main import app


@pytest_asyncio.fixture(scope="function")
async def api_client(db_session_factory, fake_redis):
    async def override_get_db():
        async with db_session_factory() as session:
            yield session

    async def override_get_redis():
        return fake_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_redis, None)
