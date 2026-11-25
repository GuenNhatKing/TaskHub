import uuid

from taskhub.core.enums import LabelColor, WorkspaceMemberRole
from tests.api.v1.constants import (
    LABELS_URL,
    PROJECTS_URL,
    TASKS_URL,
    WORKSPACES_URL,
)
from tests.api.v1.get_auth_credentials import get_auth_headers
from tests.api.v1.test_project import _create_sample_project
from tests.api.v1.test_task import _create_sample_task
from tests.api.v1.test_workspace import _create_sample_workspace


async def _create_sample_label(
    api_client,
    headers: dict,
    project_id: str,
    name: str = "Bug",
    color: LabelColor = LabelColor.RED,
) -> dict:
    response = await api_client.post(
        f"{PROJECTS_URL}/{project_id}/labels",
        headers=headers,
        json={"name": name, "color": color.value},
    )
    assert response.status_code == 201
    return response.json()


async def test_create_label_success(api_client, active_user):
    """Tạo label mới trong project thành công -> trả về 201"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    payload = {
        "name": "Feature",
        "color": LabelColor.GREEN.value,
    }
    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/labels",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["color"] == LabelColor.GREEN
    assert data["project_id"] == project["id"]
    assert "id" in data


async def test_create_label_default_color_success(api_client, active_user):
    """Tạo label không truyền color -> mặc định sử dụng LabelColor.BLUE và trả về 201"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/labels",
        headers=headers,
        json={"name": "Documentation"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Documentation"
    assert data["color"] == LabelColor.BLUE


async def test_create_label_editor_allowed(api_client, active_user, other_user):
    """Thành viên có role EDITOR được phép tạo label -> trả về 201"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.EDITOR.value,
        },
    )

    editor_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/labels",
        headers=editor_headers,
        json={"name": "Enhancement"},
    )
    assert response.status_code == 201


async def test_create_label_duplicate_name_conflict(api_client, active_user):
    """Tạo label trùng tên (không phân biệt hoa thường) trong cùng project -> trả về 409"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    await _create_sample_label(api_client, headers, project["id"], name="Urgent")

    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/labels",
        headers=headers,
        json={"name": "urgent"},
    )
    assert response.status_code == 409


async def test_create_label_same_name_different_projects_allowed(
    api_client, active_user
):
    """Hai project khác nhau có thể tạo label trùng tên -> trả về 201"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    p1 = await _create_sample_project(api_client, headers, ws["id"], "Project 1")
    p2 = await _create_sample_project(api_client, headers, ws["id"], "Project 2")

    res1 = await api_client.post(
        f"{PROJECTS_URL}/{p1['id']}/labels",
        headers=headers,
        json={"name": "Bug"},
    )
    res2 = await api_client.post(
        f"{PROJECTS_URL}/{p2['id']}/labels",
        headers=headers,
        json={"name": "Bug"},
    )
    assert res1.status_code == 201
    assert res2.status_code == 201


async def test_create_label_project_archived(api_client, active_user):
    """Tạo label trong project đã bị archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/labels",
        headers=headers,
        json={"name": "Blocked Label"},
    )
    assert response.status_code == 400


async def test_create_label_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/labels",
        json={"name": "Unauthorized Label"},
    )
    assert response.status_code == 401


async def test_create_label_forbidden_viewer_or_non_member(
    api_client, active_user, other_user
):
    """Người ngoài workspace hoặc VIEWER cố tình tạo label -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    other_headers = await get_auth_headers(api_client, other_user)

    # Chưa là thành viên
    res_non_member = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/labels",
        headers=other_headers,
        json={"name": "Hacker Label"},
    )
    assert res_non_member.status_code == 403

    # Thêm vào workspace với quyền VIEWER
    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER.value,
        },
    )

    res_viewer = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/labels",
        headers=other_headers,
        json={"name": "Viewer Label"},
    )
    assert res_viewer.status_code == 403


async def test_create_label_project_not_found(api_client, active_user):
    """Tạo label trong project không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.post(
        f"{PROJECTS_URL}/{uuid.uuid4()}/labels",
        headers=headers,
        json={"name": "Ghost Label"},
    )
    assert response.status_code == 404


async def test_create_label_invalid_payload_or_uuid(api_client, active_user):
    """Dữ liệu không hợp lệ hoặc project_id sai UUID -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    for bad_payload in [
        {},
        {"name": ""},
        {"name": "   "},
        {"name": "Ok", "color": "PINK"},
    ]:
        res = await api_client.post(
            f"{PROJECTS_URL}/{project['id']}/labels",
            headers=headers,
            json=bad_payload,
        )
        assert res.status_code == 422

    res_uuid = await api_client.post(
        f"{PROJECTS_URL}/not-a-valid-uuid/labels",
        headers=headers,
        json={"name": "Valid"},
    )
    assert res_uuid.status_code == 422


async def test_get_project_labels_success(api_client, active_user):
    """Lấy danh sách label của project thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    l1 = await _create_sample_label(api_client, headers, project["id"], "Bug")
    l2 = await _create_sample_label(api_client, headers, project["id"], "Feature")

    response = await api_client.get(
        f"{PROJECTS_URL}/{project['id']}/labels",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert {item["id"] for item in data} == {l1["id"], l2["id"]}


async def test_get_project_labels_viewer_allowed(api_client, active_user, other_user):
    """Thành viên có role VIEWER được phép xem danh sách label -> trả về 200"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    await _create_sample_label(api_client, owner_headers, project["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER.value,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.get(
        f"{PROJECTS_URL}/{project['id']}/labels",
        headers=viewer_headers,
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_project_labels_missing_token_or_forbidden(
    api_client, active_user, other_user
):
    """Thiếu token -> 401; không thuộc workspace -> 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    res_401 = await api_client.get(f"{PROJECTS_URL}/{project['id']}/labels")
    assert res_401.status_code == 401

    other_headers = await get_auth_headers(api_client, other_user)
    res_403 = await api_client.get(
        f"{PROJECTS_URL}/{project['id']}/labels",
        headers=other_headers,
    )
    assert res_403.status_code == 403


async def test_get_project_labels_not_found(api_client, active_user):
    """Project không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)
    response = await api_client.get(
        f"{PROJECTS_URL}/{uuid.uuid4()}/labels",
        headers=headers,
    )
    assert response.status_code == 404


async def test_update_label_success(api_client, active_user):
    """Cập nhật tên và màu sắc của label thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    label = await _create_sample_label(
        api_client, headers, project["id"], "Old Name", LabelColor.BLUE
    )

    payload = {
        "name": "Critical Bug",
        "color": LabelColor.RED.value,
    }
    response = await api_client.patch(
        f"{LABELS_URL}/{label['id']}",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == label["id"]
    assert data["name"] == "Critical Bug"
    assert data["color"] == LabelColor.RED


async def test_update_label_empty_or_null_ignored(api_client, active_user):
    """Gửi JSON rỗng {} hoặc giá trị null -> trả về 200 và giữ nguyên dữ liệu cũ"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    label = await _create_sample_label(
        api_client, headers, project["id"], "Keep Name", LabelColor.YELLOW
    )

    res_empty = await api_client.patch(
        f"{LABELS_URL}/{label['id']}",
        headers=headers,
        json={},
    )
    assert res_empty.status_code == 200
    assert res_empty.json()["name"] == "Keep Name"

    res_null = await api_client.patch(
        f"{LABELS_URL}/{label['id']}",
        headers=headers,
        json={"name": None, "color": None},
    )
    assert res_null.status_code == 200
    assert res_null.json()["name"] == "Keep Name"
    assert res_null.json()["color"] == LabelColor.YELLOW


async def test_update_label_duplicate_name_conflict(api_client, active_user):
    """Đổi tên label trùng với một label khác đã có trong project -> trả về 409"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    await _create_sample_label(api_client, headers, project["id"], "Backend")
    label2 = await _create_sample_label(api_client, headers, project["id"], "Frontend")

    response = await api_client.patch(
        f"{LABELS_URL}/{label2['id']}",
        headers=headers,
        json={"name": "backend"},
    )
    assert response.status_code == 409


async def test_update_label_project_archived(api_client, active_user):
    """Cập nhật label trong project đã archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    label = await _create_sample_label(api_client, headers, project["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.patch(
        f"{LABELS_URL}/{label['id']}",
        headers=headers,
        json={"name": "Updated"},
    )
    assert response.status_code == 400


async def test_update_label_missing_token_and_forbidden(
    api_client, active_user, other_user
):
    """Thiếu token -> 401; VIEWER cố tình sửa -> 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    label = await _create_sample_label(api_client, owner_headers, project["id"])

    res_401 = await api_client.patch(
        f"{LABELS_URL}/{label['id']}",
        json={"name": "No Token"},
    )
    assert res_401.status_code == 401

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER.value,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    res_403 = await api_client.patch(
        f"{LABELS_URL}/{label['id']}",
        headers=viewer_headers,
        json={"name": "Viewer Hack"},
    )
    assert res_403.status_code == 403


async def test_update_label_not_found_and_invalid_uuid(api_client, active_user):
    """Label không tồn tại -> 404; UUID sai định dạng -> 422"""
    headers = await get_auth_headers(api_client, active_user)

    res_404 = await api_client.patch(
        f"{LABELS_URL}/{uuid.uuid4()}",
        headers=headers,
        json={"name": "Ghost"},
    )
    assert res_404.status_code == 404

    res_422 = await api_client.patch(
        f"{LABELS_URL}/not-a-valid-uuid",
        headers=headers,
        json={"name": "Ghost"},
    )
    assert res_422.status_code == 422


async def test_delete_label_success(api_client, active_user):
    """Xóa label thành công (đồng thời gỡ khỏi các task đã gắn) -> trả về 204"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    label = await _create_sample_label(api_client, headers, project["id"])

    # Gắn label vào task trước khi xóa
    await api_client.post(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
        json={"label_id": label["id"]},
    )

    response = await api_client.delete(
        f"{LABELS_URL}/{label['id']}",
        headers=headers,
    )
    assert response.status_code == 204

    # Kiểm tra label đã biến mất khỏi project và khỏi task
    project_labels = await api_client.get(
        f"{PROJECTS_URL}/{project['id']}/labels",
        headers=headers,
    )
    assert project_labels.json() == []

    task_labels = await api_client.get(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
    )
    assert task_labels.json() == []


async def test_delete_label_project_archived(api_client, active_user):
    """Xóa label trong project đã archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    label = await _create_sample_label(api_client, headers, project["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.delete(
        f"{LABELS_URL}/{label['id']}",
        headers=headers,
    )
    assert response.status_code == 400


async def test_delete_label_missing_token_and_forbidden(
    api_client, active_user, other_user
):
    """Thiếu token -> 401; VIEWER cố tình xóa -> 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    label = await _create_sample_label(api_client, owner_headers, project["id"])

    res_401 = await api_client.delete(f"{LABELS_URL}/{label['id']}")
    assert res_401.status_code == 401

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER.value,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    res_403 = await api_client.delete(
        f"{LABELS_URL}/{label['id']}",
        headers=viewer_headers,
    )
    assert res_403.status_code == 403


async def test_delete_label_not_found(api_client, active_user):
    """Xóa label không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)
    response = await api_client.delete(
        f"{LABELS_URL}/{uuid.uuid4()}",
        headers=headers,
    )
    assert response.status_code == 404


async def test_assign_and_get_task_labels_success(api_client, active_user):
    """Gắn label vào task và lấy danh sách label của task thành công -> 201 & 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    l1 = await _create_sample_label(api_client, headers, project["id"], "Backend")
    l2 = await _create_sample_label(api_client, headers, project["id"], "API")

    res1 = await api_client.post(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
        json={"label_id": l1["id"]},
    )
    assert res1.status_code == 201
    assert len(res1.json()) == 1

    res2 = await api_client.post(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
        json={"label_id": l2["id"]},
    )
    assert res2.status_code == 201
    assert {item["id"] for item in res2.json()} == {l1["id"], l2["id"]}

    get_res = await api_client.get(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
    )
    assert get_res.status_code == 200
    assert {item["id"] for item in get_res.json()} == {l1["id"], l2["id"]}


async def test_assign_label_duplicate_conflict(api_client, active_user):
    """Gắn trùng một label đã tồn tại trên task -> trả về 409"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    label = await _create_sample_label(api_client, headers, project["id"])

    res1 = await api_client.post(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
        json={"label_id": label["id"]},
    )
    assert res1.status_code == 201

    res2 = await api_client.post(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
        json={"label_id": label["id"]},
    )
    assert res2.status_code == 409


async def test_assign_label_from_different_project_bad_request(api_client, active_user):
    """Gắn label thuộc project khác vào task -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    p1 = await _create_sample_project(api_client, headers, ws["id"], "Project 1")
    p2 = await _create_sample_project(api_client, headers, ws["id"], "Project 2")

    task_p1 = await _create_sample_task(api_client, headers, p1["id"])
    label_p2 = await _create_sample_label(api_client, headers, p2["id"])

    response = await api_client.post(
        f"{TASKS_URL}/{task_p1['id']}/labels",
        headers=headers,
        json={"label_id": label_p2["id"]},
    )
    assert response.status_code == 400


async def test_assign_label_project_archived(api_client, active_user):
    """Gắn label cho task khi project đã archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    label = await _create_sample_label(api_client, headers, project["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.post(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
        json={"label_id": label["id"]},
    )
    assert response.status_code == 400


async def test_assign_label_forbidden_viewer(api_client, active_user, other_user):
    """Thành viên có role VIEWER cố tình gắn label cho task -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])
    label = await _create_sample_label(api_client, owner_headers, project["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER.value,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.post(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=viewer_headers,
        json={"label_id": label["id"]},
    )
    assert response.status_code == 403


async def test_assign_label_task_or_label_not_found(api_client, active_user):
    """Task hoặc Label không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    label = await _create_sample_label(api_client, headers, project["id"])

    res_no_task = await api_client.post(
        f"{TASKS_URL}/{uuid.uuid4()}/labels",
        headers=headers,
        json={"label_id": label["id"]},
    )
    assert res_no_task.status_code == 404

    res_no_label = await api_client.post(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
        json={"label_id": str(uuid.uuid4())},
    )
    assert res_no_label.status_code == 404


async def test_remove_label_from_task_success(api_client, active_user):
    """Gỡ label khỏi task thành công -> trả về 204"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    label = await _create_sample_label(api_client, headers, project["id"])

    await api_client.post(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
        json={"label_id": label["id"]},
    )

    response = await api_client.delete(
        f"{TASKS_URL}/{task['id']}/labels/{label['id']}",
        headers=headers,
    )
    assert response.status_code == 204

    get_res = await api_client.get(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
    )
    assert get_res.json() == []


async def test_remove_label_from_task_not_assigned_not_found(api_client, active_user):
    """Gỡ label chưa được gắn vào task -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    label = await _create_sample_label(api_client, headers, project["id"])

    response = await api_client.delete(
        f"{TASKS_URL}/{task['id']}/labels/{label['id']}",
        headers=headers,
    )
    assert response.status_code == 404


async def test_remove_label_from_task_project_archived(api_client, active_user):
    """Gỡ label khỏi task khi project đã archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    label = await _create_sample_label(api_client, headers, project["id"])

    await api_client.post(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=headers,
        json={"label_id": label["id"]},
    )
    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.delete(
        f"{TASKS_URL}/{task['id']}/labels/{label['id']}",
        headers=headers,
    )
    assert response.status_code == 400


async def test_remove_label_from_task_forbidden_viewer(
    api_client, active_user, other_user
):
    """Thành viên có role VIEWER cố tình gỡ label khỏi task -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])
    label = await _create_sample_label(api_client, owner_headers, project["id"])

    await api_client.post(
        f"{TASKS_URL}/{task['id']}/labels",
        headers=owner_headers,
        json={"label_id": label["id"]},
    )
    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER.value,
        },
    )

    viewer_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.delete(
        f"{TASKS_URL}/{task['id']}/labels/{label['id']}",
        headers=viewer_headers,
    )
    assert response.status_code == 403
