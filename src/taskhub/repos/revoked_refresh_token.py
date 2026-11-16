from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import RevokedRefreshToken

from .base import BaseRepository


class RevokedRefreshTokenRepository(BaseRepository[RevokedRefreshToken]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=RevokedRefreshToken)
