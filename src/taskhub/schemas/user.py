import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from taskhub.core.validators import LoginPassword, LowerEmail, ValidName, ValidPassword
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
    email: LowerEmail | None = None
    full_name: ValidName | None = None
    current_password: LoginPassword | None = None


class ChangePasswordRequest(BaseRequest):
    old_password: LoginPassword
    new_password: ValidPassword
