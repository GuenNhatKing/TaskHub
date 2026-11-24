from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import CurrentUser, get_auth_service, get_user_service
from taskhub.core.messages import ErrorMessage
from taskhub.schemas.token import LogoutRequest, RefreshTokenRequest, TokenResponse
from taskhub.schemas.user import (
    ChangePasswordRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from taskhub.services.auth_service import AuthService
from taskhub.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản người dùng mới",
    responses={
        status.HTTP_409_CONFLICT: {
            "description": ErrorMessage.EMAIL_EXISTED.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def create_user(
    data: UserRegisterRequest,
    services: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    return await services.create_user(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập vào hệ thống",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.INACTIVE_USER.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def login(
    data: UserLoginRequest,
    services: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await services.authenticate_user(data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Làm mới access token từ refresh token",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_REFRESH_TOKEN.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.INACTIVE_USER.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def refresh(
    refresh_request: RefreshTokenRequest,
    services: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await services.refresh_tokens(refresh_request)


@router.post(
    "/logout",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Đăng xuất và thu hồi refresh token",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_REFRESH_TOKEN.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def logout(
    logout_request: LogoutRequest,
    services: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    await services.logout(logout_request)


@router.post(
    "/change-password",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Đổi mật khẩu người dùng hiện tại",
    description=(
        "Đổi mật khẩu của người dùng hiện tại. "
        "Lưu ý: Toàn bộ access token và refresh token hiện tại sẽ bị vô hiệu hóa ngay lập tức. "
        "Client bắt buộc phải yêu cầu người dùng đăng nhập lại."
    ),
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessage.SAME_PASSWORD.value,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": ErrorMessage.INVALID_CREDENTIAL.value,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": ErrorMessage.INACTIVE_USER.value,
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": ErrorMessage.BAD_REQUEST.value,
        },
    },
)
async def change_password(
    current_user: CurrentUser,
    change_password_request: ChangePasswordRequest,
    services: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    await services.change_password(current_user, change_password_request)
