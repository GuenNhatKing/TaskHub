import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import CurrentUser, get_label_service
from taskhub.core.messages import ErrorMessage
from taskhub.schemas.label import LabelResponse, LabelUpdateRequest
from taskhub.services.label_service import LabelService

router = APIRouter(prefix="/labels", tags=["Labels"])


@router.patch(
    "/{label_id}",
    response_model=LabelResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin label",
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
            "description": ErrorMessage.LABEL_NOT_FOUND.value,
        },
        status.HTTP_409_CONFLICT: {
            "description": ErrorMessage.LABEL_EXISTED.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def update_label(
    label_id: uuid.UUID,
    current_user: CurrentUser,
    update_request: LabelUpdateRequest,
    services: Annotated[LabelService, Depends(get_label_service)],
) -> LabelResponse:
    return await services.update_label(label_id, current_user, update_request)


@router.delete(
    "/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa label theo ID",
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
            "description": ErrorMessage.LABEL_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def delete_label(
    label_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[LabelService, Depends(get_label_service)],
) -> None:
    await services.delete_label(label_id, current_user)
