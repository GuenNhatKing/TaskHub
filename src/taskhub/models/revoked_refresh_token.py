from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from taskhub.models import Base


class RevokedRefreshToken(Base):
    __tablename__ = "revoked_refresh_tokens"

    hashed_token: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Dùng để dọn dẹp định kỳ, đặt index để xóa nhanh hơn
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
