import uuid
from enum import Enum

from sqlalchemy import UUID
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class WorkspaceMemberRole(str, Enum):
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    role: Mapped[WorkspaceMemberRole] = mapped_column(
        SqlAlchemyEnum(WorkspaceMemberRole),
        default=WorkspaceMemberRole.VIEWER,
        nullable=False,
    )
