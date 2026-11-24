import uuid

from sqlalchemy import func, select
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
        stmt = select(self.model).where(self.model.workspace_id == workspace_id)
        if status is not None:
            stmt = stmt.where(self.model.status == status)

        # Đếm tổng số bản ghi khớp điều kiện
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total: int = (await self.db.execute(count_stmt)).scalar_one()

        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        # Sắp xếp và phân trang
        stmt = (
            stmt.order_by(self.model.created_at.desc(), self.model.id.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return Page[Project](
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
