import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import UUID, DateTime, String, func
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

TITLE_LENGTH = 100
DESC_LENGTH = 1000


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    DONE = "DONE"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    title: Mapped[str] = mapped_column(String(TITLE_LENGTH), nullable=False)
    description: Mapped[str | None] = mapped_column(String(DESC_LENGTH), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SqlAlchemyEnum(TaskStatus), default=TaskStatus.TODO, nullable=False
    )
    priority: Mapped[Priority] = mapped_column(
        SqlAlchemyEnum(Priority), default=Priority.MEDIUM, nullable=False
    )
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
