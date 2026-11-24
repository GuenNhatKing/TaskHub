from fastapi import status

from taskhub.core.messages import ErrorCode, ErrorMessage
from taskhub.exceptions.base_business_ex import BaseBusinessException


class BadRequestException(BaseBusinessException):
    def __init__(
        self,
        message: str = ErrorMessage.BAD_REQUEST,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.BAD_REQUEST,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
