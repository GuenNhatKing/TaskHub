import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        self.db.add(user)

        await self.db.flush()
        await self.db.refresh(user)

        return user
