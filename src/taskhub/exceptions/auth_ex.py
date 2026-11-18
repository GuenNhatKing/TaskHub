from fastapi import status

from taskhub.core.messages import ErrorCode, ErrorMessage

from .base_business_ex import BaseBusinessException


class InactiveUserException(BaseBusinessException):
    def __init__(
        self,
        message: str = ErrorMessage.INACTIVE_USER,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INACTIVE_USER,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class InvalidCredentialException(BaseBusinessException):
    def __init__(
        self,
        message: str = ErrorMessage.INVALID_CREDENTIAL,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_CREDENTIAL,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidTokenException(BaseBusinessException):
    def __init__(
        self,
        message: str = ErrorMessage.INVALID_REFRESH_TOKEN,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_CREDENTIAL,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
