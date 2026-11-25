import uuid
from datetime import UTC, datetime, timedelta

from taskhub.core.enums import Priority, TaskStatus, WorkspaceMemberRole
from tests.api.v1.constants import PROJECTS_URL, TASKS_URL, WORKSPACES_URL
from tests.api.v1.get_auth_credentials import get_auth_headers
from tests.api.v1.test_project import _create_sample_project
from tests.api.v1.test_workspace import _create_sample_workspace


async def _create_sample_task(
    api_client,
    headers: dict,
    project_id: str,
    title: str = "Sample Task",
    **kwargs,
) -> dict:
    payload = {"title": title, **kwargs}
    response = await api_client.post(
        f"{PROJECTS_URL}/{project_id}/tasks",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 201
    return response.json()


async def test_create_task_success(api_client, active_user, other_user):
    """Tạo task đầy đủ thông tin trong project thành công -> trả về 201"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    # Thêm other_user vào workspace để giao việc
    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.EDITOR,
        },
    )

    due_date = (datetime.now(UTC) + timedelta(days=3)).replace(microsecond=0)
    payload = {
        "title": "Implement Task API",
        "description": "Write endpoints and services for tasks",
        "assignee_id": str(other_user["id"]),
        "status": TaskStatus.IN_PROGRESS.value,
        "priority": Priority.HIGH.value,
        "due_date": due_date.isoformat(),
    }

    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["project_id"] == project["id"]
    assert data["assignee_id"] == str(other_user["id"])
    assert data["status"] == TaskStatus.IN_PROGRESS
    assert data["priority"] == Priority.HIGH
    assert datetime.fromisoformat(data["due_date"]) == due_date
    assert data["created_by"] == str(active_user["id"])
    assert "id" in data
    assert "created_at" in data


async def test_create_task_minimal_success(api_client, active_user):
    """Tạo task chỉ với trường title -> trả về 201"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=headers,
        json={"title": "Minimal Task"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal Task"
    assert data["description"] is None
    assert data["assignee_id"] is None
    assert data["status"] == TaskStatus.TODO
    assert data["priority"] == Priority.MEDIUM
    assert data["due_date"] is None


async def test_create_task_editor_allowed(api_client, active_user, other_user):
    """Thành viên có role EDITOR được phép tạo task -> trả về 201"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.EDITOR,
        },
    )

    editor_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=editor_headers,
        json={"title": "Editor Created Task"},
    )
    assert response.status_code == 201


async def test_create_task_assignee_not_in_workspace(
    api_client, active_user, other_user
):
    """Giao task cho user không thuộc workspace -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=headers,
        json={
            "title": "Invalid Assignee Task",
            "assignee_id": str(other_user["id"]),
        },
    )
    assert response.status_code == 400


async def test_create_task_project_archived(api_client, active_user):
    """Tạo task trong project đã bị archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=headers,
        json={"title": "Task In Archived Project"},
    )
    assert response.status_code == 400


async def test_create_task_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        json={"title": "Unauthorized Task"},
    )
    assert response.status_code == 401


async def test_create_task_invalid_token(api_client, active_user):
    """Token sai định dạng -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers={"Authorization": "Bearer invalid.token.here"},
        json={"title": "Unauthorized Task"},
    )
    assert response.status_code == 401


async def test_create_task_forbidden_not_member(api_client, active_user, other_user):
    """Người dùng không thuộc workspace cố tình tạo task -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    other_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=other_headers,
        json={"title": "Forbidden Task"},
    )
    assert response.status_code == 403


async def test_create_task_forbidden_viewer(api_client, active_user, other_user):
    """Thành viên có role VIEWER cố tình tạo task -> trả về 403"""
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
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=viewer_headers,
        json={"title": "Viewer Task"},
    )
    assert response.status_code == 403


async def test_create_task_project_not_found(api_client, active_user):
    """Tạo task trong project không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.post(
        f"{PROJECTS_URL}/{uuid.uuid4()}/tasks",
        headers=headers,
        json={"title": "Ghost Task"},
    )
    assert response.status_code == 404


async def test_create_task_invalid_payload(api_client, active_user):
    """Thiếu title hoặc enum không hợp lệ -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    invalid_payloads = [
        {},
        {"title": ""},
        {"title": "   "},
        {"title": "Valid", "status": "INVALID_STATUS"},
        {"title": "Valid", "priority": "INVALID_PRIORITY"},
    ]
    for payload in invalid_payloads:
        response = await api_client.post(
            f"{PROJECTS_URL}/{project['id']}/tasks",
            headers=headers,
            json=payload,
        )
        assert response.status_code == 422


async def test_create_task_invalid_project_uuid(api_client, active_user):
    """project_id trên URL không đúng định dạng UUID -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.post(
        f"{PROJECTS_URL}/not-a-valid-uuid/tasks",
        headers=headers,
        json={"title": "Valid Title"},
    )
    assert response.status_code == 422


async def test_get_project_tasks_success(api_client, active_user):
    """Lấy danh sách task trong project thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    t1 = await _create_sample_task(api_client, headers, project["id"], "Task 1")
    t2 = await _create_sample_task(api_client, headers, project["id"], "Task 2")

    response = await api_client.get(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1

    expected_ids = [
        t["id"]
        for t in sorted(
            [t1, t2], key=lambda x: (x["created_at"], x["id"]), reverse=True
        )
    ]
    assert [item["id"] for item in data["items"]] == expected_ids


async def test_get_project_tasks_empty(api_client, active_user):
    """Project chưa có task nào -> trả về danh sách rỗng và status 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.get(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["total_pages"] == 0


async def test_get_project_tasks_filters_and_search(
    api_client, active_user, other_user
):
    """Lọc task theo status, priority, assignee_id và tìm kiếm theo title -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.EDITOR,
        },
    )

    target_task = await _create_sample_task(
        api_client,
        headers,
        project["id"],
        title="Fix Login Bug",
        status=TaskStatus.IN_PROGRESS.value,
        priority=Priority.HIGH.value,
        assignee_id=str(other_user["id"]),
    )
    await _create_sample_task(
        api_client,
        headers,
        project["id"],
        title="Write Documentation",
        status=TaskStatus.TODO.value,
        priority=Priority.LOW.value,
    )

    response = await api_client.get(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=headers,
        params={
            "status": TaskStatus.IN_PROGRESS.value,
            "priority": Priority.HIGH.value,
            "assignee_id": str(other_user["id"]),
            "search": "login",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == target_task["id"]


async def test_get_project_tasks_viewer_allowed(api_client, active_user, other_user):
    """Thành viên có role VIEWER được phép xem danh sách task -> trả về 200"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    await _create_sample_task(api_client, owner_headers, project["id"])

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
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=viewer_headers,
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


async def test_get_project_tasks_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.get(f"{PROJECTS_URL}/{project['id']}/tasks")
    assert response.status_code == 401


async def test_get_project_tasks_forbidden_not_member(
    api_client, active_user, other_user
):
    """Người dùng không thuộc workspace cố tình xem danh sách task -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])

    other_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.get(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=other_headers,
    )
    assert response.status_code == 403


async def test_get_project_tasks_project_not_found(api_client, active_user):
    """Lấy danh sách task của project không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.get(
        f"{PROJECTS_URL}/{uuid.uuid4()}/tasks",
        headers=headers,
    )
    assert response.status_code == 404


async def test_get_project_tasks_invalid_params(api_client, active_user):
    """Truyền query param không hợp lệ -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    response = await api_client.get(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=headers,
        params={"status": "INVALID_STATUS"},
    )
    assert response.status_code == 422


async def test_get_task_detail_success(api_client, active_user):
    """Lấy chi tiết task thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(
        api_client, headers, project["id"], "Detail Task", description="Task info"
    )

    response = await api_client.get(
        f"{TASKS_URL}/{task['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task["id"]
    assert data["title"] == "Detail Task"
    assert data["description"] == "Task info"
    assert data["project_id"] == project["id"]


async def test_get_task_detail_viewer_allowed(api_client, active_user, other_user):
    """Thành viên có role VIEWER được phép xem chi tiết task -> trả về 200"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])

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
        f"{TASKS_URL}/{task['id']}",
        headers=viewer_headers,
    )
    assert response.status_code == 200


async def test_get_task_detail_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    response = await api_client.get(f"{TASKS_URL}/{task['id']}")
    assert response.status_code == 401


async def test_get_task_detail_forbidden_not_member(
    api_client, active_user, other_user
):
    """Người dùng không thuộc workspace cố tình xem chi tiết task -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])

    other_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.get(
        f"{TASKS_URL}/{task['id']}",
        headers=other_headers,
    )
    assert response.status_code == 403


async def test_get_task_detail_not_found(api_client, active_user):
    """Task không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.get(
        f"{TASKS_URL}/{uuid.uuid4()}",
        headers=headers,
    )
    assert response.status_code == 404


async def test_get_task_detail_invalid_uuid(api_client, active_user):
    """task_id trên URL không đúng định dạng UUID -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.get(
        f"{TASKS_URL}/not-a-valid-uuid",
        headers=headers,
    )
    assert response.status_code == 422


async def test_update_task_success(api_client, active_user, other_user):
    """Cập nhật thông tin task thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"], "Old Title")

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.EDITOR,
        },
    )

    new_due_date = (datetime.now(UTC) + timedelta(days=5)).replace(microsecond=0)
    payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "assignee_id": str(other_user["id"]),
        "status": TaskStatus.DONE.value,
        "priority": Priority.HIGH.value,
        "due_date": new_due_date.isoformat(),
    }

    response = await api_client.patch(
        f"{TASKS_URL}/{task['id']}",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["assignee_id"] == str(other_user["id"])
    assert data["status"] == TaskStatus.DONE
    assert data["priority"] == Priority.HIGH
    assert datetime.fromisoformat(data["due_date"]) == new_due_date


async def test_update_task_clear_nullable_fields(api_client, active_user):
    """Truyền assignee_id=None và due_date=None để gỡ người làm và hạn chót -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    due_date = (datetime.now(UTC) + timedelta(days=2)).replace(microsecond=0)
    task = await _create_sample_task(
        api_client,
        headers,
        project["id"],
        title="Assigned Task",
        assignee_id=str(active_user["id"]),
        due_date=due_date.isoformat(),
    )

    response = await api_client.patch(
        f"{TASKS_URL}/{task['id']}",
        headers=headers,
        json={"assignee_id": None, "due_date": None},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["assignee_id"] is None
    assert data["due_date"] is None


async def test_update_task_empty_json_ignored(api_client, active_user):
    """Gửi JSON rỗng {} -> trả về 200 và giữ nguyên dữ liệu cũ"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(
        api_client, headers, project["id"], "Original Title"
    )

    response = await api_client.patch(
        f"{TASKS_URL}/{task['id']}",
        headers=headers,
        json={},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Original Title"


async def test_update_task_assignee_not_in_workspace(
    api_client, active_user, other_user
):
    """Cập nhật assignee_id là người ngoài workspace -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    response = await api_client.patch(
        f"{TASKS_URL}/{task['id']}",
        headers=headers,
        json={"assignee_id": str(other_user["id"])},
    )
    assert response.status_code == 400


async def test_update_task_project_archived(api_client, active_user):
    """Cập nhật task trong project đã bị archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.patch(
        f"{TASKS_URL}/{task['id']}",
        headers=headers,
        json={"title": "Cannot Update"},
    )
    assert response.status_code == 400


async def test_update_task_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    response = await api_client.patch(
        f"{TASKS_URL}/{task['id']}",
        json={"title": "Unauthorized Update"},
    )
    assert response.status_code == 401


async def test_update_task_forbidden_viewer(api_client, active_user, other_user):
    """Thành viên có role VIEWER cố tình cập nhật task -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])

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
        f"{TASKS_URL}/{task['id']}",
        headers=viewer_headers,
        json={"title": "Viewer Hack"},
    )
    assert response.status_code == 403


async def test_update_task_not_found(api_client, active_user):
    """Cập nhật task không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.patch(
        f"{TASKS_URL}/{uuid.uuid4()}",
        headers=headers,
        json={"title": "Ghost Task"},
    )
    assert response.status_code == 404


async def test_update_task_invalid_payload_or_uuid(api_client, active_user):
    """Dữ liệu cập nhật hoặc UUID không hợp lệ -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    res_bad_title = await api_client.patch(
        f"{TASKS_URL}/{task['id']}",
        headers=headers,
        json={"title": "   "},
    )
    assert res_bad_title.status_code == 422

    res_bad_uuid = await api_client.patch(
        f"{TASKS_URL}/not-a-valid-uuid",
        headers=headers,
        json={"title": "Valid"},
    )
    assert res_bad_uuid.status_code == 422


async def test_assign_and_unassign_task_success(api_client, active_user, other_user):
    """Giao task cho thành viên và gỡ người được giao thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER,
        },
    )

    # Giao việc
    res_assign = await api_client.patch(
        f"{TASKS_URL}/{task['id']}/assign",
        headers=headers,
        json={"assignee_id": str(other_user["id"])},
    )
    assert res_assign.status_code == 200
    assert res_assign.json()["assignee_id"] == str(other_user["id"])

    # Gỡ người được giao
    res_unassign = await api_client.patch(
        f"{TASKS_URL}/{task['id']}/assign",
        headers=headers,
        json={"assignee_id": None},
    )
    assert res_unassign.status_code == 200
    assert res_unassign.json()["assignee_id"] is None


async def test_assign_task_not_in_workspace(api_client, active_user, other_user):
    """Giao task qua endpoint /assign cho người ngoài workspace -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    response = await api_client.patch(
        f"{TASKS_URL}/{task['id']}/assign",
        headers=headers,
        json={"assignee_id": str(other_user["id"])},
    )
    assert response.status_code == 400


async def test_assign_task_missing_assignee_key(api_client, active_user):
    """Gửi body rỗng {} -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    response = await api_client.patch(
        f"{TASKS_URL}/{task['id']}/assign",
        headers=headers,
        json={},
    )
    assert response.status_code == 422


async def test_assign_task_forbidden_viewer(api_client, active_user, other_user):
    """Thành viên có role VIEWER cố tình giao task -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])

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
        f"{TASKS_URL}/{task['id']}/assign",
        headers=viewer_headers,
        json={"assignee_id": str(other_user["id"])},
    )
    assert response.status_code == 403


async def test_update_task_status_success(api_client, active_user):
    """Chuyển trạng thái task thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    response = await api_client.patch(
        f"{TASKS_URL}/{task['id']}/status",
        headers=headers,
        json={"status": TaskStatus.DONE.value},
    )

    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.DONE


async def test_update_task_status_project_archived(api_client, active_user):
    """Chuyển trạng thái task trong project đã archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.patch(
        f"{TASKS_URL}/{task['id']}/status",
        headers=headers,
        json={"status": TaskStatus.IN_PROGRESS.value},
    )
    assert response.status_code == 400


async def test_update_task_status_forbidden_viewer(api_client, active_user, other_user):
    """Thành viên có role VIEWER cố tình chuyển trạng thái task -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])

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
        f"{TASKS_URL}/{task['id']}/status",
        headers=viewer_headers,
        json={"status": TaskStatus.DONE.value},
    )
    assert response.status_code == 403


async def test_update_task_status_invalid_value(api_client, active_user):
    """Truyền status không hợp lệ hoặc null -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    for invalid_payload in [{}, {"status": None}, {"status": "UNKNOWN"}]:
        response = await api_client.patch(
            f"{TASKS_URL}/{task['id']}/status",
            headers=headers,
            json=invalid_payload,
        )
        assert response.status_code == 422


async def test_delete_task_success(api_client, active_user):
    """Xóa task thành công -> trả về 204"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    task_id = task["id"]

    response = await api_client.delete(
        f"{TASKS_URL}/{task_id}",
        headers=headers,
    )
    assert response.status_code == 204

    get_res = await api_client.get(
        f"{TASKS_URL}/{task_id}",
        headers=headers,
    )
    assert get_res.status_code == 404


async def test_delete_task_project_archived(api_client, active_user):
    """Xóa task trong project đã bị archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.delete(
        f"{TASKS_URL}/{task['id']}",
        headers=headers,
    )
    assert response.status_code == 400


async def test_delete_task_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    response = await api_client.delete(f"{TASKS_URL}/{task['id']}")
    assert response.status_code == 401


async def test_delete_task_forbidden_viewer(api_client, active_user, other_user):
    """Thành viên có role VIEWER cố tình xóa task -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])

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
        f"{TASKS_URL}/{task['id']}",
        headers=viewer_headers,
    )
    assert response.status_code == 403


async def test_delete_task_not_found(api_client, active_user):
    """Xóa task không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.delete(
        f"{TASKS_URL}/{uuid.uuid4()}",
        headers=headers,
    )
    assert response.status_code == 404


async def test_delete_task_invalid_uuid(api_client, active_user):
    """task_id trên URL không đúng định dạng UUID -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)

    response = await api_client.delete(
        f"{TASKS_URL}/not-a-valid-uuid",
        headers=headers,
    )
    assert response.status_code == 422


async def test_update_task_null_required_fields(api_client, active_user):
    """Truyền null cho các trường bắt buộc (không cho phép null) như title -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    null_payloads = [
        {"title": None},
        {"status": None},
        {"priority": None},
    ]

    for payload in null_payloads:
        response = await api_client.patch(
            f"{TASKS_URL}/{task['id']}",
            headers=headers,
            json=payload,
        )
        assert response.status_code == 422


async def test_create_task_past_due_date(api_client, active_user):
    """Tạo task với due_date ở quá khứ -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])

    past_due_date = (datetime.now(UTC) - timedelta(days=1)).replace(microsecond=0)
    response = await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/tasks",
        headers=headers,
        json={
            "title": "Overdue Task",
            "due_date": past_due_date.isoformat(),
        },
    )

    assert response.status_code == 400


async def test_update_task_past_due_date(api_client, active_user):
    """Cập nhật task với due_date ở quá khứ -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    past_due_date = (datetime.now(UTC) - timedelta(days=1)).replace(microsecond=0)
    response = await api_client.patch(
        f"{TASKS_URL}/{task['id']}",
        headers=headers,
        json={"due_date": past_due_date.isoformat()},
    )

    assert response.status_code == 400
