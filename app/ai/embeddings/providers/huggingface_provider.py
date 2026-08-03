from __future__ import annotations

import asyncio
import logging
from functools import cached_property
from typing import cast

import torch
from sentence_transformers import SentenceTransformer

from app.ai.embeddings.dto import (
    EmbeddedChunk,
    EmbeddingRequest,
)
from app.ai.embeddings.protocols import EmbeddingProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class HuggingFaceEmbeddingProvider(EmbeddingProvider):

    def _resolve_device(self) -> str:
        if settings.EMBEDDING_DEVICE != "auto":
            logger.info(
                "Using configured embedding device: %s",
                settings.EMBEDDING_DEVICE,
            )

            return settings.EMBEDDING_DEVICE

        if torch.cuda.is_available():
            logger.info(
                "CUDA detected, using GPU for embeddings",
            )

            return "cuda"

        logger.info(
            "CUDA unavailable, using CPU for embeddings",
        )

        return "cpu"


    @cached_property
    def model(
        self,
    ) -> SentenceTransformer:

        device = self._resolve_device()

        logger.info(
            "Loading embedding model '%s' on '%s'",
            settings.EMBEDDING_MODEL,
            device,
        )

        model = cast(
            SentenceTransformer,
            SentenceTransformer(
                settings.EMBEDDING_MODEL,
                device=device,
            ),
        )

        logger.info(
            "Embedding model loaded on '%s'",
            device,
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

        batch_size = (
            request.batch_size
            if request.batch_size is not None
            else settings.EMBEDDING_BATCH_SIZE
        )

        logger.debug(
            "Embedding %s chunks with batch size %s",
            len(texts),
            batch_size,
        )

        vectors = await asyncio.to_thread(
            lambda: self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
            ),
        )

        return [
            EmbeddedChunk(
                chunk=chunk,
                vector=tuple(
                    vector.tolist(),
                ),
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
    ) -> tuple[float, ...]:

        logger.debug(
            "Embedding query length=%s",
            len(text),
        )

        vector = await asyncio.to_thread(
            lambda: self.model.encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True,
            ),
        )

        return tuple(
            vector.tolist(),
        )


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
                "Embedding healthcheck failed",
            )

            return False