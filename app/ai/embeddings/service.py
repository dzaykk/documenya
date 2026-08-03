from __future__ import annotations

import logging

from app.ai.embeddings.dto import (
    EmbeddedChunk,
    EmbeddingRequest,
)
from app.ai.embeddings.exceptions import (
    EmbeddingProviderError,
)
from app.ai.embeddings.protocols import (
    EmbeddingProvider,
)

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(
        self,
        provider: EmbeddingProvider,
    ) -> None:
        self._provider = provider

    async def embed_documents(
        self,
        request: EmbeddingRequest,
    ) -> list[EmbeddedChunk]:
        logger.info(
            "Embedding %d document chunks",
            len(request.chunks),
        )

        try:
            result = await self._provider.embed_documents(
                request,
            )

            logger.info(
                "Embedded %d chunks successfully",
                len(result),
            )

            return result

        except Exception as exc:
            logger.exception(
                "Embedding documents failed",
            )

            raise EmbeddingProviderError(
                "Embedding generation failed",
            ) from exc

    async def embed_query(
        self,
        text: str,
    ) -> tuple[float, ...]:

        logger.debug(
            "Embedding query length=%d",
            len(text),
        )

        try:
            vector = await self._provider.embed_query(
                text,
            )

            return tuple(vector)

        except Exception as exc:
            logger.exception(
                "Query embedding failed",
            )

            raise EmbeddingProviderError(
                "Query embedding failed",
            ) from exc

    async def healthcheck(
        self,
    ) -> bool:
        return await self._provider.healthcheck()