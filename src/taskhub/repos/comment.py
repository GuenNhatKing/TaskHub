import uuid

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
        return await self.get_with_pagination(
            page=page,
            page_size=page_size,
            order_by=[
                Comment.created_at.asc(),
                Comment.id.asc(),
            ],  # Lấy comment từ cũ nhất trước, để hiểu hết luồng hội thoại
            conditions=[Comment.task_id == task_id],
        )
