import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import UUID, DateTime, String, func
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

PROJECT_NAME_LENGTH = 100
DESC_LENGTH = 1000


class ProjectStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(PROJECT_NAME_LENGTH), nullable=False)
    description: Mapped[str | None] = mapped_column(String(DESC_LENGTH), nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        SqlAlchemyEnum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
