from __future__ import annotations

import logging
import time
from collections.abc import Mapping
from typing import Any

from app.ai.embeddings.dto import EmbeddedChunk
from app.ai.vectorstores.dto import VectorSearchResult
from app.ai.vectorstores.protocols import VectorStore
from app.ai.vectorstores.qdrant.mapper import QdrantMapper


logger = logging.getLogger(__name__)


class VectorStoreService:

    def __init__(
        self,
        repository: VectorStore,
    ) -> None:

        self._repository = repository

        logger.info(
            "Vector store service initialized repository=%s",
            repository.__class__.__name__,
        )


    async def upsert_embeddings(
        self,
        chunks: list[EmbeddedChunk],
    ) -> None:

        if not chunks:

            logger.warning(
                "Skip vector upsert empty chunks",
            )

            return


        started = time.perf_counter()

        logger.info(
            "Preparing vector upsert chunks=%s",
            len(chunks),
        )


        points = [
            QdrantMapper.to_vector_point(
                chunk,
            )
            for chunk in chunks
        ]


        await self._repository.upsert(
            points,
        )


        elapsed = (
            time.perf_counter()
            - started
        )

        logger.info(
            "Vector upsert completed points=%s time=%.3fs",
            len(points),
            elapsed,
        )


    async def search(
        self,
        vector: tuple[float, ...],
        limit: int,
        filters: Mapping[str, Any] | None = None,
    ) -> list[VectorSearchResult]:

        started = time.perf_counter()

        logger.info(
            "Vector search started limit=%s dimension=%s",
            limit,
            len(vector),
        )

        logger.debug(
            "Vector search filters=%s",
            filters,
        )


        try:

            results = await self._repository.search(
                vector=vector,
                limit=limit,
                filters=filters,
            )


            elapsed = (
                time.perf_counter()
                - started
            )


            logger.info(
                "Vector search completed results=%s time=%.3fs",
                len(results),
                elapsed,
            )


            return results


        except Exception:

            logger.exception(
                "Vector search service failed",
            )

            raise



    async def delete_document(
        self,
        document_id: int,
    ) -> None:

        logger.info(
            "Deleting document vectors document_id=%s",
            document_id,
        )


        await self._repository.delete_document(
            document_id,
        )


        logger.info(
            "Document vectors deleted document_id=%s",
            document_id,
        )


    async def delete_user_documents(
        self,
        user_id: int,
    ) -> None:

        logger.info(
            "Deleting user vectors user_id=%s",
            user_id,
        )


        await self._repository.delete_user_documents(
            user_id,
        )


        logger.info(
            "User vectors deleted user_id=%s",
            user_id,
        )


    async def healthcheck(
        self,
    ) -> bool:

        logger.info(
            "Vector store healthcheck started",
        )


        try:

            result = await self._repository.healthcheck()


            if result:

                logger.info(
                    "Vector store healthcheck passed",
                )

            else:

                logger.warning(
                    "Vector store healthcheck failed",
                )


            return result


        except Exception:

            logger.exception(
                "Vector store healthcheck error",
            )

            return False