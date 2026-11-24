from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from taskhub.core.messages import ErrorMessage
from taskhub.core.security import hash_password
from taskhub.exceptions import AlreadyExistedException
from taskhub.exceptions.auth_ex import InactiveUserException, InvalidTokenException
from taskhub.exceptions.not_found_ex import NotFoundException
from taskhub.models.user import User
from taskhub.repos import UserRepository
from taskhub.schemas.user import (
    UserChangeProfileRequest,
    UserRegisterRequest,
)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    async def get_user(self, user_id):
        user = await self.user_repository.get_by_id(user_id)

        if not user:
            raise NotFoundException(
                find_by="id",
                value=user_id,
                message=ErrorMessage.USER_NOT_FOUND,
            )

        if not user.is_active:
            raise InactiveUserException()

        return user

    async def update_user(
        self,
        current_user: User,
        change_profile_request: UserChangeProfileRequest,
    ):
        update_data = change_profile_request.model_dump(
            exclude_unset=True, exclude_none=True
        )
        if not update_data:
            return current_user

        email = update_data.get("email")
        # Chỉ kiểm tra trùng nếu người dùng đổi sang một email khác email hiện tại
        if email and email != current_user.email:
            existed_user = await self.user_repository.get_by_email(email)
            if existed_user:
                raise AlreadyExistedException(key=email)

        try:
            user = await self.user_repository.update(current_user, update_data)
            await self.db.commit()
            await self.db.refresh(user)
        except IntegrityError:
            await self.db.rollback()
            if update_data.get("email"):
                raise AlreadyExistedException(key=update_data["email"])
            raise

        return user

    async def create_user(self, data: UserRegisterRequest):
        user_dict = data.model_dump()
        user_dict.pop("password", None)  # Không đưa password vào

        # Dùng để biến hàm đồng bộ thành bất đồng bộ, server không phải chờ hash xong
        user_dict["hashed_password"] = await run_in_threadpool(
            hash_password, data.password
        )

        # Kiểm tra email đã tồn tại chưa
        existed_user = await self.user_repository.get_by_email(data.email)
        if existed_user:
            raise AlreadyExistedException(key=data.email)

        try:
            user = await self.user_repository.create(user_dict)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            # Dù đã kiểm tra trước đó, vẫn có khả năng race!!
            await self.db.rollback()
            raise AlreadyExistedException(key=data.email)
        except Exception:
            await self.db.rollback()
            raise
