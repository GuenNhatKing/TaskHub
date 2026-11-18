from tests.api.v1.constants import LOGIN_URL, LOGOUT_URL, REFRESH_URL


async def test_logout_success(api_client, active_user):
    # Login
    login_response = await api_client.post(
        LOGIN_URL,
        json={
            "email": active_user["email"],
            "password": active_user["password"],
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    # Logout
    response = await api_client.post(
        LOGOUT_URL,
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 204


async def test_refresh_after_logout(api_client, active_user):
    # Login
    login_response = await api_client.post(
        LOGIN_URL,
        json={
            "email": active_user["email"],
            "password": active_user["password"],
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    # Logout
    logout_response = await api_client.post(
        LOGOUT_URL,
        json={"refresh_token": refresh_token},
    )

    assert logout_response.status_code == 204

    # Refresh revoked token
    refresh_response = await api_client.post(
        REFRESH_URL,
        json={"refresh_token": refresh_token},
    )

    assert refresh_response.status_code == 401


async def test_logout_repeatedly(api_client, active_user):
    login_response = await api_client.post(
        LOGIN_URL,
        json={
            "email": active_user["email"],
            "password": active_user["password"],
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    response = await api_client.post(
        LOGOUT_URL,
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 204

    # Lần 2 nhận về 401
    response = await api_client.post(
        LOGOUT_URL,
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 401


async def test_logout_invalid_token(api_client):
    response = await api_client.post(
        LOGOUT_URL,
        json={
            "refresh_token": "invalid.jwt.token",
        },
    )

    assert response.status_code == 401


async def test_refresh_token_reuse_detection(api_client, active_user):
    login_response = await api_client.post(
        LOGIN_URL,
        json={
            "email": active_user["email"],
            "password": active_user["password"],
        },
    )
    assert login_response.status_code == 200
    stolen_refresh_token = login_response.json()["refresh_token"]

    # Kẻ gian đánh cắp token này và dùng để refresh trước
    attacker_refresh_res = await api_client.post(
        REFRESH_URL,
        json={"refresh_token": stolen_refresh_token},
    )
    assert attacker_refresh_res.status_code == 200
    attacker_new_refresh_token = attacker_refresh_res.json()["refresh_token"]

    # Chủ tài khoản thật dùng lại token cũ để refresh sau
    victim_refresh_res = await api_client.post(
        REFRESH_URL,
        json={"refresh_token": stolen_refresh_token},
    )
    # Hệ thống phải từ chối token đã dùng và kích hoạt khóa toàn bộ group
    assert victim_refresh_res.status_code == 401

    # Token mới của kẻ gian ở bước 2 cũng phải bị vô hiệu hóa
    attacker_next_res = await api_client.post(
        REFRESH_URL,
        json={"refresh_token": attacker_new_refresh_token},
    )
    assert attacker_next_res.status_code == 401
