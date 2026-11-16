import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker


@pytest_asyncio.fixture(scope="function")
async def db_session_factory(db_engine):
    return async_sessionmaker(bind=db_engine)
