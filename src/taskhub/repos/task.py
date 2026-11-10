from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import Task

from .base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Task)
