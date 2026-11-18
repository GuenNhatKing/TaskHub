import uuid
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from taskhub.core.config import settings
from taskhub.core.constants import PASSWORD_LENGTH
from taskhub.core.messages import ErrorMessage

crypt_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12,
)


BCRYPT_MAX_BYTES = 72


def validate_password(password: str):
    if len(password) > PASSWORD_LENGTH:
        raise ValueError(ErrorMessage.PASSWORD_TOO_LONG)
    if len(password.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise ValueError(ErrorMessage.PASSWORD_TOO_LONG)


def hash_password(password: str) -> str:
    validate_password(password)
    return crypt_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    validate_password(plain_password)
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

    if token_type == "refresh":
        payload["group"] = str(group)

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def _decode_token(token: str, token_type: str) -> dict:
    require = ["sub", "jti", "type", "iat", "exp", "iss", "aud"]
    if token_type == "refresh":
        require.append("group")
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
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
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def decode_access_token(token: str) -> dict:
    return _decode_token(token, token_type="access")


def create_refresh_token(user_id: str, group: uuid.UUID) -> str:
    return _create_token(
        user_id=user_id,
        group=group,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_refresh_token(token: str) -> dict:
    return _decode_token(token, token_type="refresh")
