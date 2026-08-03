from __future__ import annotations

from functools import lru_cache

from app.ai.embeddings.protocols import EmbeddingProvider
from app.core.config import settings

from .huggingface_provider import HuggingFaceEmbeddingProvider


class EmbeddingProviderFactory:
    @staticmethod
    @lru_cache(maxsize=1)
    def create() -> EmbeddingProvider:
        provider = settings.DEFAULT_EMBEDDING_PROVIDER

        match provider:
            case "huggingface":
                return HuggingFaceEmbeddingProvider()

            case _:
                raise RuntimeError(
                    f"Unknown embedding provider: {provider}",
                )