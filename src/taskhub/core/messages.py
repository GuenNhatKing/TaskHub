from enum import Enum


class ErrorCode(str, Enum):
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"
    EMAIL_EXISTED = "EMAIL_EXISTED"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INVALID_CREDENTIAL = "INVALID_CREDENTIAL"
    INACTIVE_USER = "INACTIVE_USER"
    INVALID_TOKEN = "INVALID_TOKEN"
    SAME_PASSWORD = "SAME_PASSWORD"


class ErrorMessage(str, Enum):
    UNEXPECTED_ERROR = "Đã xảy ra lỗi ngoài dự kiến"
    EMAIL_EXISTED = "Email đã được sử dụng"
    USER_NOT_FOUND = "Người dùng không tồn tại"
    INVALID_CREDENTIAL = "Email hoặc mật khẩu không hợp lệ"
    INACTIVE_USER = "Tài khoản của bạn đã bị vô hiệu hóa"
    WEAK_PASSWORD = "Mật khẩu phải bao gồm cả chữ cái và chữ số"
    PASSWORD_TOO_LONG = "Mật khẩu dài quá độ dài quy định"
    INVALID_REFRESH_TOKEN = "Refresh token không hợp lệ"
    SAME_PASSWORD = "Mật khẩu mới trùng với mật khẩu cũ"
