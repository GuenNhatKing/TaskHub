import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from taskhub.core.validators import (
    LoginPassword,
    LowerEmail,
    NotNull,
    ValidName,
    ValidPassword,
)
from taskhub.models.user import ROLE
from taskhub.schemas.base import BaseRequest


class UserRegisterRequest(BaseRequest):
    email: LowerEmail
    full_name: ValidName
    password: ValidPassword


class UserLoginRequest(BaseRequest):
    email: LowerEmail
    password: LoginPassword


class UserResponse(BaseModel):
    id: uuid.UUID
    email: LowerEmail
    full_name: str
    created_at: datetime
    role: ROLE
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserChangeProfileRequest(BaseRequest):
    email: NotNull[LowerEmail | None] = None
    full_name: NotNull[ValidName | None] = None
    current_password: NotNull[LoginPassword | None] = None


class ChangePasswordRequest(BaseRequest):
    current_password: LoginPassword
    new_password: ValidPassword
