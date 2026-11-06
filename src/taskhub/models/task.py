import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import UUID, DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .comment import Comment
from .project import Project
from .user import User

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
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
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
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    comments: Mapped[list[Comment]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",  # Xóa đi nếu Task bị xóa và xóa coment khỏi Task
    )
    project: Mapped[Project] = relationship(back_populates="tasks")
    assignee: Mapped[User | None] = relationship(
        back_populates="assigned_tasks",
        foreign_keys=[assignee_id],  # Vì có 2 khóa ngoại đến User nên phải chỉ định
    )
    creator: Mapped[User] = relationship(
        back_populates="created_tasks", foreign_keys=[created_by]
    )
