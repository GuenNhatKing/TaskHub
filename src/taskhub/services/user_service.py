from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from taskhub.core.security import hash_password
from taskhub.exceptions import (
    EmailExistedException,
    UserNotFoundException,
)
from taskhub.models import User
from taskhub.repos import UserRepository
from taskhub.schemas.user import UserRegisterRequest


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    async def get_by_email(self, email: str) -> User:
        user = await self.repository.get_by_email(email)
        if not user:
            raise UserNotFoundException(email)
        return user

    async def create_user(self, data: UserRegisterRequest):
        user_dict = data.model_dump()
        user_dict.pop("password", None)  # Không đưa password vào

        # Dùng để biến hàm đồng bộ thành bất đồng bộ, server không phải chờ hash xong
        user_dict["hashed_password"] = await run_in_threadpool(
            hash_password, data.password
        )

        # Kiểm tra email đã tồn tại chưa
        existed_user = await self.repository.get_by_email(data.email)
        if existed_user:
            raise EmailExistedException(data.email)

        try:
            user = await self.repository.create(user_dict)
            await self.db.commit()
            return user
        except IntegrityError:
            # Dù đã kiểm tra trước đó, vẫn có khả năng race!!
            await self.db.rollback()
            raise EmailExistedException(data.email)
        except Exception:
            await self.db.rollback()
            raise
