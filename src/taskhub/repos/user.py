from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import User

from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=User)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(self.model).where(self.model.email == email)
        )
        user = result.scalar_one_or_none()
        return user
