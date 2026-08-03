from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import settings

logger = logging.getLogger(__name__)


class QdrantClientFactory:
    @staticmethod
    def create() -> AsyncQdrantClient:
        logger.info(
            "Creating Qdrant client %s",
            settings.QDRANT_URL,
        )

        return AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=settings.QDRANT_TIMEOUT,
            check_compatibility=False,
        )


@asynccontextmanager
async def get_qdrant_client() -> AsyncGenerator[AsyncQdrantClient, None]:
    client = QdrantClientFactory.create()
    try:
        yield client
    finally:
        await client.close()

async def ensure_collection_exists(
    client: AsyncQdrantClient,
) -> None:

    collections = await client.get_collections()

    exists = any(
        collection.name == settings.QDRANT_COLLECTION
        for collection in collections.collections
    )

    if exists:
        logger.info(
            "Qdrant collection '%s' already exists",
            settings.QDRANT_COLLECTION,
        )
        return

    logger.info(
        "Creating Qdrant collection '%s'",
        settings.QDRANT_COLLECTION,
    )

    await client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=settings.QDRANT_VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

    logger.info(
        "Qdrant collection '%s' created successfully",
        settings.QDRANT_COLLECTION,
    )