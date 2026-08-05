from __future__ import annotations

import logging
import time

from app.ai.context.builder import ContextBuilder
from app.ai.llm.service import LLMService
from app.ai.prompts.rag import build_rag_messages
from app.ai.query.dto import (
    QueryRequest,
    QueryResponse,
)
from app.ai.retrieval.dto import RetrievalRequest
from app.ai.retrieval.service import RetrievalService
from app.core.config import settings


logger = logging.getLogger(__name__)


class QueryService:

    def __init__(
        self,
        retrieval: RetrievalService,
        context_builder: ContextBuilder,
        llm: LLMService,
    ) -> None:

        self._retrieval = retrieval
        self._context_builder = context_builder
        self._llm = llm


    async def ask(
        self,
        request: QueryRequest,
    ) -> QueryResponse:

        started = time.perf_counter()

        logger.info(
            "Processing query owner_id=%s",
            request.owner_id,
        )

        logger.debug(
            "Question length=%s",
            len(request.question),
        )

        try:

            retrieval_started = time.perf_counter()

            retrieval = await self._retrieval.retrieve(
                RetrievalRequest(
                    query=request.question,
                    owner_id=request.owner_id,
                    top_k=settings.TOP_K,
                    similarity_threshold=(
                        settings.SIMILARITY_THRESHOLD
                    ),
                ),
            )

            retrieval_time = (
                time.perf_counter()
                - retrieval_started
            )

            logger.info(
                "Retrieval completed chunks=%s time=%.3fs",
                len(retrieval.chunks),
                retrieval_time,
            )


            if not retrieval.chunks:

                logger.warning(
                    "No relevant context found owner_id=%s",
                    request.owner_id,
                )

                return QueryResponse(
                    answer=(
                        "I couldn't find relevant information "
                        "in your uploaded documents."
                    ),
                    sources=[],
                )


            context = self._context_builder.build(
                retrieval,
            )

            logger.debug(
                "Context built characters=%s",
                len(context),
            )


            messages = build_rag_messages(
                question=request.question,
                context=context,
            )

            logger.info(
                "Sending generation request messages=%s",
                len(messages),
            )


            llm_started = time.perf_counter()

            generation = await self._llm.generate(
                messages=messages,
            )

            llm_time = (
                time.perf_counter()
                - llm_started
            )


            sources = sorted(
                {
                    item.chunk.document_id
                    for item in retrieval.chunks
                },
            )


            logger.info(
                (
                    "Generation completed "
                    "tokens=%s time=%.3fs sources=%s"
                ),
                generation.usage.total_tokens,
                llm_time,
                len(sources),
            )


            total_time = (
                time.perf_counter()
                - started
            )

            logger.info(
                "Query pipeline finished time=%.3fs",
                total_time,
            )


            return QueryResponse(
                answer=generation.answer,
                sources=sources,
            )


        except Exception:

            logger.exception(
                "Query pipeline failed owner_id=%s",
                request.owner_id,
            )

            raise