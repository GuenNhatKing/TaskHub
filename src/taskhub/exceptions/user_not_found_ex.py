from fastapi import status

from taskhub.core.messages import ErrorCode, ErrorMessage

from .base_business_ex import BaseBusinessException


class UserNotFoundException(BaseBusinessException):
    def __init__(
        self,
        email: str,
        message: str = ErrorMessage.USER_NOT_FOUND,
    ):
        self.email = email
        super().__init__(
            message=message,
            code=ErrorCode.USER_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )
