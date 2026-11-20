from typing import Any

from fastapi import status

from taskhub.core.messages import ErrorCode, ErrorMessage

from .base_business_ex import BaseBusinessException


class AlreadyExistedException(BaseBusinessException):
    def __init__(self, key: Any, message: str = ErrorMessage.ALREADY_EXISTED):
        self.key = key
        super().__init__(
            message=message,
            code=ErrorCode.ALREADY_EXISTED,
            meta={"key": key},
            status_code=status.HTTP_409_CONFLICT,
        )
