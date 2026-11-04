import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import User
from taskhub.repos import UserRepository
from taskhub.schemas.user import UserCreate


class UserServices:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.repository.get_by_id(user_id)

    async def create_user(self, data: UserCreate):
        user = User(email=data.email, full_name=data.full_name)
        try:
            await self.repository.create_user(user)
            await self.db.commit()
            return user
        except Exception:
            await self.db.rollback()
            raise
