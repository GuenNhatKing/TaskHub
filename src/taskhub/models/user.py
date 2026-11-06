import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import UUID, Boolean, DateTime, String, func
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .comment import Comment

EMAIL_LENGTH = 255
FULLNAME_LENGTH = 100


class ROLE(str, Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # Ép SQLAlchemy sử dụng đối tượng uuid.UUID thay vì str,
        default=uuid.uuid4,
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(
        String(EMAIL_LENGTH), unique=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(FULLNAME_LENGTH), nullable=False)
    # Dùng thuật toán bcrypt, độ dài đúng 60 ký tự
    hashed_password: Mapped[str] = mapped_column(String(60), nullable=False)
    role: Mapped[ROLE] = mapped_column(
        SqlAlchemyEnum(ROLE), default=ROLE.MEMBER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Tự động điền thời gian ở phía DB
        nullable=False,
    )

    comments: Mapped[list[Comment]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan" # Xóa đi nếu User bị xóa và User xóa comment
    )
