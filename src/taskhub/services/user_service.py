import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from taskhub.core.security import decode_access_token, hash_password
from taskhub.exceptions import (
    EmailExistedException,
)
from taskhub.exceptions.auth_ex import InactiveUserException, InvalidTokenException
from taskhub.repos import UserRepository
from taskhub.schemas.user import (
    UserChangeProfileRequest,
    UserRegisterRequest,
    UserResponse,
)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    async def _get_user(self, token: str):
        payload = decode_access_token(token)
        user_id = uuid.UUID(payload["sub"])
        user = await self.repository.get_by_id(user_id)

        if not user:
            raise InvalidTokenException()

        if not user.is_active:
            raise InactiveUserException()

        return user

    async def get_user_info_by_token(self, token: str) -> UserResponse:
        return await self._get_user(token)

    async def change_user_info_by_token(
        self, token: str, change_profile_request: UserChangeProfileRequest
    ):

        user = await self._get_user(token)

        update_data = change_profile_request.model_dump(
            exclude_unset=True, exclude_none=True
        )
        if not update_data:
            return user

        email = update_data.get("email")
        # Chỉ kiểm tra trùng nếu người dùng đổi sang một email khác email hiện tại
        if email and email != user.email:
            existed_user = await self.repository.get_by_email(email)
            if existed_user:
                raise EmailExistedException(email)

        await self.repository.update(user, update_data)
        try:
            await self.db.commit()
            await self.db.refresh(user)
        except IntegrityError:
            await self.db.rollback()
            raise EmailExistedException(email)

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
            await self.db.refresh(user)
            return user
        except IntegrityError:
            # Dù đã kiểm tra trước đó, vẫn có khả năng race!!
            await self.db.rollback()
            raise EmailExistedException(data.email)
        except Exception:
            await self.db.rollback()
            raise
