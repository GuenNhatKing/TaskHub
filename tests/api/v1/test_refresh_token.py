from tests.api.v1.constants import LOGIN_URL, REFRESH_URL


async def test_refresh_token_success(api_client, active_user):
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

    # Refresh
    response = await api_client.post(
        REFRESH_URL,
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"


async def test_refresh_with_invalid_token(api_client):
    response = await api_client.post(
        REFRESH_URL,
        json={
            "refresh_token": "invalid.jwt.token",
        },
    )

    assert response.status_code == 401
