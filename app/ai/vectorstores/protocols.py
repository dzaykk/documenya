from __future__ import annotations

from typing import Protocol

from app.ai.vectorstores.dto import (
    VectorPoint,
    VectorSearchResult,
)


class VectorStore(Protocol):
    async def upsert(
        self,
        points: list[VectorPoint],
    ) -> None:
        ...

    async def search(
        self,
        vector: tuple[float, ...],
        limit: int,
    ) -> list[VectorSearchResult]:
        ...

    async def delete_document(
        self,
        document_id: int,
    ) -> None:
        ...

    async def delete_user_documents(
        self,
        user_id: int,
    ) -> None:
        ...

    async def healthcheck(
        self,
    ) -> bool:
        ...