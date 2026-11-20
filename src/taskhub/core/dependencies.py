import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.core.security import decode_access_token
from taskhub.exceptions.auth_ex import InactiveUserException, InvalidTokenException
from taskhub.models.user import User
from taskhub.services import AuthService, UserService
from taskhub.services.workspace_service import WorkspaceService

from .session import AsyncSessionLocal

security = HTTPBearer()


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


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_services: Annotated[UserService, Depends(get_user_service)],
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = uuid.UUID(payload["sub"])
    user = await user_services.user_repository.get_by_id(user_id)

    if not user:
        raise InvalidTokenException()

    if not user.is_active:
        raise InactiveUserException()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_workspace_service(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return WorkspaceService(db=db)
