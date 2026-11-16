import pytest_asyncio


@pytest_asyncio.fixture(scope="function")
async def db_session(db_session_factory):
    async with db_session_factory() as session:
        yield session

        await session.rollback()
