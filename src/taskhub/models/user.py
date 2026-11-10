import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, DateTime, String, func
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskhub.core.constants import EMAIL_LENGTH, FULLNAME_LENGTH
from taskhub.core.enums import ROLE

from .base import Base

if TYPE_CHECKING:
    from .comment import Comment
    from .task import Task
    from .workspace import Workspace
    from .workspace_member import WorkspaceMember


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
        cascade="all, delete-orphan",  # Xóa đi nếu User bị xóa và User xóa comment
    )

    workspaces: Mapped[list[Workspace]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    workspace_members: Mapped[list[WorkspaceMember]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    created_tasks: Mapped[list[Task]] = relationship(
        back_populates="creator",
        foreign_keys="[Task.created_by]",  # Vì có 2 Task được gọi phải chỉ định
    )
    assigned_tasks: Mapped[list[Task]] = relationship(
        back_populates="assignee",
        foreign_keys="[Task.assignee_id]",
    )
