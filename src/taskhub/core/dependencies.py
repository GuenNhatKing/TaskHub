from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.services import AuthService, UserService

from .session import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(db)


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_services: Annotated[UserService, Depends(get_user_service)],
):
    return AuthService(db=db, user_service=user_services)
