from __future__ import annotations

from functools import lru_cache

from app.core.config import settings

from app.embeddings.protocols import EmbeddingProvider

from .fastembed_provider import FastEmbedProvider


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:

    match settings.DEFAULT_EMBEDDING_PROVIDER:

        case "fastembed":
            return FastEmbedProvider()

        case _:
            raise RuntimeError(
                f"Unknown embedding provider: "
                f"{settings.DEFAULT_EMBEDDING_PROVIDER}"
            )