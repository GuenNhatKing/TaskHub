"""sync_password_changed_at_default_and_backfill

Revision ID: 21302dab1b5e
Revises: 0efaa117e708
Create Date: 2026-11-24 21:02:34.760635

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "21302dab1b5e"
down_revision: Union[str, Sequence[str], None] = "0efaa117e708"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Đồng bộ dữ liệu cho các user cũ về thời điểm tạo tài khoản để không làm mất hiệu lực token đang dùng
    op.execute("UPDATE users SET password_changed_at = created_at")

    # Gỡ bỏ server_default=now() ở DB để chuyển sang dùng hoàn toàn giờ App (Python default)
    op.alter_column(
        "users",
        "password_changed_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "password_changed_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=False,
    )
