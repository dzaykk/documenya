from __future__ import annotations

from typing import Protocol

from app.vectorstores.dto import (
    VectorPoint,
    VectorSearchResult,
)


class VectorStore(Protocol):
    async def upsert(
        self,
        collection: str,
        points: list[VectorPoint],
    ) -> None:
        ...

    async def search(
        self,
        collection: str,
        vector: list[float],
        limit: int,
    ) -> list[VectorSearchResult]:
        ...

    async def delete_document(
        self,
        collection: str,
        document_id: int,
    ) -> None:
        ...

    async def healthcheck(
        self,
    ) -> bool:
        ...