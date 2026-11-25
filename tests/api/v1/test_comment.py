import uuid

from taskhub.core.enums import WorkspaceMemberRole
from tests.api.v1.constants import (
    COMMENTS_URL,
    PROJECTS_URL,
    TASKS_URL,
    WORKSPACES_URL,
)
from tests.api.v1.get_auth_credentials import get_auth_headers
from tests.api.v1.test_project import _create_sample_project
from tests.api.v1.test_task import _create_sample_task
from tests.api.v1.test_workspace import _create_sample_workspace


async def _create_sample_comment(
    api_client,
    headers: dict,
    task_id: str,
    content: str = "Sample comment content",
) -> dict:
    response = await api_client.post(
        f"{TASKS_URL}/{task_id}/comments",
        headers=headers,
        json={"content": content},
    )
    assert response.status_code == 201
    return response.json()


async def test_create_comment_success(api_client, active_user):
    """Thêm bình luận vào task thành công -> trả về 201"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    payload = {"content": "Looks good to me!"}
    response = await api_client.post(
        f"{TASKS_URL}/{task['id']}/comments",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == payload["content"]
    assert data["task_id"] == task["id"]
    assert data["author_id"] == str(active_user["id"])
    assert "id" in data
    assert "created_at" in data


async def test_create_comment_editor_allowed(api_client, active_user, other_user):
    """Thành viên có role EDITOR được phép bình luận -> trả về 201"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])

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
        f"{TASKS_URL}/{task['id']}/comments",
        headers=editor_headers,
        json={"content": "Editor comment"},
    )
    assert response.status_code == 201
    assert response.json()["author_id"] == str(other_user["id"])


async def test_create_comment_project_archived(api_client, active_user):
    """Thêm bình luận trong project đã archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.post(
        f"{TASKS_URL}/{task['id']}/comments",
        headers=headers,
        json={"content": "Blocked comment"},
    )
    assert response.status_code == 400


async def test_create_comment_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    response = await api_client.post(
        f"{TASKS_URL}/{task['id']}/comments",
        json={"content": "Unauthorized comment"},
    )
    assert response.status_code == 401


async def test_create_comment_forbidden_viewer_or_non_member(
    api_client, active_user, other_user
):
    """Người ngoài workspace hoặc VIEWER cố tình bình luận -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])

    other_headers = await get_auth_headers(api_client, other_user)
    res_non_member = await api_client.post(
        f"{TASKS_URL}/{task['id']}/comments",
        headers=other_headers,
        json={"content": "Stranger comment"},
    )
    assert res_non_member.status_code == 403

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.VIEWER.value,
        },
    )

    res_viewer = await api_client.post(
        f"{TASKS_URL}/{task['id']}/comments",
        headers=other_headers,
        json={"content": "Viewer comment"},
    )
    assert res_viewer.status_code == 403


async def test_create_comment_task_not_found(api_client, active_user):
    """Thêm bình luận vào task không tồn tại -> trả về 404"""
    headers = await get_auth_headers(api_client, active_user)
    response = await api_client.post(
        f"{TASKS_URL}/{uuid.uuid4()}/comments",
        headers=headers,
        json={"content": "Ghost comment"},
    )
    assert response.status_code == 404


async def test_create_comment_invalid_payload(api_client, active_user):
    """Nội dung rỗng hoặc toàn khoảng trắng -> trả về 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    for invalid_payload in [{}, {"content": ""}, {"content": "   "}]:
        response = await api_client.post(
            f"{TASKS_URL}/{task['id']}/comments",
            headers=headers,
            json=invalid_payload,
        )
        assert response.status_code == 422


async def test_get_task_comments_success(api_client, active_user):
    """Lấy danh sách bình luận của task thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])

    c1 = await _create_sample_comment(api_client, headers, task["id"], "First comment")
    c2 = await _create_sample_comment(api_client, headers, task["id"], "Second comment")

    response = await api_client.get(
        f"{TASKS_URL}/{task['id']}/comments",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert [item["id"] for item in data["items"]] == [c1["id"], c2["id"]]


async def test_get_task_comments_viewer_allowed(api_client, active_user, other_user):
    """Thành viên có role VIEWER được phép xem danh sách bình luận -> trả về 200"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])
    await _create_sample_comment(api_client, owner_headers, task["id"])

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
        f"{TASKS_URL}/{task['id']}/comments",
        headers=viewer_headers,
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1


async def test_update_comment_success(api_client, active_user):
    """Tác giả chỉnh sửa nội dung bình luận thành công -> trả về 200"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    comment = await _create_sample_comment(
        api_client, headers, task["id"], "Initial content"
    )

    response = await api_client.patch(
        f"{COMMENTS_URL}/{comment['id']}",
        headers=headers,
        json={"content": "Updated content"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == comment["id"]
    assert data["content"] == "Updated content"


async def test_update_comment_empty_or_null_ignored(api_client, active_user):
    """Gửi JSON rỗng {} hoặc content=null -> trả về 200 và giữ nguyên nội dung cũ"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    comment = await _create_sample_comment(
        api_client, headers, task["id"], "Original content"
    )

    res_empty = await api_client.patch(
        f"{COMMENTS_URL}/{comment['id']}",
        headers=headers,
        json={},
    )
    assert res_empty.status_code == 200
    assert res_empty.json()["content"] == "Original content"

    res_null = await api_client.patch(
        f"{COMMENTS_URL}/{comment['id']}",
        headers=headers,
        json={"content": None},
    )
    assert res_null.status_code == 200
    assert res_null.json()["content"] == "Original content"


async def test_update_comment_project_archived(api_client, active_user):
    """Chỉnh sửa bình luận trong project đã archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    comment = await _create_sample_comment(api_client, headers, task["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.patch(
        f"{COMMENTS_URL}/{comment['id']}",
        headers=headers,
        json={"content": "Cannot edit in archived project"},
    )
    assert response.status_code == 400


async def test_update_comment_missing_token(api_client, active_user):
    """Không đính kèm token -> trả về 401"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    comment = await _create_sample_comment(api_client, headers, task["id"])

    response = await api_client.patch(
        f"{COMMENTS_URL}/{comment['id']}",
        json={"content": "No token"},
    )
    assert response.status_code == 401


async def test_update_comment_forbidden_not_author(api_client, active_user, other_user):
    """Người khác cố tình sửa bình luận của người khác -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.EDITOR.value,
        },
    )

    # Editor tạo comment
    editor_headers = await get_auth_headers(api_client, other_user)
    editor_comment = await _create_sample_comment(
        api_client, editor_headers, task["id"], "Editor's own words"
    )

    # Owner workspace cố tình sửa comment của Editor -> 403
    res_owner_edit = await api_client.patch(
        f"{COMMENTS_URL}/{editor_comment['id']}",
        headers=owner_headers,
        json={"content": "Owner edited this"},
    )
    assert res_owner_edit.status_code == 403


async def test_update_comment_not_found_and_invalid_payload(api_client, active_user):
    """Comment không tồn tại -> 404; nội dung rỗng hoặc UUID sai -> 422"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    comment = await _create_sample_comment(api_client, headers, task["id"])

    res_404 = await api_client.patch(
        f"{COMMENTS_URL}/{uuid.uuid4()}",
        headers=headers,
        json={"content": "Ghost"},
    )
    assert res_404.status_code == 404

    res_bad_content = await api_client.patch(
        f"{COMMENTS_URL}/{comment['id']}",
        headers=headers,
        json={"content": "   "},
    )
    assert res_bad_content.status_code == 422

    res_bad_uuid = await api_client.patch(
        f"{COMMENTS_URL}/not-a-valid-uuid",
        headers=headers,
        json={"content": "Valid"},
    )
    assert res_bad_uuid.status_code == 422


async def test_delete_comment_by_author_success(api_client, active_user):
    """Tác giả tự xóa bình luận của mình thành công -> trả về 204"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    comment = await _create_sample_comment(api_client, headers, task["id"])

    response = await api_client.delete(
        f"{COMMENTS_URL}/{comment['id']}",
        headers=headers,
    )
    assert response.status_code == 204

    list_res = await api_client.get(
        f"{TASKS_URL}/{task['id']}/comments",
        headers=headers,
    )
    assert list_res.json()["total"] == 0


async def test_delete_comment_by_workspace_owner_success(
    api_client, active_user, other_user
):
    """Chủ sở hữu workspace xóa bình luận của thành viên khác thành công -> trả về 204"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.EDITOR.value,
        },
    )

    editor_headers = await get_auth_headers(api_client, other_user)
    comment = await _create_sample_comment(
        api_client, editor_headers, task["id"], "Inappropriate comment"
    )

    response = await api_client.delete(
        f"{COMMENTS_URL}/{comment['id']}",
        headers=owner_headers,
    )
    assert response.status_code == 204


async def test_delete_comment_forbidden_other_member(
    api_client, active_user, other_user
):
    """Thành viên không phải tác giả cũng không phải Owner cố tình xóa bình luận -> trả về 403"""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    task = await _create_sample_task(api_client, owner_headers, project["id"])
    owner_comment = await _create_sample_comment(api_client, owner_headers, task["id"])

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=owner_headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.EDITOR.value,
        },
    )

    editor_headers = await get_auth_headers(api_client, other_user)
    response = await api_client.delete(
        f"{COMMENTS_URL}/{owner_comment['id']}",
        headers=editor_headers,
    )
    assert response.status_code == 403


async def test_delete_comment_project_archived(api_client, active_user):
    """Xóa bình luận trong project đã archive -> trả về 400"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    comment = await _create_sample_comment(api_client, headers, task["id"])

    await api_client.post(
        f"{PROJECTS_URL}/{project['id']}/archive",
        headers=headers,
    )

    response = await api_client.delete(
        f"{COMMENTS_URL}/{comment['id']}",
        headers=headers,
    )
    assert response.status_code == 400


async def test_delete_comment_missing_token_and_not_found(api_client, active_user):
    """Thiếu token -> 401; comment không tồn tại -> 404"""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"])
    comment = await _create_sample_comment(api_client, headers, task["id"])

    res_401 = await api_client.delete(f"{COMMENTS_URL}/{comment['id']}")
    assert res_401.status_code == 401

    res_404 = await api_client.delete(
        f"{COMMENTS_URL}/{uuid.uuid4()}",
        headers=headers,
    )
    assert res_404.status_code == 404
