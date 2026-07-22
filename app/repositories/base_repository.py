from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        obj: ModelType,
    ) -> ModelType:

        self.session.add(obj)

        await self.session.commit()
        await self.session.refresh(obj)

        return obj

    async def update(
        self,
        obj: ModelType,
    ) -> ModelType:

        await self.session.commit()
        await self.session.refresh(obj)

        return obj

    async def delete(
        self,
        obj: ModelType,
    ) -> None:

        await self.session.delete(obj)
        await self.session.commit()