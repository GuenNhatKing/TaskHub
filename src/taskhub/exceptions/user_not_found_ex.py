import uuid

from .base_business_ex import BaseBusinessException


class UserNotFoundException(BaseBusinessException):
    def __init__(self, user_id: uuid.UUID, message: str = "Người dùng không tồn tại"):
        self.user_id = user_id
        self.message = message
        super().__init__(message)
