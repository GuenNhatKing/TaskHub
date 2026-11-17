import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskhub.models import Base

if TYPE_CHECKING:
    from .revoked_refresh_token import RevokedRefreshToken


class RevokedRefreshGroup(Base):
    __tablename__ = "revoked_refresh_groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )

    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    tokens: Mapped[list[RevokedRefreshToken]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )
