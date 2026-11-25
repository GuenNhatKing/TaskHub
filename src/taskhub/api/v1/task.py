import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import CurrentUser, get_task_service
from taskhub.core.messages import ErrorMessage
from taskhub.schemas.task import (
    TaskAssignRequest,
    TaskResponse,
    TaskStatusUpdateRequest,
    TaskUpdateRequest,
)
from taskhub.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin chi tiết task theo ID",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_MEMBER_NOT_FOUND.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.TASK_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def get_task(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    return await services.get_task_detail(task_id, current_user)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin task (title, description, assignee, status, priority, due_date)",
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
            "description": ErrorMessage.TASK_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def update_task(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    update_request: TaskUpdateRequest,
    services: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    return await services.update_task(task_id, current_user, update_request)


@router.patch(
    "/{task_id}/assign",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Giao hoặc gỡ người thực hiện task",
)
async def assign_task(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    assign_request: TaskAssignRequest,
    services: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    return await services.update_task(
        task_id,
        current_user,
        TaskUpdateRequest(assignee_id=assign_request.assignee_id),
    )


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Chuyển trạng thái (status) của task",
)
async def update_task_status(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    status_request: TaskStatusUpdateRequest,
    services: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    return await services.update_task(
        task_id,
        current_user,
        TaskUpdateRequest(status=status_request.status),
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa task theo ID",
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
            "description": ErrorMessage.TASK_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def delete_task(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[TaskService, Depends(get_task_service)],
) -> None:
    await services.delete_task(task_id, current_user)
