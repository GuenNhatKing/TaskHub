LOGIN_URL = "/api/v1/auth/login"


async def test_login_success(api_client, active_user):
    response = await api_client.post(
        LOGIN_URL,
        json={
            "email": active_user["email"],
            "password": active_user["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(api_client, active_user):
    response = await api_client.post(
        LOGIN_URL,
        json={
            "email": active_user["email"],
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401


async def test_login_nonexist_email(api_client):
    response = await api_client.post(
        LOGIN_URL,
        json={
            "email": "nonexist@mail.com",
            "password": "Password@123",
        },
    )

    assert response.status_code == 401


async def test_login_inactive_user(api_client, inactive_user):
    response = await api_client.post(
        LOGIN_URL,
        json={
            "email": inactive_user["email"],
            "password": inactive_user["password"],
        },
    )

    assert response.status_code == 403


async def test_login_invalid_email(api_client):
    response = await api_client.post(
        LOGIN_URL,
        json={
            "email": "invalid-email",
            "password": "Password@123",
        },
    )

    assert response.status_code == 422


async def test_login_missing_password(api_client):
    response = await api_client.post(
        LOGIN_URL,
        json={
            "email": "test@example.com",
        },
    )

    assert response.status_code == 422
