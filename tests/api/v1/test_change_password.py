from tests.api.v1.constants import CHANGE_PASSWORD_URL, LOGIN_URL


async def _get_auth_headers(api_client, user_credentials: dict) -> dict:
    response = await api_client.post(
        LOGIN_URL,
        json={
            "email": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token
    return {"Authorization": f"Bearer {token}"}


async def test_change_password_success(api_client, active_user):
    headers = await _get_auth_headers(api_client, active_user)
    new_password = "StrongPassword@123"

    response = await api_client.post(
        CHANGE_PASSWORD_URL,
        json={
            "old_password": active_user["password"],
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


async def test_change_password_wrong_old_password(api_client, active_user):
    headers = await _get_auth_headers(api_client, active_user)

    response = await api_client.post(
        CHANGE_PASSWORD_URL,
        json={
            "old_password": "WrongPassword@123",
            "new_password": "StrongPassword@123",
        },
        headers=headers,
    )
    assert response.status_code == 401


async def test_change_password_same_as_old(api_client, active_user):
    headers = await _get_auth_headers(api_client, active_user)

    response = await api_client.post(
        CHANGE_PASSWORD_URL,
        json={
            "old_password": active_user["password"],
            "new_password": active_user["password"],
        },
        headers=headers,
    )
    assert response.status_code == 400


async def test_change_password_weak_new_password(api_client, active_user):
    headers = await _get_auth_headers(api_client, active_user)

    response = await api_client.post(
        CHANGE_PASSWORD_URL,
        json={
            "old_password": active_user["password"],
            "new_password": "12345678",
        },
        headers=headers,
    )
    assert response.status_code == 422


async def test_change_password_unauthenticated(api_client):
    response = await api_client.post(
        CHANGE_PASSWORD_URL,
        json={
            "old_password": "SomePassword@123",
            "new_password": "StrongPassword@123",
        },
    )
    assert response.status_code == 401
