from typing import Annotated

from pydantic import AfterValidator, EmailStr, StringConstraints

from taskhub.core.constants import FULLNAME_LENGTH, PASSWORD_LENGTH

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
        raise ValueError("Mật khẩu phải bao gồm cả chữ cái và chữ số")
    return value


ValidPassword = Annotated[
    str,
    StringConstraints(min_length=1, max_length=PASSWORD_LENGTH),
    AfterValidator(check_password_complexity),
]
