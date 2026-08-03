from collections.abc import Sequence

from sqlalchemy import delete, func, or_, select

from app.models.document import Document
from app.repositories.base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    async def get_by_id(
        self,
        document_id: int,
    ) -> Document | None:

        result = await self.session.execute(
            select(Document).where(
                Document.id == document_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id_and_owner(
        self,
        document_id: int,
        owner_id: int,
    ) -> Document | None:

        result = await self.session.execute(
            select(Document).where(
                Document.id == document_id,
                Document.owner_id == owner_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_file_paths_by_owner(
        self,
        owner_id: int,
    ) -> Sequence[str]:

        result = await self.session.execute(
            select(Document.file_path).where(
                Document.owner_id == owner_id,
            )
        )

        return result.scalars().all()

    async def get_user_documents(
        self,
        user_id: int,
        search: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> list[Document]:

        query = (
            select(Document)
            .where(Document.owner_id == user_id)
        )

        if search:
            query = query.where(
                or_(
                    Document.title.ilike(f"%{search}%"),
                    Document.content.ilike(f"%{search}%"),
                )
            )

        query = (
            query
            .order_by(Document.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def count_user_documents(
        self,
        user_id: int,
        search: str | None = None,
    ) -> int:

        query = (
            select(func.count(Document.id))
            .where(Document.owner_id == user_id)
        )

        if search:
            query = query.where(
                or_(
                    Document.title.ilike(f"%{search}%"),
                    Document.content.ilike(f"%{search}%"),
                )
            )

        result = await self.session.execute(query)

        return result.scalar_one()

    async def delete_all_by_owner_id(
        self,
        owner_id: int,
    ) -> int:

        result = await self.session.execute(
            delete(Document).where(
                Document.owner_id == owner_id,
            )
        )

        return result.rowcount