import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from taskhub.core.constants import DUMMY_PASSWORD_HASH
from taskhub.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from taskhub.exceptions import InactiveUserException, InvalidCredentialException
from taskhub.exceptions.auth_ex import InvalidTokenException, SamePasswordException
from taskhub.repos import RevokedRefreshTokenRepository
from taskhub.repos.revoked_refresh_group import RevokedRefreshGroupRepository
from taskhub.schemas.token import LogoutRequest, RefreshTokenRequest, TokenResponse
from taskhub.schemas.user import ChangePasswordRequest, UserLoginRequest
from taskhub.services.user_service import UserService


class AuthService:
    def __init__(self, db: AsyncSession, user_service: UserService):
        self.db = db
        self.revoked_refresh_token_repository = RevokedRefreshTokenRepository(db)
        self.revoked_refresh_group_repository = RevokedRefreshGroupRepository(db)
        self.user_service = user_service

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
        user = await self.user_service.repository.get_by_email(data.email)

        # Chọn hash thật nếu có user, ngược lại dùng dummy hash
        hashed_password = user.hashed_password if user else DUMMY_PASSWORD_HASH

        is_valid = await run_in_threadpool(
            verify_password, data.password, hashed_password
        )

        if not user or not is_valid:
            raise InvalidCredentialException()

        if not user.is_active:
            raise InactiveUserException()

        refresh_group = uuid.uuid4()

        return self._create_token_response(user.id, refresh_group)

    async def refresh_tokens(
        self,
        refresh_request: RefreshTokenRequest,
    ) -> TokenResponse:

        payload = decode_refresh_token(refresh_request.refresh_token)
        jti = uuid.UUID(payload["jti"])
        group = uuid.UUID(payload["group"])

        # Kiểm tra group đã bị revoke chưa
        revoked_group = await self.revoked_refresh_group_repository.get_by_id(group)
        if revoked_group is not None:
            raise InvalidTokenException()

        # Kiểm tra thông tin user
        user_id = uuid.UUID(payload["sub"])
        user = await self.user_service.repository.get_by_id(user_id)

        if not user:
            raise InvalidTokenException()

        if not user.is_active:
            raise InactiveUserException()

        # Kiểm tra token có được tạo trước thời điểm đổi mật khẩu không
        issued_at = datetime.fromtimestamp(payload["iat"], UTC)
        password_changed_at = user.password_changed_at
        if password_changed_at.tzinfo is None:
            password_changed_at = password_changed_at.replace(tzinfo=UTC)
        if issued_at < password_changed_at:
            await self._revoke_refresh_group(group)
            raise InvalidTokenException()

        # Revoke token hiện tại (Rotation)
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
            await self._revoke_refresh_group(group)
            raise InvalidTokenException()

        # Cấp token mới
        return self._create_token_response(user_id, group)

    async def logout(
        self,
        logout_request: LogoutRequest,
    ) -> None:

        payload = decode_refresh_token(logout_request.refresh_token)
        jti = uuid.UUID(payload["jti"])
        group = uuid.UUID(payload["group"])

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
            await self._revoke_refresh_group(group)
            raise InvalidTokenException()

        await self._revoke_refresh_group(group)

    async def change_password(
        self,
        token: str,
        change_password_request: ChangePasswordRequest,
    ):
        user = await self.user_service.get_user(token)
        # Kiểm tra mật khẩu cũ có khớp không
        is_valid = await run_in_threadpool(
            verify_password, change_password_request.old_password, user.hashed_password
        )
        if not is_valid:
            raise InvalidCredentialException()

        # Tránh đặt mật khẩu mới trùng với mật khẩu cũ
        if change_password_request.old_password == change_password_request.new_password:
            raise SamePasswordException()

        # Hash mật khẩu mới và cập nhật
        new_hashed_password = await run_in_threadpool(
            hash_password, change_password_request.new_password
        )

        await self.user_service.repository.update(
            user,
            {
                "hashed_password": new_hashed_password,
                "password_changed_at": datetime.now(UTC),
            },
        )
        try:
            await self.db.commit()
            await self.db.refresh(user)
        except Exception:
            await self.db.rollback()
            raise
