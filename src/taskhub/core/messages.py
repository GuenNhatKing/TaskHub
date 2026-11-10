from enum import Enum


class ErrorCode(Enum):
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"
    EMAIL_EXISTED = "EMAIL_EXISTED"
    USER_NOT_FOUND = "USER_NOT_FOUND"


class ErrorMessage(Enum):
    UNEXPECTED_ERROR = "Đã xảy ra lỗi ngoài dự kiến"
    EMAIL_EXISTED = "Email đã được sử dụng"
    USER_NOT_FOUND = "Người dùng không tồn tại"
