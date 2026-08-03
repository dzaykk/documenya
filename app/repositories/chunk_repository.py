from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select

from app.models.chunk import DocumentChunk
from app.repositories.base_repository import BaseRepository


class ChunkRepository(
    BaseRepository[DocumentChunk],
):

    async def get_document_chunks(
        self,
        document_id: int,
    ) -> list[DocumentChunk]:

        result = await self.session.execute(
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
            )
            .order_by(
                DocumentChunk.chunk_index.asc(),
            )
        )

        return list(
            result.scalars().all()
        )


    async def delete_document_chunks(
        self,
        document_id: int,
    ) -> None:

        await self.session.execute(
            delete(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
            )
        )


    async def create_many(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        self.session.add_all(
            chunks,
        )

        await self.session.flush()

        for chunk in chunks:
            await self.session.refresh(
                chunk,
            )

        return chunks


    async def update_vector_ids(
        self,
        mapping: dict[UUID, str],
    ) -> None:

        if not mapping:
            return

        mappings = [
            {"id": chunk_id, "vector_id": vector_id}
            for chunk_id, vector_id in mapping.items()
        ]

        await self.session.run_sync(
            lambda sync_session: sync_session.bulk_update_mappings(
                DocumentChunk,
                mappings,
            )
        )

        await self.session.flush()