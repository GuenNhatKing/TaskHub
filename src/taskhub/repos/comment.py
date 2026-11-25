import uuid
from select import select

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import Comment

from .base import BaseRepository, Page


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Comment)

    async def get_by_task_id(
        self,
        task_id: uuid.UUID,
        page: int,
        page_size: int,
    ) -> Page[Comment]:
        conditions = [Comment.task_id == task_id]

        total: int = (
            await self.db.execute(
                select(func.count()).select_from(Comment).where(*conditions)
            )
        ).scalar_one()

        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        stmt = (
            select(Comment)
            .where(*conditions)
            .order_by(Comment.created_at.asc())
            .offset(offset)
            .limit(page_size)
        )
        items = list((await self.db.execute(stmt)).scalars().all())

        return Page[Comment](
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
