import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from taskhub.core.validators import LowerEmail, ValidName, ValidPassword
from taskhub.models.user import ROLE


class UserCreate(BaseModel):
    email: LowerEmail
    full_name: ValidName
    password: ValidPassword


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
