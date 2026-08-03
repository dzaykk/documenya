from __future__ import annotations

from app.ai.embeddings.dto import EmbeddedChunk
from app.ai.vectorstores.dto import VectorSearchResult
from app.ai.vectorstores.protocols import VectorStore
from app.ai.vectorstores.qdrant.mapper import QdrantMapper


class VectorStoreService:
    def __init__(
        self,
        repository: VectorStore,
    ) -> None:
        self._repository = repository

    async def upsert_embeddings(
        self,
        chunks: list[EmbeddedChunk],
    ) -> None:

        if not chunks:
            return

        points = [
            QdrantMapper.to_vector_point(
                chunk,
            )
            for chunk in chunks
        ]

        await self._repository.upsert(
            points,
        )

    async def search(
        self,
        vector: tuple[float, ...],
        limit: int,
    ) -> list[VectorSearchResult]:

        return await self._repository.search(
            vector,
            limit,
        )

    async def delete_document(
        self,
        document_id: int,
    ) -> None:

        await self._repository.delete_document(
            document_id,
        )

    async def delete_user_documents(
        self,
        user_id: int,
    ) -> None:

        await self._repository.delete_user_documents(
            user_id,
        )

    async def healthcheck(
        self,
    ) -> bool:

        return await self._repository.healthcheck()