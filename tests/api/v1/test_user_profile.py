from sqlalchemy import update

from taskhub.models.user import User
from tests.api.v1.constants import PROFILES_URL
from tests.api.v1.get_auth_credentials import get_auth_headers


async def test_user_profile(api_client, active_user):
    headers = await get_auth_headers(api_client, active_user)

    # Gửi request GET kèm JWT Token ở header
    response = await api_client.get(
        PROFILES_URL,
        headers=headers,
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


async def test_patch_user_profile_partial_full_name(api_client, active_user):
    """Chỉ cập nhật full_name, email được giữ nguyên"""
    headers = await get_auth_headers(api_client, active_user)
    new_full_name = "Fullname Updated"

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json={"full_name": new_full_name},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == new_full_name
    assert data["email"] == active_user["email"]


async def test_patch_user_profile_all_fields(api_client, active_user):
    """Cập nhật cả email và full_name cùng lúc"""
    headers = await get_auth_headers(api_client, active_user)
    payload = {
        "email": "new.email@mail.com",
        "full_name": "Fullname Updated",
        "current_password": active_user["password"],
    }

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]


async def test_patch_user_profile_email_missing_current_password(
    api_client, active_user
):
    """Đổi email nhưng không gửi kèm current_password -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    payload = {
        "email": "new.email@mail.com",
        "full_name": "Fullname Updated",
    }

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json=payload,
    )

    assert response.status_code == 400


async def test_patch_user_profile_email_wrong_current_password(api_client, active_user):
    """Đổi email nhưng nhập sai current_password -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    payload = {
        "email": "new.email@mail.com",
        "full_name": "Fullname Updated",
        "current_password": "wrongPass@123",
    }

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json=payload,
    )

    assert response.status_code == 400


async def test_patch_user_profile_empty_json(api_client, active_user):
    """Gửi JSON rỗng {} -> trả về 200 và giữ nguyên dữ liệu cũ"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json={},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == active_user["full_name"]
    assert data["email"] == active_user["email"]


async def test_patch_user_profile_no_body(api_client, active_user):
    """Không đính kèm body -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
    )

    assert response.status_code == 422


async def test_patch_user_profile_empty_payload_ignored(api_client, active_user):
    """Bỏ trống các trường (gửi JSON rỗng {}) -> trả về 200 và giữ nguyên dữ liệu cũ"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json={},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == active_user["full_name"]
    assert data["email"] == active_user["email"]


async def test_patch_user_profile_null_required_fields(api_client, active_user):
    """Truyền null cho các trường không cho phép null (email, full_name) -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    null_payloads = [
        {"email": None},
        {"full_name": None},
    ]

    for payload in null_payloads:
        response = await api_client.patch(
            PROFILES_URL,
            headers=headers,
            json=payload,
        )
        assert response.status_code == 422


async def test_patch_user_profile_invalid_email(api_client, active_user):
    """Gửi email sai định dạng -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json={"email": "email-khong-hop-le"},
    )

    assert response.status_code == 422


async def test_patch_user_profile_invalid_token(api_client):
    """Token sai -> trả về 401"""
    response = await api_client.patch(
        PROFILES_URL,
        headers={"Authorization": "Bearer token.khong.hop.le"},
        json={"full_name": "Hacker"},
    )

    assert response.status_code == 401


async def test_patch_user_profile_missing_token(api_client):
    """Thiếu token -> trả về 401"""
    response = await api_client.patch(
        PROFILES_URL,
        json={"full_name": "Hacker"},
    )

    assert response.status_code == 401


async def test_patch_user_profile_duplicate_email(
    api_client, active_user, inactive_user
):
    """Cập nhật email trùng với người dùng khác -> trả về 409"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json={"email": inactive_user["email"]},
    )

    assert response.status_code == 409


async def test_patch_user_profile_empty_full_name(api_client, active_user):
    """Gửi full_name là chuỗi rỗng hoặc toàn khoảng trắng -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    for invalid_name in ["", "   "]:
        response = await api_client.patch(
            PROFILES_URL,
            headers=headers,
            json={"full_name": invalid_name},
        )
        assert response.status_code == 422


async def test_patch_user_profile_extra_fields_rejected(api_client, active_user):
    """Gửi kèm trường lạ không có trong schema"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json={"full_name": "Fullname Updated", "is_active": False, "hacker": True},
    )

    assert response.status_code == 422


async def test_patch_user_profile_duplicate_email_case_insensitive(
    api_client, active_user, inactive_user
):
    """Cập nhật email trùng với người dùng khác nhưng khác chữ hoa/thường -> trả về 409"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json={
            "email": inactive_user["email"].upper(),
            "current_password": active_user["password"],
        },
    )

    assert response.status_code == 409


async def test_patch_user_profile_same_email(api_client, active_user):
    """Cập nhật email hiện tại nhưng mà viết hoa -> không báo trùng, trả về 200"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json={
            "email": active_user["email"].upper(),
            "current_password": active_user["password"],
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == active_user["email"].lower()


async def test_patch_user_profile_email_and_login_flow(api_client, active_user):
    """Đổi email thành công -> đăng nhập bằng email mới được (200), email cũ bị từ chối (401)"""
    headers = await get_auth_headers(api_client, active_user)
    old_email = active_user["email"]
    new_email = "updated.login@mail.com"
    password = active_user["password"]

    # Đổi sang email mới
    patch_res = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json={
            "email": new_email,
            "current_password": password,
        },
    )
    assert patch_res.status_code == 200

    # Đăng nhập bằng email mới -> thành công (200)
    login_new_res = await api_client.post(
        "/api/v1/auth/login",
        json={"email": new_email, "password": password},
    )
    assert login_new_res.status_code == 200

    # Đăng nhập bằng email cũ -> thất bại (401)
    login_old_res = await api_client.post(
        "/api/v1/auth/login",
        json={"email": old_email, "password": password},
    )
    assert login_old_res.status_code == 401


async def test_patch_user_profile_inactive_user(api_client, active_user, db_session):
    """Tài khoản bị vô hiệu hóa sau khi đã đăng nhập -> gọi PATCH /me trả về 403"""
    # Lấy token hợp lệ khi user còn đang active
    headers = await get_auth_headers(api_client, active_user)

    # Khóa tài khoản (is_active = False)
    await db_session.execute(
        update(User).where(User.email == active_user["email"]).values(is_active=False)
    )
    await db_session.commit()

    # Dùng token cũ để cập nhật profile -> bị chặn với mã 403
    response = await api_client.patch(
        PROFILES_URL,
        headers=headers,
        json={"full_name": "Inactive User Update"},
    )

    assert response.status_code == 403
