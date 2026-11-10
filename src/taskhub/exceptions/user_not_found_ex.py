import uuid

from fastapi import status

from .base_business_ex import BaseBusinessException


class UserNotFoundException(BaseBusinessException):
    def __init__(self, user_id: uuid.UUID, message: str = "Người dùng không tồn tại"):
        self.user_id = user_id
        super().__init__(
            message=message,
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
