import uuid

from taskhub.core.enums import WorkspaceMemberRole
from tests.api.v1.constants import WORKSPACES_URL
from tests.api.v1.get_auth_credentials import get_auth_headers


async def _create_sample_workspace(
    api_client, headers: dict, name: str = "My Workspace"
) -> dict:
    """Helper tạo nhanh một workspace để dùng cho các test case khác"""
    response = await api_client.post(
        WORKSPACES_URL,
        headers=headers,
        json={"name": name},
    )
    assert response.status_code == 201
    return response.json()


async def test_create_workspace_success(api_client, active_user):
    """Tạo workspace thành công với dữ liệu hợp lệ"""
    headers = await get_auth_headers(api_client, active_user)
    payload = {"name": "Engineering Team"}

    response = await api_client.post(
        WORKSPACES_URL,
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["owner_id"] == str(active_user["id"])
    assert "id" in data
    assert "created_at" in data


async def test_create_workspace_missing_token(api_client):
    """Không đính kèm token -> trả về 401"""
    response = await api_client.post(
        WORKSPACES_URL,
        json={"name": "Unauthorized Workspace"},
    )
    assert response.status_code == 401


async def test_create_workspace_invalid_token(api_client):
    """Token sai định dạng hoặc hết hạn -> trả về 401"""
    response = await api_client.post(
        WORKSPACES_URL,
        headers={"Authorization": "Bearer invalid.token.here"},
        json={"name": "Unauthorized Workspace"},
    )
    assert response.status_code == 401


async def test_create_workspace_invalid_payload(api_client, active_user):
    """Thiếu trường bắt buộc (name) hoặc name không hợp lệ -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    for invalid_payload in [{}, {"name": ""}, {"name": "   "}]:
        response = await api_client.post(
            WORKSPACES_URL,
            headers=headers,
            json=invalid_payload,
        )
        assert response.status_code == 422


async def test_get_workspace_by_id_success(api_client, active_user):
    """Lấy thông tin workspace thành công theo ID"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers, "Design Team")
    ws_id = created_ws["id"]

    response = await api_client.get(
        f"{WORKSPACES_URL}/{ws_id}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ws_id
    assert data["name"] == "Design Team"
    assert data["owner_id"] == str(active_user["id"])
    assert "created_at" in data


async def test_get_workspace_by_id_missing_token(api_client, active_user):
    """Lấy thông tin workspace không có token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.get(f"{WORKSPACES_URL}/{created_ws['id']}")
    assert response.status_code == 401


async def test_get_workspace_by_id_forbidden_not_member(
    api_client, active_user, other_user
):
    """Người dùng không thuộc workspace cố tình xem thông tin -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, owner_headers)

    other_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.get(
        f"{WORKSPACES_URL}/{created_ws['id']}",
        headers=other_headers,
    )
    assert response.status_code == 403


async def test_get_workspace_by_id_not_found(api_client, active_user):
    """ID đúng định dạng UUID nhưng không tồn tại trong DB -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)
    random_uuid = uuid.uuid4()
    response = await api_client.get(
        f"{WORKSPACES_URL}/{random_uuid}",
        headers=headers,
    )

    assert response.status_code == 404


async def test_get_workspace_by_id_invalid_uuid(api_client, active_user):
    """ID không phải định dạng UUID -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    response = await api_client.get(
        f"{WORKSPACES_URL}/not-a-valid-uuid",
        headers=headers,
    )

    assert response.status_code == 422


async def test_delete_workspace_success(api_client, active_user):
    """Chủ sở hữu xóa workspace thành công -> trả về 204"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)
    ws_id = created_ws["id"]

    response = await api_client.delete(
        f"{WORKSPACES_URL}/{ws_id}",
        headers=headers,
    )
    assert response.status_code == 204

    # Kiểm tra lại xem workspace đã thực sự bị xóa chưa
    get_res = await api_client.get(
        f"{WORKSPACES_URL}/{ws_id}",
        headers=headers,
    )
    assert get_res.status_code == 404


async def test_delete_workspace_missing_token(api_client, active_user):
    """Xóa workspace không có token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.delete(f"{WORKSPACES_URL}/{created_ws['id']}")
    assert response.status_code == 401


async def test_delete_workspace_forbidden_not_owner(
    api_client, active_user, other_user
):
    """Người dùng khác (không phải owner) cố tình xóa workspace -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, owner_headers)

    other_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.delete(
        f"{WORKSPACES_URL}/{created_ws['id']}",
        headers=other_headers,
    )
    assert response.status_code == 403


async def test_delete_workspace_not_found(api_client, active_user):
    """Xóa workspace không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)
    response = await api_client.delete(
        f"{WORKSPACES_URL}/{uuid.uuid4()}",
        headers=headers,
    )
    assert response.status_code == 404


async def test_add_workspace_member_success(api_client, active_user, other_user):
    """Thêm thành viên mới vào workspace thành công -> trả về 201"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)
    ws_id = created_ws["id"]

    payload = {
        "user_id": str(other_user["id"]),
        "role": WorkspaceMemberRole.VIEWER,
    }

    response = await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/members",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["workspace_id"] == ws_id
    assert data["user_id"] == payload["user_id"]
    assert data["role"] == payload["role"]


async def test_add_workspace_member_duplicate(api_client, active_user, other_user):
    """Thêm thành viên đã tồn tại trong workspace -> trả về 409"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)
    ws_id = created_ws["id"]

    payload = {
        "user_id": str(other_user["id"]),
        "role": WorkspaceMemberRole.VIEWER,
    }

    res1 = await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/members", headers=headers, json=payload
    )
    assert res1.status_code == 201

    res2 = await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/members", headers=headers, json=payload
    )
    assert res2.status_code == 409


async def test_add_workspace_member_invalid_role_or_uuid(api_client, active_user):
    """Gửi role không nằm trong WorkspaceMemberRole hoặc user_id sai định dạng -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)
    ws_id = created_ws["id"]

    # Role không hợp lệ
    res_bad_role = await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/members",
        headers=headers,
        json={"user_id": str(uuid.uuid4()), "role": "INVALID_ROLE"},
    )
    assert res_bad_role.status_code == 422

    # user_id không phải UUID
    res_bad_uuid = await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/members",
        headers=headers,
        json={"user_id": "not-a-uuid", "role": WorkspaceMemberRole.VIEWER.value},
    )
    assert res_bad_uuid.status_code == 422


async def test_add_workspace_member_forbidden(api_client, active_user, other_user):
    """Người không có quyền (không phải owner) thêm thành viên -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, owner_headers)
    ws_id = created_ws["id"]

    other_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/members",
        headers=other_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER,
        },
    )
    assert response.status_code == 403


async def test_add_workspace_member_missing_token(api_client, active_user, other_user):
    """Thiếu token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.post(
        f"{WORKSPACES_URL}/{created_ws['id']}/members",
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER.value,
        },
    )
    assert response.status_code == 401


async def test_remove_workspace_member_success(api_client, active_user, other_user):
    """Xóa thành viên khỏi workspace thành công -> trả về 204"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)
    ws_id = created_ws["id"]
    member_id = str(other_user["id"])

    add_res = await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/members",
        headers=headers,
        json={"user_id": member_id, "role": WorkspaceMemberRole.VIEWER},
    )
    assert add_res.status_code == 201

    del_res = await api_client.delete(
        f"{WORKSPACES_URL}/{ws_id}/members/{member_id}",
        headers=headers,
    )
    assert del_res.status_code == 204


async def test_remove_workspace_member_not_found(api_client, active_user):
    """Xóa user không nằm trong workspace -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.delete(
        f"{WORKSPACES_URL}/{created_ws['id']}/members/{uuid.uuid4()}",
        headers=headers,
    )
    assert response.status_code == 404


async def test_remove_workspace_member_forbidden(api_client, active_user, other_user):
    """User không có quyền cố tình xóa thành viên -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, owner_headers)
    ws_id = created_ws["id"]

    other_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.delete(
        f"{WORKSPACES_URL}/{ws_id}/members/{active_user['id']}",
        headers=other_headers,
    )
    assert response.status_code == 403


async def test_remove_workspace_member_missing_token(
    api_client, active_user, other_user
):
    """Xóa thành viên khỏi workspace không có token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.delete(
        f"{WORKSPACES_URL}/{created_ws['id']}/members/{other_user['id']}",
    )
    assert response.status_code == 401


async def test_update_workspace_success(api_client, active_user):
    """Owner cập nhật tên workspace thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers, "Old Name")
    ws_id = created_ws["id"]

    payload = {"name": "New Workspace Name"}
    response = await api_client.patch(
        f"{WORKSPACES_URL}/{ws_id}",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ws_id
    assert data["name"] == payload["name"]
    assert data["owner_id"] == str(active_user["id"])


async def test_update_workspace_empty_json_ignored(api_client, active_user):
    """Gửi JSON rỗng {} -> trả về 200 và giữ nguyên dữ liệu cũ"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers, "Original Name")
    ws_id = created_ws["id"]

    response = await api_client.patch(
        f"{WORKSPACES_URL}/{ws_id}",
        headers=headers,
        json={},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Original Name"


async def test_update_workspace_null_values_ignored(api_client, active_user):
    """Gửi giá trị null -> giữ nguyên dữ liệu cũ"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers, "Original Name")
    ws_id = created_ws["id"]

    response = await api_client.patch(
        f"{WORKSPACES_URL}/{ws_id}",
        headers=headers,
        json={"name": None},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Original Name"


async def test_update_workspace_no_body(api_client, active_user):
    """Không đính kèm body -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.patch(
        f"{WORKSPACES_URL}/{created_ws['id']}",
        headers=headers,
    )
    assert response.status_code == 422


async def test_update_workspace_invalid_name(api_client, active_user):
    """Gửi name là chuỗi rỗng hoặc toàn khoảng trắng -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)
    ws_id = created_ws["id"]

    for invalid_name in ["", "   "]:
        response = await api_client.patch(
            f"{WORKSPACES_URL}/{ws_id}",
            headers=headers,
            json={"name": invalid_name},
        )
        assert response.status_code == 422


async def test_update_workspace_missing_token(api_client, active_user):
    """Thiếu token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.patch(
        f"{WORKSPACES_URL}/{created_ws['id']}",
        json={"name": "Hacker Name"},
    )
    assert response.status_code == 401


async def test_update_workspace_invalid_token(api_client, active_user):
    """Token không hợp lệ -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.patch(
        f"{WORKSPACES_URL}/{created_ws['id']}",
        headers={"Authorization": "Bearer token.khong.hop.le"},
        json={"name": "Hacker Name"},
    )
    assert response.status_code == 401


async def test_update_workspace_forbidden_not_owner(
    api_client, active_user, other_user
):
    """Người dùng khác (không phải owner) cố tình cập nhật workspace -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, owner_headers)

    other_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.patch(
        f"{WORKSPACES_URL}/{created_ws['id']}",
        headers=other_headers,
        json={"name": "New Workspace Name"},
    )
    assert response.status_code == 403


async def test_update_workspace_not_found(api_client, active_user):
    """Cập nhật workspace không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        f"{WORKSPACES_URL}/{uuid.uuid4()}",
        headers=headers,
        json={"name": "Ghost Workspace"},
    )
    assert response.status_code == 404


async def test_update_workspace_invalid_uuid(api_client, active_user):
    """ID trên URL không đúng định dạng UUID -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        f"{WORKSPACES_URL}/not-a-valid-uuid",
        headers=headers,
        json={"name": "Valid Name"},
    )
    assert response.status_code == 422


async def test_remove_workspace_member_self_bad_request(api_client, active_user):
    """Owner tự xóa chính mình khỏi workspace -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    created_ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.delete(
        f"{WORKSPACES_URL}/{created_ws['id']}/members/{active_user['id']}",
        headers=headers,
    )
    assert response.status_code == 400
