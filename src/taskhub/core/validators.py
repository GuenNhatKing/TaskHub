from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, EmailStr, StringConstraints

from taskhub.core.constants import (
    BCRYPT_MAX_BYTES,
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
