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


async def test_register_with_no_number_password(api_client):
    response = await api_client.post(
        REGISTER_URL,
        json={
            "full_name": "Nhat King",
            "email": "no-number-password@mail.com",
            "password": "password",
        },
    )

    assert response.status_code == 422


async def test_register_duplicate_email(api_client, active_user):
    response = await api_client.post(
        REGISTER_URL,
        json={
            "full_name": "Nhat King",
            "email": active_user["email"],
            "password": "Password123!",
        },
    )

    assert response.status_code == 409


async def test_register_with_password_exceeding_72_bytes(api_client):
    # Mật khẩu dài 73 ký tự (73 bytes > giới hạn 72 bytes của bcrypt)
    long_password = "Password" + "1" * 65
    response = await api_client.post(
        REGISTER_URL,
        json={
            "full_name": "Nhat King",
            "email": "long-password@mail.com",
            "password": long_password,
        },
    )

    assert response.status_code == 422
