from typing import Annotated

from pydantic import AfterValidator, EmailStr, StringConstraints

from taskhub.core.constants import (
    BCRYPT_MAX_BYTES,
    FULLNAME_LENGTH,
    PASSWORD_LENGTH,
    PASSWORD_MIN_LENGTH,
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
    str, StringConstraints(min_length=1, max_length=WORKSPACE_NAME_LENGTH)
]
