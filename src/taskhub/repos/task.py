import uuid

from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.core.enums import Priority, TaskStatus
from taskhub.models import Task

from .base import BaseRepository, Page


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Task)

    async def get_by_project_id(
        self,
        project_id: uuid.UUID,
        page: int,
        page_size: int,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
        assignee_id: uuid.UUID | None = None,
        search: str | None = None,
    ) -> Page[Task]:
        conditions: list[ColumnElement[bool]] = [Task.project_id == project_id]

        if status is not None:
            conditions.append(Task.status == status)
        if priority is not None:
            conditions.append(Task.priority == priority)
        if assignee_id is not None:
            conditions.append(Task.assignee_id == assignee_id)
        if search and search.strip():
            # Tìm kiếm gần đúng theo title
            conditions.append(Task.title.ilike(f"%{search.strip()}%"))

        return await self.get_with_pagination(
            page=page,
            page_size=page_size,
            order_by=[Task.created_at.desc(), Task.id.desc()],
            conditions=conditions,
        )
