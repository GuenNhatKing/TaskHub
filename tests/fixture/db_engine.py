import pytest_asyncio
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine

from taskhub.models.base import Base


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",  # Sử dụng SQLite trên RAM dùng aiosqlite
        connect_args={"check_same_thread": False},  # Tắt kiểm tra trùng luồng
        poolclass=StaticPool,
        echo=False,
    )

    # Tạo tất cả các bảng
    async with engine.begin() as db:
        await db.run_sync(Base.metadata.create_all)

    yield engine

    # Xóa tất cả bảng
    async with engine.begin() as db:
        await db.run_sync(Base.metadata.drop_all)
    await engine.dispose()
