from datetime import UTC, datetime, timedelta
import hashlib

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from taskhub.core.config import settings
from taskhub.core.constants import PASSWORD_LENGTH

crypt_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12,
)


BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    if len(password) > PASSWORD_LENGTH:
        raise ValueError(f"Mật khẩu dài quá độ dài quy định là {PASSWORD_LENGTH} ký tự")
    if len(password.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise ValueError("Mật khẩu không được vượt quá 72 bytes")
    return crypt_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    if len(plain_password) > PASSWORD_LENGTH:
        raise ValueError(f"Mật khẩu dài quá độ dài quy định là {PASSWORD_LENGTH} ký tự")
    if len(plain_password.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise ValueError("Mật khẩu không được vượt quá 72 bytes")

    return crypt_context.verify(
        plain_password,
        hashed_password,
    )


def _create_token(email: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(UTC)

    payload = {
        "sub": str(email),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def _decode_token(token: str, token_type: str) -> dict:
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
        options={"require": ["sub", "type", "iat", "exp", "iss", "aud"]},
    )

    if payload["type"] != token_type:
        raise InvalidTokenError(f"Token không hợp lệ, token phải là loại: {token_type}")

    return payload


def create_access_token(email: str) -> str:
    return _create_token(
        email=email,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def decode_access_token(token: str) -> dict:
    return _decode_token(token, token_type="access")


def create_refresh_token(email: str) -> str:
    return _create_token(
        email=email,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_refresh_token(token: str) -> dict:
    return _decode_token(token, token_type="refresh")


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
