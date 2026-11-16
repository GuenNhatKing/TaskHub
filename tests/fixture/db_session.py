import pytest_asyncio

from taskhub.models.base import Base


@pytest_asyncio.fixture(scope="function")
async def db_session(db_session_factory):
    async with db_session_factory() as session:
        yield session

        await session.rollback()

        # Xóa dữ liệu đã commit tránh bị trùng lại
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
