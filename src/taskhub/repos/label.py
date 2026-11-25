import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import Label, TaskLabel

from .base import BaseRepository


class LabelRepository(BaseRepository[Label]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Label)

    async def get_by_project_id(self, project_id: uuid.UUID) -> list[Label]:
        stmt = (
            select(Label)
            .where(Label.project_id == project_id)
            .order_by(Label.name.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_project_and_name(
        self, project_id: uuid.UUID, name: str
    ) -> Label | None:
        stmt = select(Label).where(
            Label.project_id == project_id,
            func.lower(Label.name) == name.lower(),  # So sánh lower
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_task_id(self, task_id: uuid.UUID) -> list[Label]:
        stmt = (
            select(Label)
            .join(TaskLabel, TaskLabel.label_id == Label.id)
            .where(TaskLabel.task_id == task_id)
            .order_by(Label.name.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
