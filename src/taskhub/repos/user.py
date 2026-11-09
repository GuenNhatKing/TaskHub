from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import User

from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=User)
