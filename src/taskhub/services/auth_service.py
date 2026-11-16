from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from taskhub.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from taskhub.exceptions import InactiveUserException, InvalidCredentialException
from taskhub.repos import UserRepository
from taskhub.schemas.token import TokenResponse
from taskhub.schemas.user import UserLoginRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    def _create_token_response(email: str) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(email),
            refresh_token=create_refresh_token(email),
        )

    async def authenticate_user(self, data: UserLoginRequest) -> TokenResponse:
        user = await self.repository.get_by_email(data.email)
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
        refresh_token: str,
    ) -> TokenResponse | None:

        try:
            payload = decode_refresh_token(refresh_token)
        except InvalidTokenError:
            raise InvalidCredentialException("Refresh token không hợp lệ")

        email = payload["sub"]

        user = await self.repository.get_by_email(email)

        if not user:
            raise InvalidCredentialException()

        if not user.is_active:
            raise InactiveUserException()

        return self._create_token_response(user.email)
