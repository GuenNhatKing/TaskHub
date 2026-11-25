import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, Index, String, func
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskhub.core.constants import LABEL_NAME_LENGTH
from taskhub.core.enums import LabelColor

from .base import Base

if TYPE_CHECKING:
    from .project import Project
    from .task_label import TaskLabel


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
    __table_args__ = (
        Index(
            "uq_labels_project_id_lower_name",
            "project_id",
            func.lower(name),
            unique=True,
        ),
    )

    project: Mapped[Project] = relationship(back_populates="labels")

    task_labels: Mapped[list[TaskLabel]] = relationship(
        back_populates="label", cascade="all, delete-orphan"
    )
