import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskhub.core.enums import LabelColor

from .base import Base

if TYPE_CHECKING:
    from .project import Project
    from .task_label import TaskLabel

LABEL_NAME_LENGTH = 100


class Label(Base):
    __tablename__ = "labels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(LABEL_NAME_LENGTH), nullable=False)
    color: Mapped[LabelColor] = mapped_column(
        SqlAlchemyEnum(LabelColor), default=LabelColor.BLUE, nullable=False
    )

    project: Mapped[Project] = relationship(back_populates="labels")

    task_labels: Mapped[list[TaskLabel]] = relationship(
        back_populates="label", cascade="all, delete-orphan"
    )
