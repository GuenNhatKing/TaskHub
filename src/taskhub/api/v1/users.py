import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from taskhub.core.dependencies import get_user_service
from taskhub.core.validators import LowerEmail
from taskhub.schemas.user import UserResponse
from taskhub.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


logger = logging.getLogger(__name__)


@router.get("/{email}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    email: LowerEmail, services: Annotated[UserService, Depends(get_user_service)]
):
    return await services.get_by_email(email)
