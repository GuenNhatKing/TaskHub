from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import CurrentUser, get_user_service
from taskhub.core.messages import ErrorMessage
from taskhub.schemas.user import UserChangeProfileRequest, UserResponse
from taskhub.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin cá nhân người dùng hiện tại",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.INACTIVE_USER.value,
        },
    },
)
async def get_user_info(current_user: CurrentUser) -> UserResponse:
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin cá nhân người dùng hiện tại",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": (
                f"{ErrorMessage.REQUIRE_CURRENT_PASSWORD_TO_CHANGE_EMAIL.value} / "
                f"{ErrorMessage.INCORRECT_CURRENT_PASSWORD.value}"
            ),
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.INACTIVE_USER.value,
        },
        status.HTTP_409_CONFLICT: {
            "description": ErrorMessage.EMAIL_EXISTED.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def change_user_info(
    current_user: CurrentUser,
    change_profile_request: UserChangeProfileRequest,
    services: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    return await services.update_user(current_user, change_profile_request)
