import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import get_user_services
from taskhub.schemas.user import UserCreate, UserResponse
from taskhub.services.user import UserServices

router = APIRouter(prefix="/users", tags=["Users"])


logger = logging.getLogger(__name__)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate, services: Annotated[UserServices, Depends(get_user_services)]
):
    return await services.create_user(data)


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: uuid.UUID, services: Annotated[UserServices, Depends(get_user_services)]
):
    return await services.get_by_id(user_id)
