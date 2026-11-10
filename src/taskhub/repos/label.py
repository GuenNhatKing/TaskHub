from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import Label

from .base import BaseRepository


class LabelRepository(BaseRepository[Label]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Label)
