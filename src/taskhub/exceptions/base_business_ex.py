from typing import Any

from fastapi import status

from taskhub.core.messages import ErrorCode, ErrorMessage


class BaseBusinessException(Exception):
    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        meta: dict[str, Any] | None = None,
        status_code: int | None = None,
    ):
        self.message = message or ErrorMessage.UNEXPECTED_ERROR
        self.code = code or ErrorCode.UNEXPECTED_ERROR
        self.meta = meta
        self.status_code = status_code or status.HTTP_400_BAD_REQUEST
        super().__init__(self.message)
