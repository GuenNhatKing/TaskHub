import uuid

from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from taskhub.core.enums import ProjectStatus
from taskhub.models import Project

from .base import BaseRepository, Page


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Project)

    async def get_by_workspace_id(
        self,
        workspace_id: uuid.UUID,
        status: ProjectStatus | None = None,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Page[Project]:
        conditions: list[ColumnElement[bool]] = [Project.workspace_id == workspace_id]
        if status is not None:
            conditions.append(Project.status == status)

        return await self.get_with_pagination(
            page=page,
            page_size=page_size,
            order_by=[Project.created_at.desc(), Project.id.desc()],
            conditions=conditions,
        )
