import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

CONTENT_LENGTH = 1000


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    content: Mapped[str] = mapped_column(String(CONTENT_LENGTH), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
