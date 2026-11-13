from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import get_user_services
from taskhub.schemas.user import UserRegisterForm, UserResponse
from taskhub.services.user import UserServices

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    data: UserRegisterForm,
    services: Annotated[UserServices, Depends(get_user_services)],
):
    return await services.create_user(data)
