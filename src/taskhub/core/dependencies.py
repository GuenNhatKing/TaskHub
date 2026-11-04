from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.services import UserServices

from .session import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def get_user_services(db: Annotated[AsyncSession, Depends(get_db)]) -> UserServices:
    return UserServices(db)
