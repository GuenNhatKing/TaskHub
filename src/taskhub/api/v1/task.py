import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import CurrentUser, get_label_service, get_task_service
from taskhub.core.messages import ErrorMessage
from taskhub.schemas.label import LabelResponse, TaskLabelAssignRequest
from taskhub.schemas.task import (
    TaskAssignRequest,
    TaskResponse,
    TaskStatusUpdateRequest,
    TaskUpdateRequest,
)
from taskhub.services.label_service import LabelService
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


@router.get(
    "/{task_id}/labels",
    response_model=list[LabelResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách label đã gắn cho task",
)
async def get_task_labels(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[LabelService, Depends(get_label_service)],
) -> list[LabelResponse]:
    return await services.get_task_labels(task_id, current_user)


@router.post(
    "/{task_id}/labels",
    response_model=list[LabelResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Gắn label vào task",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": f"{ErrorMessage.PROJECT_ARCHIVED.value} / {ErrorMessage.LABEL_NOT_IN_PROJECT.value}",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_EDITOR_REQUIRED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": f"{ErrorMessage.TASK_NOT_FOUND.value} / {ErrorMessage.LABEL_NOT_FOUND.value}",
        },
        status.HTTP_409_CONFLICT: {
            "description": ErrorMessage.TASK_LABEL_ALREADY_EXISTS.value,
        },
    },
)
async def assign_label_to_task(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    assign_request: TaskLabelAssignRequest,
    services: Annotated[LabelService, Depends(get_label_service)],
) -> list[LabelResponse]:
    return await services.assign_label_to_task(
        task_id, assign_request.label_id, current_user
    )


@router.delete(
    "/{task_id}/labels/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Gỡ label khỏi task",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessage.PROJECT_ARCHIVED.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.WORKSPACE_EDITOR_REQUIRED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": f"{ErrorMessage.TASK_NOT_FOUND.value} / {ErrorMessage.TASK_LABEL_NOT_FOUND.value}",
        },
    },
)
async def remove_label_from_task(
    task_id: uuid.UUID,
    label_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[LabelService, Depends(get_label_service)],
) -> None:
    await services.remove_label_from_task(task_id, label_id, current_user)
