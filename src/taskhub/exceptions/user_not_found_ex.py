import uuid

from fastapi import status

from taskhub.core.messages import ErrorCode, ErrorMessage

from .base_business_ex import BaseBusinessException


class UserNotFoundException(BaseBusinessException):
    def __init__(self, user_id: uuid.UUID, message: str = ErrorMessage.USER_NOT_FOUND):
        self.user_id = user_id
        super().__init__(
            message=message,
            code=ErrorCode.USER_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )
