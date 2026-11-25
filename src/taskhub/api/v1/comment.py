import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import CurrentUser, get_comment_service
from taskhub.core.messages import ErrorMessage
from taskhub.schemas.comment import CommentResponse, CommentUpdateRequest
from taskhub.services.comment_service import CommentService

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
    summary="Chỉnh sửa nội dung bình luận",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessage.PROJECT_ARCHIVED.value,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.COMMENT_EDIT_PERMISSION_DENIED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.COMMENT_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def update_comment(
    comment_id: uuid.UUID,
    current_user: CurrentUser,
    update_request: CommentUpdateRequest,
    services: Annotated[CommentService, Depends(get_comment_service)],
) -> CommentResponse:
    return await services.update_comment(comment_id, current_user, update_request)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa bình luận theo ID",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessage.PROJECT_ARCHIVED.value,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.COMMENT_DELETE_PERMISSION_DENIED.value,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessage.COMMENT_NOT_FOUND.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def delete_comment(
    comment_id: uuid.UUID,
    current_user: CurrentUser,
    services: Annotated[CommentService, Depends(get_comment_service)],
) -> None:
    await services.delete_comment(comment_id, current_user)
