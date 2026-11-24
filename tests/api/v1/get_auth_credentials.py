from tests.api.v1.constants import LOGIN_URL


async def get_auth_tokens(api_client, user_credentials: dict) -> dict:
    response = await api_client.post(
        LOGIN_URL,
        json={
            "email": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"]
    return data


async def get_auth_headers(api_client, user_credentials: dict) -> dict:
    token = await get_auth_tokens(api_client, user_credentials)
    access_token = token["access_token"]
    assert access_token
    return {"Authorization": f"Bearer {access_token}"}
