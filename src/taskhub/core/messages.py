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
    INTERNAL_SERVER_ERROR = (
        "Đã có lỗi xảy ra từ hệ thống. Vui lòng thử lại sau hoặc liên hệ Admin."
    )
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
    INACTIVE_USER = "Tài khoản đã bị vô hiệu hóa"

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

    PROJECT_NOT_FOUND = "Project không tồn tại"
    PROJECT_ARCHIVED = "Project đã được lưu trữ, không thể thực hiện thao tác chỉnh sửa"
    WORKSPACE_EDITOR_REQUIRED = (
        "Chỉ chủ sở hữu hoặc người chỉnh sửa mới có quyền thực hiện thao tác này"
    )

    REQUIRE_CURRENT_PASSWORD_TO_CHANGE_EMAIL = (
        "Phải nhập mật khẩu hiện tại để thay đổi email"
    )
    INCORRECT_CURRENT_PASSWORD = "Mật khẩu hiện tại không chính xác"
    CANNOT_REMOVE_SELF = "Không thể tự xóa chính bản thân"

    TASK_NOT_FOUND = "Task không tồn tại"
    ASSIGNEE_NOT_IN_WORKSPACE = (
        "Người được giao việc không phải thành viên của workspace"
    )
    INVALID_DUE_DATE = "Hạn hoàn thành phải lớn hơn thời điểm hiện tại"

    LABEL_NOT_FOUND = "Label không tồn tại"
    LABEL_EXISTED = "Tên label đã tồn tại trong project này"
    LABEL_NOT_IN_PROJECT = "Label không thuộc cùng project với task"
    TASK_LABEL_ALREADY_EXISTS = "Task đã được gắn label này"
    TASK_LABEL_NOT_FOUND = "Task chưa được gắn label này"

    COMMENT_NOT_FOUND = "Bình luận không tồn tại"
    COMMENT_DELETE_PERMISSION_DENIED = (
        "Chỉ tác giả bình luận hoặc chủ sở hữu workspace mới có quyền xóa bình luận này"
    )
    COMMENT_EDIT_PERMISSION_DENIED = (
        "Chỉ tác giả bình luận mới có quyền chỉnh sửa bình luận này"
    )
