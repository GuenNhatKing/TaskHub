import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from taskhub.core.dependencies import get_user_services
from taskhub.schemas.user import UserCreate, UserResponse
from taskhub.services.user import UserServices

router = APIRouter(prefix="/users", tags=["Users"])


logger = logging.getLogger(__name__)

MOCK_USER = UserResponse(
    id=uuid.uuid4(),
    full_name="nhat king",
    is_active=True,
    role="MEMBER",
    email="test@gmail.com",
    created_at="2026-11-04 12:00",
)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate, services: Annotated[UserServices, Depends(get_user_services)]
):
    return MOCK_USER
    try:
        return await services.create_user(data)
    except ValueError:
        logger.exception("Lỗi validate hoặc xử lý dữ liệu người dùng")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Yêu cầu không hợp lệ"
        )
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã có lỗi ở server, vui lòng thử lại sau",
        )


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: uuid.UUID, services: Annotated[UserServices, Depends(get_user_services)]
):
    return MOCK_USER
    result = await services.get_by_id(user_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result
