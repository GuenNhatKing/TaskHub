import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.exceptions import EmailExistedException, UserNotFoundException
from taskhub.models import User
from taskhub.repos import UserRepository
from taskhub.schemas.user import UserCreate


class UserServices:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user

    async def create_user(self, data: UserCreate):
        user_dict = data.model_dump()
        user_dict.pop("password", None)  # Hiện tại chưa xử lý password
        user_dict["hashed_password"] = "Chua trien khai"  # Hiện tại chưa xử lý password

        # Kiểm tra email đã tồn tại chưa
        existed_user = await self.repository.get_by_email(data.email)
        if existed_user:
            raise EmailExistedException(data.email)

        try:
            user = await self.repository.create(user_dict)
            await self.db.commit()
            return user
        except Exception:
            await self.db.rollback()
            raise
