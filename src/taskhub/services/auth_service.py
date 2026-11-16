from datetime import UTC, datetime

from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from taskhub.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_refresh_token,
    verify_password,
)
from taskhub.exceptions import InactiveUserException, InvalidCredentialException
from taskhub.models import RevokedRefreshToken
from taskhub.repos import RevokedRefreshTokenRepository, UserRepository
from taskhub.schemas.token import LogoutRequest, RefreshTokenRequest, TokenResponse
from taskhub.schemas.user import UserLoginRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.revoked_refresh_token_repository = RevokedRefreshTokenRepository

    @staticmethod
    def _create_token_response(email: str) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(email),
            refresh_token=create_refresh_token(email),
        )

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

        return self._create_token_response(user.email)

    async def refresh_tokens(
        self,
        refresh_request: RefreshTokenRequest,
    ) -> TokenResponse | None:

        try:
            payload = decode_refresh_token(refresh_request.refresh_token)
        except InvalidTokenError:
            raise InvalidCredentialException("Refresh token không hợp lệ")

        # Kiểm tra token bị revoke chưa
        token_hash = hash_refresh_token(refresh_request.refresh_token)

        revoked_token = await self.revoked_refresh_token_repository.get_by_id(
            token_hash
        )

        if revoked_token is not None:
            raise InvalidCredentialException("Refresh token không hợp lệ")

        email = payload["sub"]

        user = await self.user_repository.get_by_email(email)

        if not user:
            raise InvalidCredentialException()

        if not user.is_active:
            raise InactiveUserException()

        return self._create_token_response(user.email)

    async def revoke_refresh_token(
        self,
        logout_request: LogoutRequest,
    ) -> None:

        try:
            payload = decode_refresh_token(logout_request.refresh_token)
        except InvalidTokenError:
            raise InvalidCredentialException("Refresh token không hợp lệ")

        token_hash = hash_refresh_token(logout_request.refresh_token)

        # Tránh lưu trùng token
        existing = await self.db.get(
            RevokedRefreshToken,
            token_hash,
        )

        if existing is not None:
            return

        revoked_token = RevokedRefreshToken(
            token_hash=token_hash,
            expires_at=datetime.fromtimestamp(
                payload["exp"],
                UTC,
            ),
            revoked_at=datetime.now(UTC),
        )

        await self.revoked_refresh_token_repository.create(revoked_token)
        await self.db.commit()
