import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from taskhub.core.dependencies import get_db
from taskhub.main import app


@pytest_asyncio.fixture(scope="function")
async def api_client(db_session_factory):
    async def override_get_db():
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.pop(get_db, None)
