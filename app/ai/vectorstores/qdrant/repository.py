from __future__ import annotations

import logging

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
)

from app.ai.vectorstores.dto import (
    VectorPoint,
    VectorSearchResult,
)
from app.ai.vectorstores.exceptions import (
    VectorDeleteError,
    VectorSearchError,
    VectorUpsertError,
)
from app.ai.vectorstores.protocols import VectorStore
from app.core.config import settings

from .mapper import QdrantMapper

logger = logging.getLogger(__name__)


class QdrantVectorStore(VectorStore):
    def __init__(
        self,
        client: AsyncQdrantClient,
    ) -> None:
        self._client = client
        self._collection = settings.QDRANT_COLLECTION

    async def upsert(
        self,
        points: list[VectorPoint],
    ) -> None:
        if not points:
            logger.warning(
                "Skip empty vector upsert",
            )
            return

        try:
            await self._client.upsert(
                collection_name=self._collection,
                wait=True,
                points=[
                    QdrantMapper.to_qdrant_point(
                        point,
                    )
                    for point in points
                ],
            )

            logger.info(
                "Upserted %s vectors into %s",
                len(points),
                self._collection,
            )

        except Exception as exc:
            logger.exception(
                "Vector upsert failed",
            )

            raise VectorUpsertError() from exc

    async def search(
        self,
        vector: tuple[float, ...],
        limit: int,
    ) -> list[VectorSearchResult]:
        try:
            result = await self._client.query_points(
                collection_name=self._collection,
                query=list(vector),
                limit=limit,
            )

            if not result.points:
                return []

            logger.debug(
                "Vector search returned %s results",
                len(result.points),
            )

            return [
                QdrantMapper.to_search_result(
                    point,
                )
                for point in result.points
            ]

        except Exception as exc:
            logger.exception(
                "Vector search failed",
            )

            raise VectorSearchError() from exc

    async def delete_document(
        self,
        document_id: int,
    ) -> None:
        try:
            await self._client.delete(
                collection_name=self._collection,
                wait=True,
                points_selector=FilterSelector(
                    filter=Filter(
                        must=[
                            FieldCondition(
                                key="document_id",
                                match=MatchValue(
                                    value=document_id,
                                ),
                            ),
                        ],
                    ),
                ),
            )

            logger.info(
                "Deleted vectors for document %s",
                document_id,
            )

        except Exception as exc:
            logger.exception(
                "Failed deleting document vectors",
            )

            raise VectorDeleteError() from exc

    async def healthcheck(
        self,
    ) -> bool:
        try:
            await self._client.get_collection(
                collection_name=self._collection,
            )

            return True

        except Exception:
            logger.exception(
                "Qdrant healthcheck failed",
            )

            return False