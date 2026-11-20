from typing import Any

from fastapi import status

from taskhub.core.messages import ErrorCode, ErrorMessage
from taskhub.exceptions.base_business_ex import BaseBusinessException


class PermissionDeniedException(BaseBusinessException):
    def __init__(
        self,
        message: str = ErrorMessage.PERMISSION_DENIED,
        required_role: Any | None = None,
    ):
        self.required_role = required_role
        meta = {"required_role": required_role} if required_role is not None else None

        super().__init__(
            message=message,
            code=ErrorCode.PERMISSION_DENIED,
            meta=meta,
            status_code=status.HTTP_403_FORBIDDEN,
        )
