from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chunk_repository import (
    ChunkRepository,
)
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.repositories.user_repository import (
    UserRepository,
)

from .base import AbstractUnitOfWork


class SQLAlchemyUnitOfWork(
    AbstractUnitOfWork,
):
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.users = UserRepository(
            session,
        )
        self.documents = DocumentRepository(
            session,
        )
        self.chunks = ChunkRepository(
            session,
        )

    async def __aenter__(
        self,
    ):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):

        if exc_type:
            await self.rollback()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()