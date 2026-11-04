import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TaskLabel(Base):
    __tablename__ = "task_labels"

    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    label_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
