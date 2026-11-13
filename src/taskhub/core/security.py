from passlib.context import CryptContext

crypt_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12,
)

from taskhub.core.constants import PASSWORD_LENGTH

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
