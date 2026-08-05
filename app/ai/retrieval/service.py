from __future__ import annotations

import logging
import time

from app.ai.embeddings.service import (
    EmbeddingService,
)
from app.ai.retrieval.dto import (
    RetrievalRequest,
    RetrievalResult,
)
from app.ai.retrieval.mapper import (
    RetrievalMapper,
)
from app.ai.vectorstores.service import (
    VectorStoreService,
)


logger = logging.getLogger(__name__)


class RetrievalService:

    def __init__(
        self,
        embeddings: EmbeddingService,
        vector_store: VectorStoreService,
    ) -> None:

        self._embeddings = embeddings
        self._vector_store = vector_store

        logger.info(
            "Retrieval service initialized",
        )


    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResult:

        started = time.perf_counter()

        logger.info(
            (
                "Retrieval started "
                "owner_id=%s top_k=%s threshold=%.3f"
            ),
            request.owner_id,
            request.top_k,
            request.similarity_threshold,
        )

        logger.debug(
            "Query length=%s",
            len(request.query),
        )


        try:

            embedding_started = time.perf_counter()

            query_vector = await self._embeddings.embed_query(
                request.query,
            )

            embedding_time = (
                time.perf_counter()
                - embedding_started
            )

            logger.info(
                "Query embedding generated dimension=%s time=%.3fs",
                len(query_vector),
                embedding_time,
            )


            search_started = time.perf_counter()

            results = await self._vector_store.search(
                vector=query_vector,
                limit=request.top_k,
                filters={
                    "owner_id": request.owner_id,
                },
            )

            search_time = (
                time.perf_counter()
                - search_started
            )

            logger.info(
                "Vector search completed results=%s time=%.3fs",
                len(results),
                search_time,
            )


            if results:

                scores = [
                    result.score
                    for result in results
                ]

                logger.debug(
                    (
                        "Vector scores "
                        "min=%.4f max=%.4f avg=%.4f top=%.4f"
                    ),
                    min(scores),
                    max(scores),
                    sum(scores) / len(scores),
                    max(scores),
                )


            chunks = [
                RetrievalMapper.to_retrieved_chunk(
                    result,
                )
                for result in results
                if result.score >= request.similarity_threshold
            ]


            logger.info(
                (
                    "Retrieval completed "
                    "accepted=%s filtered=%s"
                ),
                len(chunks),
                len(results) - len(chunks),
            )


            total_time = (
                time.perf_counter()
                - started
            )

            logger.info(
                "Retrieval pipeline finished time=%.3fs",
                total_time,
            )


            return RetrievalResult(
                chunks=chunks,
            )


        except Exception:

            logger.exception(
                "Retrieval failed owner_id=%s",
                request.owner_id,
            )

            raise