from __future__ import annotations

import logging

from app.ai.chunking.dto import (
    ChunkMetadata,
    DocumentChunk,
)
from app.ai.embeddings.service import EmbeddingService
from app.ai.retrieval.dto import (
    RetrievalRequest,
    RetrievalResult,
    RetrievedChunk,
)
from app.ai.vectorstores.protocols import VectorStore

logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(
        self,
        embeddings: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        self._embeddings = embeddings
        self._vector_store = vector_store

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResult:

        logger.info(
            "Retrieving context owner_id=%s top_k=%s",
            request.owner_id,
            request.top_k,
        )

        embedding = await self._embeddings.embed_query(
            request.query,
        )

        results = await self._vector_store.search(
            vector=embedding,
            limit=request.top_k,
        )

        chunks: list[RetrievedChunk] = []

        for result in results:
            payload = result.payload

            if payload.get("owner_id") != request.owner_id:
                continue

            if result.score < request.similarity_threshold:
                continue

            chunks.append(
                RetrievedChunk(
                    chunk=DocumentChunk(
                        id=result.id,
                        document_id=payload["document_id"],
                        text=payload["text"],
                        metadata=ChunkMetadata(
                            document_id=payload["document_id"],
                            owner_id=payload["owner_id"],
                            chunk_index=payload["chunk_index"],
                            page=payload.get("page"),
                            title=payload.get("title"),
                            section=payload.get("section"),
                        ),
                    ),
                    score=result.score,
                )
            )

        logger.info(
            "Retrieved %d chunks",
            len(chunks),
        )

        return RetrievalResult(
            chunks=chunks,
        )