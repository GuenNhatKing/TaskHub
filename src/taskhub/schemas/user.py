import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from taskhub.core.validators import LoginPassword, LowerEmail, ValidName, ValidPassword
from taskhub.models.user import ROLE


class UserRegisterRequest(BaseModel):
    email: LowerEmail
    full_name: ValidName
    password: ValidPassword


class UserLoginRequest(BaseModel):
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
