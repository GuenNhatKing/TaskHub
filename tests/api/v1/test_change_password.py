from sqlalchemy import update

from taskhub.models.user import User
from tests.api.v1.constants import (
    CHANGE_PASSWORD_URL,
    LOGIN_URL,
    PROFILES_URL,
    REFRESH_URL,
)
from tests.api.v1.get_auth_credentials import get_auth_headers, get_auth_tokens


async def test_change_password_success(api_client, active_user):
    headers = await get_auth_headers(api_client, active_user)
    new_password = "StrongPassword@123"

    response = await api_client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": active_user["password"],
            "new_password": new_password,
        },
        headers=headers,
    )
    assert response.status_code == 200

    # Xác nhận không thể đăng nhập bằng mật khẩu cũ nữa
    old_login_res = await api_client.post(
        LOGIN_URL,
        json={
            "email": active_user["email"],
            "password": active_user["password"],
        },
    )
    assert old_login_res.status_code == 401

    # Xác nhận đăng nhập thành công bằng mật khẩu mới
    new_login_res = await api_client.post(
        LOGIN_URL,
        json={
            "email": active_user["email"],
            "password": new_password,
        },
    )
    assert new_login_res.status_code == 200
    assert "access_token" in new_login_res.json()

    # Access token cũ gọi GET /users/me sau khi đổi pass -> 401
    me_res = await api_client.get(PROFILES_URL, headers=headers)
    assert me_res.status_code == 401

    # Refresh ngay bằng refresh_token mới vừa nhận sau khi đổi pass -> 200
    new_tokens = new_login_res.json()
    refresh_res = await api_client.post(
        REFRESH_URL,
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()


async def test_change_password_wrong_current_password(api_client, active_user):
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": "WrongPassword@123",
            "new_password": "StrongPassword@123",
        },
        headers=headers,
    )
    assert response.status_code == 400


async def test_change_password_same_as_old(api_client, active_user):
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": active_user["password"],
            "new_password": active_user["password"],
        },
        headers=headers,
    )
    assert response.status_code == 400


async def test_change_password_weak_new_password(api_client, active_user):
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": active_user["password"],
            "new_password": "12345678",
        },
        headers=headers,
    )
    assert response.status_code == 422


async def test_change_password_unauthenticated(api_client):
    response = await api_client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": "SomePassword@123",
            "new_password": "StrongPassword@123",
        },
    )
    assert response.status_code == 401


async def test_refresh_token_after_change_password(api_client, active_user):
    # Đăng nhập để lấy access_token và refresh_token ban đầu
    tokens = await get_auth_tokens(api_client, active_user)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    refresh_token = tokens["refresh_token"]

    # Thực hiện đổi mật khẩu
    change_res = await api_client.post(
        CHANGE_PASSWORD_URL,
        json={
            "current_password": active_user["password"],
            "new_password": "StrongPassword@123",
        },
        headers=headers,
    )
    assert change_res.status_code == 200

    # Dùng refresh_token cũ để lấy token mới sau khi đổi mật khẩu
    response = await api_client.post(
        REFRESH_URL,
        json={
            "refresh_token": refresh_token,
        },
    )
    assert response.status_code == 401


async def test_change_password_inactive_user(api_client, active_user, db_session):
    """Tài khoản bị vô hiệu hóa sau khi đã đăng nhập -> gọi POST /change-password trả về 403"""
    # Lấy token hợp lệ khi user còn đang active
    headers = await get_auth_headers(api_client, active_user)

    # Khóa tài khoản (is_active = False)
    await db_session.execute(
        update(User).where(User.email == active_user["email"]).values(is_active=False)
    )
    await db_session.commit()

    # Dùng token cũ để đổi mật khẩu -> bị chặn với mã 403
    response = await api_client.post(
        CHANGE_PASSWORD_URL,
        headers=headers,
        json={
            "current_password": active_user["password"],
            "new_password": "StrongPassword@123",
        },
    )

    assert response.status_code == 403
