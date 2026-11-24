import uuid

from taskhub.core.enums import ProjectStatus, WorkspaceMemberRole
from tests.api.v1.constants import PROJECTS_URL, WORKSPACES_URL
from tests.api.v1.get_auth_credentials import get_auth_headers


async def _create_sample_workspace(
    api_client, headers: dict, name: str = "My Workspace"
) -> dict:
    response = await api_client.post(
        WORKSPACES_URL,
        headers=headers,
        json={"name": name},
    )
    assert response.status_code == 201
    return response.json()


async def _create_sample_project(
    api_client,
    headers: dict,
    workspace_id: str,
    name: str = "Sample Project",
    description: str = "Project description",
) -> dict:
    response = await api_client.post(
        f"{WORKSPACES_URL}/{workspace_id}/projects",
        headers=headers,
        json={"name": name, "description": description},
    )
    assert response.status_code == 201
    return response.json()


async def test_create_project_success(api_client, active_user):
    """Tạo project thành công với dữ liệu hợp lệ -> trả về 201"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    ws_id = ws["id"]

    payload = {
        "name": "Engineering Project",
        "description": "Core backend development",
    }

    response = await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/projects",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["workspace_id"] == ws_id
    assert "id" in data
    assert "status" in data
    assert "created_at" in data


async def test_create_project_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/projects",
        json={"name": "Unauthorized Project"},
    )
    assert response.status_code == 401


async def test_create_project_invalid_token(api_client, active_user):
    """Token sai định dạng hoặc hết hạn -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/projects",
        headers={"Authorization": "Bearer invalid.token.here"},
        json={"name": "Unauthorized Project"},
    )
    assert response.status_code == 401


async def test_create_project_invalid_payload(api_client, active_user):
    """Thiếu trường bắt buộc hoặc không hợp lệ -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    ws_id = ws["id"]

    for invalid_payload in [{}, {"name": ""}, {"name": "   "}]:
        response = await api_client.post(
            f"{WORKSPACES_URL}/{ws_id}/projects",
            headers=headers,
            json=invalid_payload,
        )
        assert response.status_code == 422


async def test_create_project_invalid_workspace_uuid(api_client, active_user):
    """workspace_id trên URL không đúng định dạng UUID -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.post(
        f"{WORKSPACES_URL}/not-a-valid-uuid/projects",
        headers=headers,
        json={"name": "Valid Project"},
    )
    assert response.status_code == 422


async def test_create_project_workspace_not_found(api_client, active_user):
    """Tạo project trong workspace không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.post(
        f"{WORKSPACES_URL}/{uuid.uuid4()}/projects",
        headers=headers,
        json={"name": "Ghost Project"},
    )
    assert response.status_code == 404


async def test_create_project_forbidden_not_member(api_client, active_user, other_user):
    """Người dùng không thuộc workspace cố tình tạo project -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)

    other_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/projects",
        headers=other_headers,
        json={"name": "Forbidden Project"},
    )
    assert response.status_code == 403


async def test_create_project_forbidden_viewer(api_client, active_user, other_user):
    """Thành viên có role VIEWER cố tình tạo project -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    ws_id = ws["id"]

    await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/projects",
        headers=viewer_headers,
        json={"name": "Viewer Project"},
    )
    assert response.status_code == 403


async def test_get_projects_success(api_client, active_user):
    """Lấy danh sách project trong workspace thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    ws_id = ws["id"]

    p1 = await _create_sample_project(api_client, headers, ws_id, "Project 1")
    p2 = await _create_sample_project(api_client, headers, ws_id, "Project 2")

    response = await api_client.get(
        f"{WORKSPACES_URL}/{ws_id}/projects",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1
    assert {item["id"] for item in data["items"]} == {p1["id"], p2["id"]}


async def test_get_projects_empty(api_client, active_user):
    """Workspace chưa có project nào -> trả về mảng rỗng [] và status 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.get(
        f"{WORKSPACES_URL}/{ws['id']}/projects",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["total_pages"] == 0


async def test_get_projects_filter_by_status(api_client, active_user):
    """Lọc danh sách project theo query param status -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    ws_id = ws["id"]

    await _create_sample_project(api_client, headers, ws_id, "Active Project")

    res_active = await api_client.get(
        f"{WORKSPACES_URL}/{ws_id}/projects",
        headers=headers,
        params={"status": ProjectStatus.ACTIVE.value},
    )
    assert res_active.status_code == 200
    assert len(res_active.json()["items"]) == 1

    res_archived = await api_client.get(
        f"{WORKSPACES_URL}/{ws_id}/projects",
        headers=headers,
        params={"status": ProjectStatus.ARCHIVED.value},
    )
    assert res_archived.status_code == 200
    assert res_archived.json()["items"] == []


async def test_get_projects_invalid_status_param(api_client, active_user):
    """Truyền query param status không hợp lệ -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.get(
        f"{WORKSPACES_URL}/{ws['id']}/projects",
        headers=headers,
        params={"status": "INVALID_STATUS"},
    )
    assert response.status_code == 422


async def test_get_projects_viewer_allowed(api_client, active_user, other_user):
    """Thành viên có role VIEWER được phép xem danh sách project -> trả về 200"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    ws_id = ws["id"]
    await _create_sample_project(api_client, owner_headers, ws_id, "Shared Project")

    await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.get(
        f"{WORKSPACES_URL}/{ws_id}/projects",
        headers=viewer_headers,
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


async def test_get_projects_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.get(f"{WORKSPACES_URL}/{ws['id']}/projects")
    assert response.status_code == 401


async def test_get_projects_invalid_token(api_client, active_user):
    """Token không hợp lệ -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)

    response = await api_client.get(
        f"{WORKSPACES_URL}/{ws['id']}/projects",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


async def test_get_projects_forbidden_not_member(api_client, active_user, other_user):
    """Người dùng không thuộc workspace cố tình xem danh sách project -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)

    other_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.get(
        f"{WORKSPACES_URL}/{ws['id']}/projects",
        headers=other_headers,
    )
    assert response.status_code == 403


async def test_get_projects_workspace_not_found(api_client, active_user):
    """Lấy danh sách project của workspace không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.get(
        f"{WORKSPACES_URL}/{uuid.uuid4()}/projects",
        headers=headers,
    )
    assert response.status_code == 404


async def test_get_projects_invalid_workspace_uuid(api_client, active_user):
    """workspace_id trên URL không đúng định dạng UUID -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.get(
        f"{WORKSPACES_URL}/not-a-valid-uuid/projects",
        headers=headers,
    )
    assert response.status_code == 422


async def test_get_project_detail_success(api_client, active_user):
    """Lấy chi tiết project thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(
        api_client, headers, ws["id"], "Detail Project", "Detailed info"
    )
    project_id = project["id"]

    response = await api_client.get(
        f"{PROJECTS_URL}/{project_id}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Detail Project"
    assert data["description"] == "Detailed info"
    assert data["workspace_id"] == ws["id"]


async def test_get_project_detail_viewer_allowed(api_client, active_user, other_user):
    """Thành viên có role VIEWER được phép xem chi tiết project -> trả về 200"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.get(
        f"{PROJECTS_URL}/{project['id']}",
        headers=viewer_headers,
    )
    assert response.status_code == 200


async def test_get_project_detail_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.get(f"{PROJECTS_URL}/{project['id']}")
    assert response.status_code == 401


async def test_get_project_detail_forbidden_not_member(
    api_client, active_user, other_user
):
    """Người dùng không thuộc workspace cố tình xem chi tiết project -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    other_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.get(
        f"{PROJECTS_URL}/{project['id']}",
        headers=other_headers,
    )
    assert response.status_code == 403


async def test_get_project_detail_not_found(api_client, active_user):
    """Project không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.get(
        f"{PROJECTS_URL}/{uuid.uuid4()}",
        headers=headers,
    )
    assert response.status_code == 404


async def test_get_project_detail_invalid_uuid(api_client, active_user):
    """project_id trên URL không đúng định dạng UUID -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.get(
        f"{PROJECTS_URL}/not-a-valid-uuid",
        headers=headers,
    )
    assert response.status_code == 422


async def test_update_project_success(api_client, active_user):
    """Cập nhật thông tin project thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(
        api_client, headers, ws["id"], "Old Name", "Old Description"
    )
    project_id = project["id"]

    payload = {
        "name": "Updated Project Name",
        "description": "Updated Description",
    }
    response = await api_client.patch(
        f"{PROJECTS_URL}/{project_id}",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]


async def test_update_project_empty_or_null_ignored(api_client, active_user):
    """Gửi JSON rỗng {} hoặc giá trị null -> trả về 200 và giữ nguyên dữ liệu cũ"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(
        api_client, headers, ws["id"], "Original Name", "Original Desc"
    )
    project_id = project["id"]

    res_empty = await api_client.patch(
        f"{PROJECTS_URL}/{project_id}",
        headers=headers,
        json={},
    )
    assert res_empty.status_code == 200
    assert res_empty.json()["name"] == "Original Name"

    res_null = await api_client.patch(
        f"{PROJECTS_URL}/{project_id}",
        headers=headers,
        json={"name": None, "description": None},
    )
    assert res_null.status_code == 200
    assert res_null.json()["name"] == "Original Name"
    assert res_null.json()["description"] == "Original Desc"


async def test_update_project_invalid_name(api_client, active_user):
    """Gửi name là chuỗi rỗng hoặc toàn khoảng trắng -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    for invalid_name in ["", "   "]:
        response = await api_client.patch(
            f"{PROJECTS_URL}/{project['id']}",
            headers=headers,
            json={"name": invalid_name},
        )
        assert response.status_code == 422


async def test_update_project_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.patch(
        f"{PROJECTS_URL}/{project['id']}",
        json={"name": "Unauthorized Update"},
    )
    assert response.status_code == 401


async def test_update_project_forbidden_viewer(api_client, active_user, other_user):
    """Thành viên có role VIEWER cố tình cập nhật project -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.patch(
        f"{PROJECTS_URL}/{project['id']}",
        headers=viewer_headers,
        json={"name": "Viewer Hack"},
    )
    assert response.status_code == 403


async def test_update_project_not_found(api_client, active_user):
    """Cập nhật project không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        f"{PROJECTS_URL}/{uuid.uuid4()}",
        headers=headers,
        json={"name": "Ghost Project"},
    )
    assert response.status_code == 404


async def test_update_project_invalid_uuid(api_client, active_user):
    """project_id trên URL không đúng định dạng UUID -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        f"{PROJECTS_URL}/not-a-valid-uuid",
        headers=headers,
        json={"name": "Valid Name"},
    )
    assert response.status_code == 422


async def test_delete_project_success(api_client, active_user):
    """Xóa project thành công -> trả về 204"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    project_id = project["id"]

    response = await api_client.delete(
        f"{PROJECTS_URL}/{project_id}",
        headers=headers,
    )
    assert response.status_code == 204

    get_res = await api_client.get(
        f"{PROJECTS_URL}/{project_id}",
        headers=headers,
    )
    assert get_res.status_code == 404


async def test_delete_project_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.delete(f"{PROJECTS_URL}/{project['id']}")
    assert response.status_code == 401


async def test_delete_project_forbidden_viewer(api_client, active_user, other_user):
    """Thành viên có role VIEWER cố tình xóa project -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.delete(
        f"{PROJECTS_URL}/{project['id']}",
        headers=viewer_headers,
    )
    assert response.status_code == 403


async def test_delete_project_not_found(api_client, active_user):
    """Xóa project không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.delete(
        f"{PROJECTS_URL}/{uuid.uuid4()}",
        headers=headers,
    )
    assert response.status_code == 404


async def test_delete_project_invalid_uuid(api_client, active_user):
    """project_id trên URL không đúng định dạng UUID -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.delete(
        f"{PROJECTS_URL}/not-a-valid-uuid",
        headers=headers,
    )
    assert response.status_code == 422


async def test_archive_project_success(api_client, active_user):
    """Archive project đang active thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    project_id = project["id"]

    response = await api_client.post(
        f"{PROJECTS_URL}/{project_id}/archive",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["status"] == ProjectStatus.ARCHIVED


async def test_archive_project_already_archived(api_client, active_user):
    """Archive một project đã ở trạng thái archived -> trả về 400 hoặc 409"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    project_id = project["id"]

    res1 = await api_client.post(
        f"{PROJECTS_URL}/{project_id}/archive",
        headers=headers,
    )
    assert res1.status_code == 200

    res2 = await api_client.post(
        f"{PROJECTS_URL}/{project_id}/archive",
        headers=headers,
    )
    assert res2.status_code == 200


async def test_archive_project_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.post(f"{PROJECTS_URL}/{project['id']}/archive")
    assert response.status_code == 401


async def test_archive_project_forbidden_viewer(api_client, active_user, other_user):
    """Thành viên có role VIEWER cố tình archive project -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=viewer_headers,
    )
    assert response.status_code == 403


async def test_archive_project_not_found(api_client, active_user):
    """Archive project không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.post(
        f"{PROJECTS_URL}/{uuid.uuid4()}/archive",
        headers=headers,
    )
    assert response.status_code == 404


async def test_unarchive_project_success(api_client, active_user):
    """Unarchive project đang archived thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    project_id = project["id"]

    archive_res = await api_client.post(
        f"{PROJECTS_URL}/{project_id}/archive",
        headers=headers,
    )
    assert archive_res.status_code == 200

    response = await api_client.post(
        f"{PROJECTS_URL}/{project_id}/unarchive",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["status"] == ProjectStatus.ACTIVE


async def test_unarchive_project_already_active(api_client, active_user):
    """Unarchive một project đang active -> trả về 400 hoặc 409"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/unarchive",
        headers=headers,
    )
    assert response.status_code == 200


async def test_unarchive_project_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.post(f"{PROJECTS_URL}/{project['id']}/unarchive")
    assert response.status_code == 401


async def test_unarchive_project_forbidden_viewer(api_client, active_user, other_user):
    """Thành viên có role VIEWER cố tình unarchive project -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=owner_headers,
    )

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/unarchive",
        headers=viewer_headers,
    )
    assert response.status_code == 403


async def test_unarchive_project_not_found(api_client, active_user):
    """Unarchive project không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.post(
        f"{PROJECTS_URL}/{uuid.uuid4()}/unarchive",
        headers=headers,
    )
    assert response.status_code == 404


async def test_create_project_only_name_success(api_client, active_user):
    """Tạo project thành công khi chỉ truyền trường name (không có description) -> trả về 201"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    ws_id = ws["id"]

    payload = {"name": "Minimal Project"}

    response = await api_client.post(
        f"{WORKSPACES_URL}/{ws_id}/projects",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] is None
    assert data["workspace_id"] == ws_id
    assert "id" in data
    assert "status" in data
    assert "created_at" in data
