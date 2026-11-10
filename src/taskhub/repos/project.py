from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import Project

from .base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Project)
