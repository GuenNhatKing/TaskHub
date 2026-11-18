import uuid
from datetime import UTC, datetime

from jwt import InvalidTokenError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from taskhub.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from taskhub.exceptions import InactiveUserException, InvalidCredentialException
from taskhub.repos import RevokedRefreshTokenRepository, UserRepository
from taskhub.repos.revoked_refresh_group import RevokedRefreshGroupRepository
from taskhub.schemas.token import LogoutRequest, RefreshTokenRequest, TokenResponse
from taskhub.schemas.user import UserLoginRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.revoked_refresh_token_repository = RevokedRefreshTokenRepository(db)
        self.revoked_refresh_group_repository = RevokedRefreshGroupRepository(db)

    @staticmethod
    def _create_token_response(
        user_id: uuid.UUID, refresh_group: uuid.UUID
    ) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id, refresh_group),
        )

    async def _revoke_refresh_group(self, refresh_group: uuid.UUID):
        revoked_token_group_dict = {
            "id": refresh_group,
            "revoked_at": datetime.now(UTC),
        }

        try:
            await self.revoked_refresh_group_repository.create(revoked_token_group_dict)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()

    async def authenticate_user(self, data: UserLoginRequest) -> TokenResponse:
        user = await self.user_repository.get_by_email(data.email)
        if not user:
            raise InvalidCredentialException()

        if not user.is_active:
            raise InactiveUserException()

        is_valid = await run_in_threadpool(
            verify_password, data.password, user.hashed_password
        )

        if not is_valid:
            raise InvalidCredentialException()

        refresh_group = uuid.uuid4()

        return self._create_token_response(user.id, refresh_group)

    async def refresh_tokens(
        self,
        refresh_request: RefreshTokenRequest,
    ) -> TokenResponse | None:

        try:
            payload = decode_refresh_token(refresh_request.refresh_token)
            jti = uuid.UUID(payload["jti"])
            group = uuid.UUID(payload["group"])
        except InvalidTokenError:
            raise InvalidCredentialException("Refresh token không hợp lệ")

        # Kiểm tra group đã bị revoke chưa
        revoked_group = await self.revoked_refresh_group_repository.get_by_id(group)
        if revoked_group is not None:
            raise InvalidCredentialException("Refresh token không hợp lệ")

        # Kiểm tra thông tin user
        user_id = uuid.UUID(payload["sub"])

        user = await self.user_repository.get_by_id(user_id)

        if not user:
            raise InvalidCredentialException()

        if not user.is_active:
            raise InactiveUserException()

        # Revoke token (không cần check, có lỗi db thì trả 401)
        revoked_token_dict = {
            "id": jti,
            "group_id": group,
            "expires_at": datetime.fromtimestamp(payload["exp"], UTC),
            "revoked_at": datetime.now(UTC),
        }

        try:
            await self.revoked_refresh_token_repository.create(revoked_token_dict)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            # Sử dụng token cũ -> có thể có ai đó đã đánh cắp token và refresh trước -> revoked toàn bộ group
            await self._revoke_refresh_group(group)
            raise InvalidCredentialException("Refresh token không hợp lệ")

        # Cấp token mới
        return self._create_token_response(user_id, group)

    async def logout(
        self,
        logout_request: LogoutRequest,
    ) -> None:

        try:
            payload = decode_refresh_token(logout_request.refresh_token)
            jti = uuid.UUID(payload["jti"])
            group = uuid.UUID(payload["group"])
        except InvalidTokenError:
            raise InvalidCredentialException("Refresh token không hợp lệ")

        # Revoke token (không cần check, có lỗi db thì trả 401)
        revoked_token_dict = {
            "id": jti,
            "group_id": group,
            "expires_at": datetime.fromtimestamp(payload["exp"], UTC),
            "revoked_at": datetime.now(UTC),
        }

        try:
            await self.revoked_refresh_token_repository.create(revoked_token_dict)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise InvalidCredentialException("Refresh token không hợp lệ")

        await self._revoke_refresh_group(group)
