from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import Base

T = TypeVar("T", bound=Base)

class BaseRepository[T: Base]:
    def __init__(self, db: AsyncSession, model: type[T]):
        self.db = db
        self.model = model

    # Dùng Any để cho đối tượng có 1 id hoặc nhiều id 
    async def get_by_id(self, id: Any) -> T | None:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[T]:
        result = await self.db.execute(select(self.model))
        return list(result.scalars().all())

    async def create(self, data: dict) -> T:
        instance = self.model(**data)

        self.db.add(instance)
        await self.db.flush()

        return instance

    async def update(
        self,
        instance: T,
        data: dict,
    ) -> T:
        for key, value in data.items():
            setattr(instance, key, value)

        await self.session.flush()

        return instance

    async def delete(self, instance: T) -> None:
        await self.session.delete(instance)
        await self.session.flush()


    
        

