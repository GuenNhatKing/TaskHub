from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import CurrentUser, get_user_service
from taskhub.schemas.user import UserChangeProfileRequest, UserResponse
from taskhub.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_info(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def change_user_info(
    current_user: CurrentUser,
    change_profile_request: UserChangeProfileRequest,
    services: Annotated[UserService, Depends(get_user_service)],
):
    return await services.update_user(current_user, change_profile_request)
