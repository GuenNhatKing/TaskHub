from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import WorkspaceMember

from .base import BaseRepository


class WorkspaceMemberRepository(BaseRepository[WorkspaceMember]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=WorkspaceMember)
