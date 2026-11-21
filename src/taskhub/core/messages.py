from enum import Enum


class ErrorCode(str, Enum):
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"
    ALREADY_EXISTED = "ALREADY_EXISTED"
    NOT_FOUND = "NOT_FOUND"
    INVALID_CREDENTIAL = "INVALID_CREDENTIAL"
    INACTIVE_USER = "INACTIVE_USER"
    INVALID_TOKEN = "INVALID_TOKEN"
    SAME_PASSWORD = "SAME_PASSWORD"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    BAD_REQUEST = "BAD_REQUEST"


class ErrorMessage(str, Enum):
    UNEXPECTED_ERROR = "Đã xảy ra lỗi ngoài dự kiến"

    ALREADY_EXISTED = "Đối tượng đã được sử dụng"
    EMAIL_EXISTED = "Email đã được sử dụng"
    WORKSPACE_EXISTED = "Workspace đã được sử dụng"
    MEMBER_ALREADY_EXISTS = "Người dùng này đã là thành viên của workspace"

    NOT_FOUND = "Đối tượng không tồn tại"
    USER_NOT_FOUND = "Người dùng không tồn tại"
    WORKSPACE_NOT_FOUND = "Workspace không tồn tại"
    WORKSPACE_MEMBER_NOT_FOUND = "Người dùng không phải thành viên của workspace"

    INVALID_CREDENTIAL = "Email hoặc mật khẩu không hợp lệ"
    INACTIVE_USER = "Tài khoản của bạn đã bị vô hiệu hóa"

    WEAK_PASSWORD = "Mật khẩu phải bao gồm cả chữ cái và chữ số"
    PASSWORD_TOO_LONG = "Mật khẩu dài quá độ dài quy định"

    INVALID_REFRESH_TOKEN = "Refresh token không hợp lệ"
    SAME_PASSWORD = "Mật khẩu mới trùng với mật khẩu cũ"

    PERMISSION_DENIED = "Bạn không có quyền thực hiện thao tác này"
    WORKSPACE_PERMISSION_DENIED = (
        "Bạn không có quyền quản lý hoặc thay đổi workspace này"
    )
    WORKSPACE_OWNER_REQUIRED = (
        "Chỉ chủ sở hữu workspace mới có quyền thực hiện thao tác này"
    )

    BAD_REQUEST = "Yêu cầu không hợp lệ"
    CANNOT_ASSIGN_OWNER_ROLE = "Không thể gán người tạo cho thành viên"
