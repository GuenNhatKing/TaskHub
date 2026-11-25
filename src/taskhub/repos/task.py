import uuid

from sqlalchemy import func, select
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
        conditions = [Task.project_id == project_id]

        if status is not None:
            conditions.append(Task.status == status)
        if priority is not None:
            conditions.append(Task.priority == priority)
        if assignee_id is not None:
            conditions.append(Task.assignee_id == assignee_id)
        if search:
            # Tìm kiếm gần đúng như là theo title
            conditions.append(Task.title.ilike(f"%{search.strip()}%"))

        total: int = (
            await self.db.execute(
                select(func.count()).select_from(Task).where(*conditions)
            )
        ).scalar_one()

        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        stmt = (
            select(Task)
            .where(*conditions)
            .order_by(Task.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list((await self.db.execute(stmt)).scalars().all())

        return Page[Task](
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
