from fastapi import status

from .base_business_ex import BaseBusinessException


class EmailExistedException(BaseBusinessException):
    def __init__(self, email: str, message: str = "Email đã được sử dụng"):
        self.email = email
        super().__init__(
            message=message,
            code="EMAIL_EXISTED",
            meta={"email": email},
            status_code=status.HTTP_409_CONFLICT,
        )
