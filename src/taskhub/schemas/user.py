import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from taskhub.models.user import FULLNAME_LENGTH, ROLE

PASSWORD_LENGTH = 20


# POST /users
class UserCreate(BaseModel):
    email: str = EmailStr
    full_name: str = Field(max_length=FULLNAME_LENGTH)
    password: str = Field(max_length=PASSWORD_LENGTH)


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    created_at: datetime
    role: ROLE
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )
