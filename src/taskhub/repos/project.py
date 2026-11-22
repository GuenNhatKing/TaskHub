import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.core.enums import ProjectStatus
from taskhub.models import Project

from .base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Project)

    async def get_by_workspace_id(
        self, workspace_id: uuid.UUID, status: ProjectStatus | None = None
    ) -> list[Project]:
        stmt = select(self.model).where(self.model.workspace_id == workspace_id)
        if status is not None:
            stmt = stmt.where(self.model.status == status)
        result = await self.db.execute(stmt)
        projects = list(result.scalars().all())
        return projects
