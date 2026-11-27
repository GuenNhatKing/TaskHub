from unittest.mock import AsyncMock

from redis.exceptions import RedisError

from taskhub.core.enums import Priority, TaskStatus, WorkspaceMemberRole
from taskhub.core.redis import get_redis
from taskhub.main import app
from taskhub.repos.task import TaskRepository
from tests.api.v1.constants import PROJECTS_URL, TASKS_URL, WORKSPACES_URL
from tests.api.v1.get_auth_credentials import get_auth_headers
from tests.api.v1.test_project import _create_sample_project
from tests.api.v1.test_task import _create_sample_task
from tests.api.v1.test_workspace import _create_sample_workspace


async def test_get_project_tasks_cache_hit_and_miss(
    api_client,
    active_user,
    fake_redis,
    monkeypatch,
):
    """Cache Miss lần 1 (query DB + lưu Redis) và Cache Hit lần 2 (lấy từ Redis)."""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    await _create_sample_task(api_client, headers, project["id"], "Task 1")

    url = f"{PROJECTS_URL}/{project['id']}/tasks"

    db_call_count = 0
    original_get_by_project_id = TaskRepository.get_by_project_id

    # monkeypatch là fixture của pytest giúp tráo tạm thời một hàm/thuộc tính trong lúc chạy test
    # và tự động khôi phục lại hàm gốc khi test kết thúc. Ở đây, spy_get_by_project_id bọc
    # lấy TaskRepository.get_by_project_id thật để tăng biến đếm db_call_count += 1
    # mỗi lần gọi db, sau đó vẫn gọi original_get_by_project_id để trả về dữ liệu thật.
    # Nhờ đó ta chứng minh được lần gọi thứ 2 không hề chạy xuống DB.
    async def spy_get_by_project_id(self, *args, **kwargs):
        nonlocal db_call_count
        db_call_count += 1
        return await original_get_by_project_id(self, *args, **kwargs)

    monkeypatch.setattr(TaskRepository, "get_by_project_id", spy_get_by_project_id)

    # Lần 1 (Cache Miss): Query DB và lưu vào Redis kèm TTL
    res1 = await api_client.get(url, headers=headers)
    assert res1.status_code == 200
    assert db_call_count == 1

    keys = [k async for k in fake_redis.scan_iter(f"tasks:project:{project['id']}:*")]
    assert len(keys) == 1
    assert await fake_redis.ttl(keys[0]) > 0

    # Lần 2 (Cache Hit): Trả về kết quả cũ, không gọi xuống DB
    res2 = await api_client.get(url, headers=headers)
    assert res2.status_code == 200
    assert res2.json() == res1.json()
    assert db_call_count == 1


async def test_get_project_tasks_cache_distinct_keys_by_filters(
    api_client,
    active_user,
    fake_redis,
):
    """Các bộ lọc/trang khác nhau sinh ra các cache key riêng biệt trong Redis."""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    await _create_sample_task(
        api_client, headers, project["id"], "High Task", priority=Priority.HIGH.value
    )

    url = f"{PROJECTS_URL}/{project['id']}/tasks"
    pattern = f"tasks:project:{project['id']}:*"

    await api_client.get(url, headers=headers)
    await api_client.get(url, headers=headers, params={"priority": Priority.HIGH.value})
    await api_client.get(url, headers=headers, params={"page": 2, "page_size": 10})

    keys = [k async for k in fake_redis.scan_iter(pattern)]
    assert len(keys) == 3


async def test_cache_invalidated_on_create_task(
    api_client,
    active_user,
    fake_redis,
):
    """Tạo task mới -> xóa cache cũ và lần GET tiếp theo trả về đủ task mới."""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    await _create_sample_task(api_client, headers, project["id"], "Task 1")

    list_url = f"{PROJECTS_URL}/{project['id']}/tasks"
    pattern = f"tasks:project:{project['id']}:*"

    # Nạp cache (1 task)
    res_before = await api_client.get(list_url, headers=headers)
    assert res_before.json()["total"] == 1
    assert len([k async for k in fake_redis.scan_iter(pattern)]) == 1

    # Tạo thêm task mới -> cache bị xóa
    await _create_sample_task(api_client, headers, project["id"], "Task 2")
    assert len([k async for k in fake_redis.scan_iter(pattern)]) == 0

    # Gọi lại GET -> nạp lại cache mới với 2 task
    res_after = await api_client.get(list_url, headers=headers)
    assert res_after.status_code == 200
    assert res_after.json()["total"] == 2
    assert len([k async for k in fake_redis.scan_iter(pattern)]) == 1


async def test_cache_invalidated_on_update_task(
    api_client,
    active_user,
    other_user,
    fake_redis,
):
    """Cập nhật task (PATCH, /assign, /status) -> xóa cache cũ và cập nhật dữ liệu mới."""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"], "Old Title")

    await api_client.post(
        f"{WORKSPACES_URL}/{ws['id']}/members",
        headers=headers,
        json={
            "user_id": str(other_user["id"]),
            "role": WorkspaceMemberRole.EDITOR.value,
        },
    )

    list_url = f"{PROJECTS_URL}/{project['id']}/tasks"
    pattern = f"tasks:project:{project['id']}:*"

    # Cập nhật qua PATCH /tasks/{task_id}
    await api_client.get(list_url, headers=headers)
    assert len([k async for k in fake_redis.scan_iter(pattern)]) == 1

    patch_res = await api_client.patch(
        f"{TASKS_URL}/{task['id']}",
        headers=headers,
        json={"title": "New Title", "priority": Priority.HIGH.value},
    )
    assert patch_res.status_code == 200
    assert len([k async for k in fake_redis.scan_iter(pattern)]) == 0

    # Cập nhật qua PATCH /tasks/{task_id}/assign
    await api_client.get(list_url, headers=headers)
    assert len([k async for k in fake_redis.scan_iter(pattern)]) == 1

    assign_res = await api_client.patch(
        f"{TASKS_URL}/{task['id']}/assign",
        headers=headers,
        json={"assignee_id": str(other_user["id"])},
    )
    assert assign_res.status_code == 200
    assert len([k async for k in fake_redis.scan_iter(pattern)]) == 0

    # Cập nhật qua PATCH /tasks/{task_id}/status
    await api_client.get(list_url, headers=headers)
    assert len([k async for k in fake_redis.scan_iter(pattern)]) == 1

    status_res = await api_client.patch(
        f"{TASKS_URL}/{task['id']}/status",
        headers=headers,
        json={"status": TaskStatus.DONE.value},
    )
    assert status_res.status_code == 200
    assert len([k async for k in fake_redis.scan_iter(pattern)]) == 0

    # Kiểm tra dữ liệu trả về sau khi nạp lại cache khớp với các thay đổi
    res_after = await api_client.get(list_url, headers=headers)
    item = res_after.json()["items"][0]
    assert item["title"] == "New Title"
    assert item["priority"] == Priority.HIGH
    assert item["assignee_id"] == str(other_user["id"])
    assert item["status"] == TaskStatus.DONE


async def test_cache_invalidated_on_delete_task(
    api_client,
    active_user,
    fake_redis,
):
    """Xóa task -> xóa cache cũ và lần GET tiếp theo không còn task đã xóa."""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    t1 = await _create_sample_task(api_client, headers, project["id"], "Task 1")
    t2 = await _create_sample_task(api_client, headers, project["id"], "Task 2")

    list_url = f"{PROJECTS_URL}/{project['id']}/tasks"
    pattern = f"tasks:project:{project['id']}:*"

    # Nạp cache (2 task)
    res_before = await api_client.get(list_url, headers=headers)
    assert res_before.json()["total"] == 2
    assert len([k async for k in fake_redis.scan_iter(pattern)]) == 1

    # Xóa t1 -> cache bị xóa
    del_res = await api_client.delete(f"{TASKS_URL}/{t1['id']}", headers=headers)
    assert del_res.status_code == 204
    assert len([k async for k in fake_redis.scan_iter(pattern)]) == 0

    # Gọi lại GET -> chỉ còn t2
    res_after = await api_client.get(list_url, headers=headers)
    assert res_after.status_code == 200
    assert res_after.json()["total"] == 1
    assert res_after.json()["items"][0]["id"] == t2["id"]


async def test_cache_invalidation_isolated_between_projects(
    api_client,
    active_user,
    fake_redis,
):
    """Thay đổi task ở Project 1 không làm mất cache của Project 2."""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    p1 = await _create_sample_project(api_client, headers, ws["id"], "Project 1")
    p2 = await _create_sample_project(api_client, headers, ws["id"], "Project 2")

    await _create_sample_task(api_client, headers, p1["id"], "Task P1")
    await _create_sample_task(api_client, headers, p2["id"], "Task P2")

    # Nạp cache cho cả 2 project
    await api_client.get(f"{PROJECTS_URL}/{p1['id']}/tasks", headers=headers)
    await api_client.get(f"{PROJECTS_URL}/{p2['id']}/tasks", headers=headers)

    assert (
        len([k async for k in fake_redis.scan_iter(f"tasks:project:{p1['id']}:*")]) == 1
    )
    assert (
        len([k async for k in fake_redis.scan_iter(f"tasks:project:{p2['id']}:*")]) == 1
    )

    # Thêm task mới vào p1 -> chỉ cache của p1 bị xóa, cache của p2 vẫn giữ nguyên
    await _create_sample_task(api_client, headers, p1["id"], "Another Task P1")

    assert (
        len([k async for k in fake_redis.scan_iter(f"tasks:project:{p1['id']}:*")]) == 0
    )
    assert (
        len([k async for k in fake_redis.scan_iter(f"tasks:project:{p2['id']}:*")]) == 1
    )


async def test_cache_hit_still_enforces_workspace_permission(
    api_client,
    active_user,
    other_user,
    fake_redis,
):
    """Ngay cả khi dữ liệu đã nằm trong Redis, người ngoài workspace vẫn bị chặn 403."""
    owner_headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, owner_headers)
    project = await _create_sample_project(api_client, owner_headers, ws["id"])
    await _create_sample_task(api_client, owner_headers, project["id"], "Secret Task")

    list_url = f"{PROJECTS_URL}/{project['id']}/tasks"

    # Owner nạp cache
    res_owner = await api_client.get(list_url, headers=owner_headers)
    assert res_owner.status_code == 200
    assert (
        len([k async for k in fake_redis.scan_iter(f"tasks:project:{project['id']}:*")])
        == 1
    )

    # Người không thuộc workspace gọi vào -> vẫn trả 403
    other_headers = await get_auth_headers(api_client, other_user)
    res_other = await api_client.get(list_url, headers=other_headers)
    assert res_other.status_code == 403


async def test_redis_down_fallback_on_read_and_write(
    api_client,
    active_user,
):
    """Giả lập Redis sập -> đọc (GET) và ghi (POST/PATCH/DELETE) vẫn hoạt động bình thường."""
    headers = await get_auth_headers(api_client, active_user)
    ws = await _create_sample_workspace(api_client, headers)
    project = await _create_sample_project(api_client, headers, ws["id"])
    task = await _create_sample_task(api_client, headers, project["id"], "Task 1")

    broken_redis = AsyncMock()
    broken_redis.get.side_effect = RedisError("Connection refused")
    broken_redis.set.side_effect = RedisError("Connection refused")

    async def broken_scan_iter(*args, **kwargs):
        raise RedisError("Connection refused")
        yield

    broken_redis.scan_iter = broken_scan_iter
    previous_override = app.dependency_overrides.get(get_redis)
    app.dependency_overrides[get_redis] = lambda: broken_redis

    try:
        # GET fallback về DB
        get_res = await api_client.get(
            f"{PROJECTS_URL}/{project['id']}/tasks",
            headers=headers,
        )
        assert get_res.status_code == 200
        assert get_res.json()["total"] == 1

        # POST, PATCH, DELETE không bị crash khi invalidate Redis lỗi
        create_res = await api_client.post(
            f"{PROJECTS_URL}/{project['id']}/tasks",
            headers=headers,
            json={"title": "Task 2"},
        )
        assert create_res.status_code == 201

        patch_res = await api_client.patch(
            f"{TASKS_URL}/{task['id']}",
            headers=headers,
            json={"title": "Task 1 Updated"},
        )
        assert patch_res.status_code == 200

        del_res = await api_client.delete(
            f"{TASKS_URL}/{task['id']}",
            headers=headers,
        )
        assert del_res.status_code == 204
    finally:
        if previous_override is not None:
            app.dependency_overrides[get_redis] = previous_override
        else:
            app.dependency_overrides.pop(get_redis, None)
