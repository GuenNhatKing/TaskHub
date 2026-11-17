from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import get_auth_service, get_user_service
from taskhub.schemas.user import UserLoginRequest, UserRegisterRequest, UserResponse
from taskhub.services.auth_service import AuthService
from taskhub.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])
from taskhub.schemas.token import LogoutRequest, RefreshTokenRequest, TokenResponse


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    data: UserRegisterRequest,
    services: Annotated[UserService, Depends(get_user_service)],
):
    return await services.create_user(data)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    data: UserLoginRequest,
    services: Annotated[AuthService, Depends(get_auth_service)],
):
    return await services.authenticate_user(data)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh(
    refresh_request: RefreshTokenRequest,
    services: Annotated[AuthService, Depends(get_auth_service)],
):
    return await services.refresh_tokens(refresh_request)


@router.post("/logout", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    logout_request: LogoutRequest,
    services: Annotated[AuthService, Depends(get_auth_service)],
):
    await services.logout(logout_request)
