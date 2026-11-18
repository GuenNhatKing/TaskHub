import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskhub.models import Base

if TYPE_CHECKING:
    from .revoked_refresh_group import RevokedRefreshGroup


class RevokedRefreshToken(Base):
    __tablename__ = "revoked_refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )

    # Revoked nhiều token cùng 1 group khi logout
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("revoked_refresh_groups.id"),
        nullable=False,
        index=True,
    )

    # Dùng để dọn dẹp định kỳ, đặt index để xóa nhanh hơn
    # TODO (Day 7 Celery beat).
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    group: Mapped[RevokedRefreshGroup] = relationship(back_populates="tokens")
