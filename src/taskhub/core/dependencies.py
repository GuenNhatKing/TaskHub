from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.services import UserService

from .session import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def get_user_services(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(db)
