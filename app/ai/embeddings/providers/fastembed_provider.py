from __future__ import annotations

import asyncio
import logging
from functools import cached_property

from fastembed import TextEmbedding

from app.core.config import settings
from app.embeddings.dto import (
    EmbeddedChunk,
    EmbeddingRequest,
)
from app.embeddings.protocols import EmbeddingProvider

logger = logging.getLogger(__name__)


class FastEmbedProvider(EmbeddingProvider):
    @cached_property
    def model(self) -> TextEmbedding:

        logger.info(
            "Loading embedding model '%s'...",
            settings.EMBEDDING_MODEL,
        )

        model = TextEmbedding(
            model_name=settings.EMBEDDING_MODEL,
        )

        logger.info(
            "Embedding model loaded.",
        )

        return model

    async def embed_documents(
        self,
        request: EmbeddingRequest,
    ) -> list[EmbeddedChunk]:

        texts = [
            chunk.text
            for chunk in request.chunks
        ]

        vectors = await asyncio.to_thread(
            lambda: list(
                self.model.embed(
                    texts,
                    batch_size=request.batch_size
                    or settings.EMBEDDING_BATCH_SIZE,
                )
            )
        )

        return [
            EmbeddedChunk(
                chunk=chunk,
                vector=tuple(vector),
            )
            for chunk, vector in zip(
                request.chunks,
                vectors,
                strict=True,
            )
        ]

    async def embed_query(
        self,
        text: str,
    ) -> list[float]:

        vector = await asyncio.to_thread(
            lambda: next(
                self.model.embed(
                    [text],
                )
            )
        )

        return list(vector)

    async def healthcheck(
        self,
    ) -> bool:

        try:
            await self.embed_query(
                "healthcheck",
            )
            return True

        except Exception:
            logger.exception(
                "Embedding provider healthcheck failed.",
            )
            return False