from tests.api.v1.constants import REGISTER_URL


async def test_register_success(api_client, active_user):
    response = await api_client.post(
        REGISTER_URL,
        json={
            "full_name": "Nhat King",
            "email": "success@mail.com",
            "password": active_user["password"],
        },
    )

    assert response.status_code == 201


async def test_register_with_invalid_email(api_client, active_user):
    response = await api_client.post(
        REGISTER_URL,
        json={
            "full_name": "Nhat King",
            "email": "invalid-email",
            "password": active_user["password"],
        },
    )

    assert response.status_code == 422


async def test_register_with_no_number_password(api_client, active_user):
    response = await api_client.post(
        REGISTER_URL,
        json={
            "full_name": "Nhat King",
            "email": "no-number-password@mail.com",
            "password": "password",
        },
    )

    assert response.status_code == 422
