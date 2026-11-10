from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import Comment

from .base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Comment)
