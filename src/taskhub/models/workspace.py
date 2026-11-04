import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

WORKSPACE_NAME_LENGTH = 100


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    name: Mapped[str] = mapped_column(String(WORKSPACE_NAME_LENGTH), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
