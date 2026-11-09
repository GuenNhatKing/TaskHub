from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import Workspace

from .base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Workspace)
