from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import RevokedRefreshGroup

from .base import BaseRepository


class RevokedRefreshGroupRepository(BaseRepository[RevokedRefreshGroup]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=RevokedRefreshGroup)
