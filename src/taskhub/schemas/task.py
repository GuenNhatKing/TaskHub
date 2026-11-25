import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from taskhub.core.enums import Priority, TaskStatus
from taskhub.core.validators import (
    AwareDatetime,
    NotNull,
    ValidDescription,
    ValidTaskTitle,
)
from taskhub.schemas.base import BaseRequest


class TaskCreateRequest(BaseRequest):
    title: ValidTaskTitle
    description: ValidDescription | None = None
    assignee_id: uuid.UUID | None = None
    priority: Priority = Priority.MEDIUM
    due_date: AwareDatetime | None = None


class TaskUpdateRequest(BaseRequest):
    title: NotNull[ValidTaskTitle | None] = None
    description: ValidDescription | None = None
    assignee_id: uuid.UUID | None = None
    status: NotNull[TaskStatus | None] = None
    priority: NotNull[Priority | None] = None
    due_date: AwareDatetime | None = None


class TaskAssignRequest(BaseRequest):
    assignee_id: uuid.UUID | None


class TaskStatusUpdateRequest(BaseRequest):
    status: TaskStatus


class TaskResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    assignee_id: uuid.UUID | None
    title: str
    description: str | None
    status: TaskStatus
    priority: Priority
    due_date: AwareDatetime | None
    created_by: uuid.UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
