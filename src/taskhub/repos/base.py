from typing import Any, TypeVar

from pydantic.dataclasses import dataclass
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskhub.models import Base

T = TypeVar("T", bound=Base)


@dataclass
class Page[T]:
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


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

        await self.db.flush()

        return instance

    async def delete(self, instance: T) -> None:
        await self.db.delete(instance)
        await self.db.flush()

    # Phải chỉ định order_by, nên là created_at
    async def get_with_pagination(
        self, page: int, page_size: int, order_by: Any = None
    ) -> Page[T]:
        if not order_by:
            raise ValueError("Phải chỉ định kiểu order_by")
        if page < 1 or page_size < 1:
            raise ValueError("page và page_size phải lớn hơn 1")

        total: int = (
            await self.db.execute(select(func.count()).select_from(self.model))
        ).scalar_one()

        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        items_raw = await self.db.execute(
            select(self.model).order_by(order_by).offset(offset).limit(page_size)
        )
        items = list(items_raw.scalars().all())

        result: Page[T] = {
            items: items,
            total: total,
            page: page,
            page_size: page_size,
            total_pages: total_pages,
        }
        return result
