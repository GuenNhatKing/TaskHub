import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskhub.core.constants import DESC_LENGTH, PROJECT_NAME_LENGTH
from taskhub.core.enums import ProjectStatus

from .base import Base

if TYPE_CHECKING:
    from .label import Label
    from .task import Task
    from .workspace import Workspace


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
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

    workspace: Mapped[Workspace] = relationship(back_populates="projects")
    tasks: Mapped[list[Task]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    labels: Mapped[list[Label]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
