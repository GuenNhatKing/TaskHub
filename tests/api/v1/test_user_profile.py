from tests.api.v1.constants import LOGIN_URL, PROFILES_URL


async def test_user_profile(api_client, active_user):
    # Đăng nhập để lấy access_token
    response = await api_client.post(
        LOGIN_URL,
        json={
            "email": active_user["email"],
            "password": active_user["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]
    assert token

    # Gửi request GET kèm JWT Token ở header
    response = await api_client.get(
        PROFILES_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    profile_data = response.json()
    assert profile_data["email"] == active_user["email"]


async def test_user_profile_invalid_token(api_client):
    response = await api_client.get(
        PROFILES_URL,
        headers={"Authorization": "Bearer token.khong.hop.le"},
    )

    assert response.status_code == 401


async def test_user_profile_missing_token(api_client):
    response = await api_client.get(PROFILES_URL)

    assert response.status_code == 401
