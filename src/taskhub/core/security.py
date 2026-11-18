import uuid
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from taskhub.core.config import settings
from taskhub.core.constants import BCRYPT_ROUNDS, TokenType

crypt_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=BCRYPT_ROUNDS)


def hash_password(password: str) -> str:
    return crypt_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return crypt_context.verify(
        plain_password,
        hashed_password,
    )


def _create_token(
    user_id: str,
    token_type: str,
    expires_delta: timedelta,
    group: uuid.UUID | None = None,
) -> str:
    now = datetime.now(UTC)

    payload = {
        "sub": str(user_id),
        "jti": str(uuid4()),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }

    if token_type == TokenType.REFRESH:
        payload["group"] = str(group)

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def _decode_token(token: str, token_type: str) -> dict:
    require = ["sub", "jti", "type", "iat", "exp", "iss", "aud"]
    if token_type == TokenType.REFRESH:
        require.append("group")
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM],
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
        options={"require": require},
    )

    if payload["type"] != token_type:
        raise InvalidTokenError(f"Token không hợp lệ, token phải là loại: {token_type}")

    return payload


def create_access_token(user_id: str) -> str:
    return _create_token(
        user_id=user_id,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def decode_access_token(token: str) -> dict:
    return _decode_token(token, token_type=TokenType.ACCESS)


def create_refresh_token(user_id: str, group: uuid.UUID) -> str:
    return _create_token(
        user_id=user_id,
        group=group,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_refresh_token(token: str) -> dict:
    return _decode_token(token, token_type=TokenType.REFRESH)
