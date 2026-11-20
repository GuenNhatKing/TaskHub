from fastapi import status

from taskhub.core.messages import ErrorCode, ErrorMessage
from taskhub.exceptions.base_business_ex import BaseBusinessException


class BadRequestException(BaseBusinessException):
    def __init__(
        self,
        message: str = ErrorMessage.PERMISSION_DENIED,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.PERMISSION_DENIED,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
