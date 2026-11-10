from fastapi import status

from taskhub.core.messages import ErrorCode, ErrorMessage

from .base_business_ex import BaseBusinessException


class EmailExistedException(BaseBusinessException):
    def __init__(self, email: str, message: str = ErrorMessage.EMAIL_EXISTED):
        self.email = email
        super().__init__(
            message=message,
            code=ErrorCode.EMAIL_EXISTED,
            meta={"email": email},
            status_code=status.HTTP_409_CONFLICT,
        )
