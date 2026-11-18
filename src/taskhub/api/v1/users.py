from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from taskhub.core.dependencies import get_user_service
from taskhub.schemas.user import UserResponse
from taskhub.services.user_service import UserService

security = HTTPBearer()

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_info(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    services: Annotated[UserService, Depends(get_user_service)],
):
    token = credentials.credentials
    return await services.get_user_info_by_token(token)
