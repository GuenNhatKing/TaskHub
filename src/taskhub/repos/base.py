from typing import Any, TypeVar

from pydantic.dataclasses import dataclass
from sqlalchemy import ColumnElement, Sequence, func, select
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
        # Tìm theo primary key, bất kể tên cột là gì
        return await self.db.get(self.model, id)

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
        self,
        page: int,
        page_size: int,
        order_by: Sequence[ColumnElement[Any]],
        conditions: Sequence[ColumnElement[bool]] | None = None,
    ) -> Page[T]:
        if not order_by:
            raise ValueError("Phải chỉ định ít nhất một điều kiện order_by")
        if page < 1 or page_size < 1:
            raise ValueError("page và page_size phải lớn hơn hoặc bằng 1")

        where_clauses = conditions or ()

        count_stmt = select(func.count()).select_from(self.model).where(*where_clauses)
        total: int = (await self.db.execute(count_stmt)).scalar_one()

        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        items_stmt = (
            select(self.model)
            .where(*where_clauses)
            .order_by(*order_by)
            .offset(offset)
            .limit(page_size)
        )
        items = list((await self.db.execute(items_stmt)).scalars().all())

        return Page[T](
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
