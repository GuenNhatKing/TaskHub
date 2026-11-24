import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import (
    CurrentUser,
    get_project_service,
)
from taskhub.core.messages import ErrorMessage
from taskhub.schemas.project import ProjectResponse, ProjectUpdateRequest
from taskhub.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin chi tiết project theo ID",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_MEMBER_NOT_FOUND.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.PROJECT_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def get_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    return await services.get_project_detail(project_id, current_user)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin project",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessage.PROJECT_ARCHIVED.value,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_EDITOR_REQUIRED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.PROJECT_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def update_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    update_request: ProjectUpdateRequest,
    services: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    return await services.update_project(project_id, current_user, update_request)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa project theo ID",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_EDITOR_REQUIRED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.PROJECT_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def delete_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[ProjectService, Depends(get_project_service)],
) -> None:
    return await services.delete_project(project_id, current_user)


@router.post(
    "/{project_id}/archive",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Lưu trữ (archive) project",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_EDITOR_REQUIRED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.PROJECT_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def archive_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    return await services.archive_project(project_id, current_user)


@router.post(
    "/{project_id}/unarchive",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Bỏ lưu trữ (unarchive) project",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_EDITOR_REQUIRED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.PROJECT_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def unarchive_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    return await services.unarchive_project(project_id, current_user)
