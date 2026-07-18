from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        document: Document,
    ) -> Document:
        self.session.add(document)

        await self.session.flush()
        await self.session.refresh(document)

        return document

    async def get_by_id(
        self,
        document_id: int,
    ) -> Document | None:
        result = await self.session.execute(
            select(Document).where(
                Document.id == document_id
            )
        )

        return result.scalar_one_or_none()

    async def get_user_documents(
        self,
        user_id: int,
    ) -> list[Document]:

        result = await self.session.execute(
            select(Document)
            .where(Document.owner_id == user_id)
            .order_by(Document.created_at.desc())
        )

        return list(result.scalars().all())

    async def delete(
        self,
        document: Document,
    ) -> None:
        await self.session.delete(document)