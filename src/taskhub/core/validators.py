from datetime import UTC, datetime
from typing import Annotated, Any, TypeVar

from pydantic import AfterValidator, BeforeValidator, EmailStr, StringConstraints

from taskhub.core.constants import (
    BCRYPT_MAX_BYTES,
    COMMENT_CONTENT_LENGTH,
    DESC_LENGTH,
    FULLNAME_LENGTH,
    LABEL_NAME_LENGTH,
    PASSWORD_LENGTH,
    PASSWORD_MIN_LENGTH,
    PROJECT_NAME_LENGTH,
    TITLE_LENGTH,
    WORKSPACE_NAME_LENGTH,
)
from taskhub.core.messages import ErrorMessage

T = TypeVar("T")


ValidName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=FULLNAME_LENGTH),
]


def to_lowercase(value: str) -> str:
    return value.lower()


LowerEmail = Annotated[
    EmailStr,
    AfterValidator(to_lowercase),
]


def check_password_complexity(value: str) -> str:
    if not any(c.isdigit() for c in value) or not any(c.isalpha() for c in value):
        raise ValueError(ErrorMessage.WEAK_PASSWORD)
    return value


def check_password_bytes_length(value: str) -> str:
    if len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise ValueError(ErrorMessage.PASSWORD_TOO_LONG)
    return value


ValidPassword = Annotated[
    str,
    StringConstraints(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_LENGTH),
    AfterValidator(check_password_bytes_length),
    AfterValidator(check_password_complexity),
]

LoginPassword = Annotated[
    str,
    StringConstraints(
        min_length=1, max_length=PASSWORD_LENGTH
    ),  # Min length = 1 chỉ để chặn trường hợp password rỗng
]

ValidWorkspaceName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=1, max_length=WORKSPACE_NAME_LENGTH
    ),
]

ValidProjectName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=1, max_length=PROJECT_NAME_LENGTH
    ),
]

ValidDescription = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=0, max_length=DESC_LENGTH),
]


def check_field_is_not_null(value: Any) -> Any:
    if value is None:
        raise ValueError(ErrorMessage.CAN_NOT_BE_NULL)
    return value


# Với Kiểu dữ liệu là NotNull[T | None] = None
# Pydantic gán trực tiếp giá trị mặc định None cho field
# Các validator như là BeforeValidator chỉ chạy khi dữ liệu được truyền vào từ input,
# hoàn toàn không chạy đối với giá trị mặc định
# Nghĩa là với trường hợp không có giá trị -> Pass, có giá trị Null -> 422
NotNull = Annotated[T, BeforeValidator(check_field_is_not_null)]


ValidTaskTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=TITLE_LENGTH),
]


def ensure_timezone_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=UTC)
    return value


AwareDatetime = Annotated[
    datetime,
    AfterValidator(ensure_timezone_aware),
]

ValidLabelName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=1, max_length=LABEL_NAME_LENGTH
    ),
]

ValidCommentContent = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=1, max_length=COMMENT_CONTENT_LENGTH
    ),
]
