from __future__ import annotations

from typing import Protocol

from app.embeddings.dto import (
    EmbeddedChunk,
    EmbeddingRequest,
)


class EmbeddingProvider(Protocol):
    async def embed_documents(
        self,
        request: EmbeddingRequest,
    ) -> list[EmbeddedChunk]:
        ...

    async def embed_query(
        self,
        text: str,
    ) -> list[float]:
        ...

    async def healthcheck(
        self,
    ) -> bool:
        ...