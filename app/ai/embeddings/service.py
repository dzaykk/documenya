from __future__ import annotations

import logging
from time import perf_counter

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

        logger.info(
            "Embedding service initialized provider=%s",
            provider.__class__.__name__,
        )


    async def embed_documents(
        self,
        request: EmbeddingRequest,
    ) -> list[EmbeddedChunk]:

        chunks_count = len(
            request.chunks,
        )


        logger.info(
            "Document embedding started provider=%s chunks=%s",
            self._provider.__class__.__name__,
            chunks_count,
        )


        started_at = perf_counter()


        try:

            result = await self._provider.embed_documents(
                request,
            )


            elapsed = (
                perf_counter() - started_at
            )


            logger.info(
                "Document embedding completed chunks=%s vectors=%s elapsed=%.3fs",
                chunks_count,
                len(result),
                elapsed,
            )


            return result


        except Exception as exc:

            logger.exception(
                "Document embedding failed",
            )


            raise EmbeddingProviderError(
                "Embedding generation failed",
            ) from exc



    async def embed_query(
        self,
        text: str,
    ) -> tuple[float, ...]:

        logger.info(
            "Query embedding started provider=%s text_length=%s",
            self._provider.__class__.__name__,
            len(text),
        )


        started_at = perf_counter()


        try:

            vector = await self._provider.embed_query(
                text,
            )


            result = tuple(
                vector,
            )


            elapsed = (
                perf_counter() - started_at
            )


            logger.info(
                "Query embedding completed dimension=%s elapsed=%.3fs",
                len(result),
                elapsed,
            )


            return result


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

        logger.info(
            "Embedding healthcheck started provider=%s",
            self._provider.__class__.__name__,
        )


        try:

            result = await self._provider.healthcheck()


            if result:

                logger.info(
                    "Embedding healthcheck passed",
                )

            else:

                logger.warning(
                    "Embedding healthcheck failed",
                )


            return result


        except Exception:

            logger.exception(
                "Embedding healthcheck error",
            )

            return False