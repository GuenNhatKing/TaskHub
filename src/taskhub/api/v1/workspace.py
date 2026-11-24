import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from taskhub.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from taskhub.core.dependencies import (
    CurrentUser,
    get_project_service,
    get_workspace_service,
)
from taskhub.core.enums import ProjectStatus
from taskhub.core.messages import ErrorMessage
from taskhub.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
)
from taskhub.schemas.workspace import (
    WorkspaceAddMemberRequest,
    WorkspaceCreateRequest,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)
from taskhub.services.project_service import ProjectService
from taskhub.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo workspace mới",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.INACTIVE_USER.value,
        },
        status.HTTP_409_CONFLICT: {
            "description": ErrorMessage.WORKSPACE_EXISTED.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def create_workspace(
    current_user: CurrentUser,
    create_workspace_request: WorkspaceCreateRequest,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> WorkspaceResponse:
    return await services.create_new_workspace(current_user, create_workspace_request)


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin chi tiết workspace theo ID",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.WORKSPACE_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def get_workspace_by_id(
    current_user: CurrentUser,
    workspace_id: uuid.UUID,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> WorkspaceResponse:
    return await services.get_workspace(workspace_id, current_user)


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin workspace",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_OWNER_REQUIRED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.WORKSPACE_NOT_FOUND.value,
        },
        status.HTTP_409_CONFLICT: {
            "description": ErrorMessage.WORKSPACE_EXISTED.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def update_workspace(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    update_workspace_request: WorkspaceUpdateRequest,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> WorkspaceResponse:
    return await services.update_workspace(
        workspace_id, current_user, update_workspace_request
    )


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa workspace theo ID",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_OWNER_REQUIRED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.WORKSPACE_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def delete_workspace_by_id(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> None:
    return await services.delete_workspace(workspace_id, current_user)


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên vào workspace",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessage.CANNOT_ASSIGN_OWNER_ROLE.value,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_OWNER_REQUIRED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": f"{ErrorMessage.WORKSPACE_NOT_FOUND.value} / {ErrorMessage.USER_NOT_FOUND.value}",
        },
        status.HTTP_409_CONFLICT: {
            "description": ErrorMessage.MEMBER_ALREADY_EXISTS.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def add_workspace_member(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    add_member_request: WorkspaceAddMemberRequest,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> WorkspaceMemberResponse:
    return await services.add_workspace_member(
        workspace_id, current_user, add_member_request
    )


@router.delete(
    "/{workspace_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa thành viên khỏi workspace",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_OWNER_REQUIRED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": f"{ErrorMessage.WORKSPACE_NOT_FOUND.value} / {ErrorMessage.WORKSPACE_MEMBER_NOT_FOUND.value}",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def remove_workspace_member(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> None:
    await services.remove_workspace_member(workspace_id, user_id, current_user)


@router.post(
    "/{workspace_id}/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo project mới trong workspace",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_EDITOR_REQUIRED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.WORKSPACE_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def create_workspace_project(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    create_project_request: ProjectCreateRequest,
    services: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    return await services.create_project(
        workspace_id, current_user, create_project_request
    )


@router.get(
    "/{workspace_id}/projects",
    response_model=list[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách project trong workspace",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_PERMISSION_DENIED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.WORKSPACE_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
@router.get(
    "/{workspace_id}/projects",
    response_model=ProjectListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_projects(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[ProjectService, Depends(get_project_service)],
    status: ProjectStatus | None = None,
    page: Annotated[int, Query(ge=DEFAULT_PAGE)] = DEFAULT_PAGE,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
):
    return await services.get_workspace_projects(
        workspace_id=workspace_id,
        current_user=current_user,
        status=status,
        page=page,
        page_size=page_size,
    )
