import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.core.security import decode_access_token
from taskhub.exceptions.auth_ex import InvalidTokenException
from taskhub.exceptions.not_found_ex import NotFoundException
from taskhub.models.user import User
from taskhub.services import AuthService, UserService
from taskhub.services.project_service import ProjectService
from taskhub.services.task_service import TaskService
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
):
    return AuthService(db=db)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_services: Annotated[UserService, Depends(get_user_service)],
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = uuid.UUID(payload["sub"])

    try:
        user = await user_services.get_user(user_id)
    except NotFoundException as exc:
        # Bắt NotFoundException → đổi thành InvalidTokenException (401).
        # User bị khóa → giữ nguyên InactiveUserException (403).
        raise InvalidTokenException() from exc

    if payload["tv"] != user.token_version:
        raise InvalidTokenException()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_workspace_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_services: Annotated[UserService, Depends(get_user_service)],
):
    return WorkspaceService(db=db, user_service=user_services)


def get_project_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    return ProjectService(db=db, workspace_service=workspace_service)


def get_task_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> TaskService:
    return TaskService(
        db=db,
        project_service=project_service,
        workspace_service=workspace_service,
    )
