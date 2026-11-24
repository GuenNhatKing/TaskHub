from fastapi import status

from taskhub.core.messages import ErrorCode, ErrorMessage

from .base_business_ex import BaseBusinessException


class NotFoundException(BaseBusinessException):
    def __init__(
        self,
        find_by: str,
        value: str,
        message: str = ErrorMessage.NOT_FOUND,
    ):
        self.find_by = find_by
        self.value = value
        super().__init__(
            message=message,
            code=ErrorCode.NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )
