import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from taskhub.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from taskhub.core.dependencies import (
    CurrentUser,
    get_label_service,
    get_project_service,
    get_task_service,
)
from taskhub.core.enums import Priority, TaskStatus
from taskhub.core.messages import ErrorMessage
from taskhub.schemas.label import LabelCreateRequest, LabelResponse
from taskhub.schemas.project import ProjectResponse, ProjectUpdateRequest
from taskhub.schemas.task import TaskCreateRequest, TaskListResponse, TaskResponse
from taskhub.services.label_service import LabelService
from taskhub.services.project_service import ProjectService
from taskhub.services.task_service import TaskService

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
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
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
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
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
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
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
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
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
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
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


@router.post(
    "/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo task mới trong project",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": f"{ErrorMessage.PROJECT_ARCHIVED.value} / {ErrorMessage.ASSIGNEE_NOT_IN_WORKSPACE.value}",
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
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def create_project_task(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    create_request: TaskCreateRequest,
    services: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    return await services.create_task(project_id, current_user, create_request)


@router.get(
    "/{project_id}/tasks",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách task trong project",
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
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def get_project_tasks(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[TaskService, Depends(get_task_service)],
    status: TaskStatus | None = None,
    priority: Priority | None = None,
    assignee_id: uuid.UUID | None = None,
    search: str | None = None,  # Tìm kiếm gần đúng như là theo title
    page: Annotated[int, Query(ge=DEFAULT_PAGE)] = DEFAULT_PAGE,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
):
    return await services.get_project_tasks(
        project_id=project_id,
        current_user=current_user,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/{project_id}/labels",
    response_model=LabelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo label mới trong project",
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
        status.HTTP_409_CONFLICT: {
            "description": ErrorMessage.LABEL_EXISTED.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def create_project_label(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    create_request: LabelCreateRequest,
    services: Annotated[LabelService, Depends(get_label_service)],
) -> LabelResponse:
    return await services.create_label(project_id, current_user, create_request)


@router.get(
    "/{project_id}/labels",
    response_model=list[LabelResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách label trong project",
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
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def get_project_labels(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[LabelService, Depends(get_label_service)],
) -> list[LabelResponse]:
    return await services.get_project_labels(project_id, current_user)
