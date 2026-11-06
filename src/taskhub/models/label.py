import uuid
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .project import Project

LABEL_NAME_LENGTH = 100


class LabelColor(str, Enum):
    RED = "#EF4444"
    ORANGE = "#F97316"
    YELLOW = "#EAB308"
    GREEN = "#22C55E"
    BLUE = "#3B82F6"
    PURPLE = "#A855F7"
    PINK = "#EC4899"
    TEAL = "#14B8A6"
    BROWN = "#78350F"
    GRAY = "#6B7280"


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
