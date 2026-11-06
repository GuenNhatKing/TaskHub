import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .label import Label
    from .task import Task


class TaskLabel(Base):
    __tablename__ = "task_labels"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), primary_key=True
    )
    label_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("labels.id"), primary_key=True
    )
    
    task: Mapped[Task] = relationship(back_populates="task_labels")
    label: Mapped[Label] = relationship(back_populates="task_labels")
