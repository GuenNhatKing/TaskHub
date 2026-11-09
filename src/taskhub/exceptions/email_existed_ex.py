from .base_business_ex import BaseBusinessException


class EmailExistedException(BaseBusinessException):
    def __init__(self, email: str, message: str = "Email đã được sử dụng"):
        self.email = email
        self.message = message
        super().__init__(message)
