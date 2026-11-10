from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import TaskLabel

from .base import BaseRepository


class TaskLabelRepository(BaseRepository[TaskLabel]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=TaskLabel)
