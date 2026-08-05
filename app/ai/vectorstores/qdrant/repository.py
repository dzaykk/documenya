from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

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

        logger.info(
            "Qdrant vector store initialized collection=%s",
            self._collection,
        )


    async def upsert(
        self,
        points: list[VectorPoint],
    ) -> None:

        if not points:

            logger.warning(
                "Skip empty vector upsert",
            )

            return


        logger.info(
            "Qdrant upsert started points=%s collection=%s",
            len(points),
            self._collection,
        )


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
                "Qdrant upsert completed points=%s",
                len(points),
            )


        except Exception as exc:

            logger.exception(
                "Qdrant vector upsert failed",
            )

            raise VectorUpsertError() from exc



    async def search(
        self,
        vector: tuple[float, ...],
        limit: int,
        filters: Mapping[str, Any] | None = None,
    ) -> list[VectorSearchResult]:


        logger.info(
            "Qdrant search started collection=%s limit=%s dimension=%s filters=%s",
            self._collection,
            limit,
            len(vector),
            filters,
        )


        query_filter: Filter | None = None


        if filters:

            query_filter = Filter(
                must=[
                    FieldCondition(
                        key=key,
                        match=MatchValue(
                            value=value,
                        ),
                    )
                    for key, value in filters.items()
                ],
            )


        try:

            result = await self._client.query_points(
                collection_name=self._collection,
                query=list(vector),
                limit=limit,
                query_filter=query_filter,
            )


            if not result.points:

                logger.info(
                    "Qdrant search returned no points",
                )

                return []


            scores = [
                point.score
                for point in result.points
            ]


            logger.info(
                "Qdrant search completed results=%s min_score=%.4f max_score=%.4f",
                len(result.points),
                min(scores),
                max(scores),
            )


            return [
                QdrantMapper.to_search_result(
                    point,
                )
                for point in result.points
            ]


        except Exception as exc:

            logger.exception(
                "Qdrant vector search failed",
            )

            raise VectorSearchError() from exc



    async def delete_document(
        self,
        document_id: int,
    ) -> None:

        logger.info(
            "Deleting document vectors document_id=%s",
            document_id,
        )


        try:

            await self._client.delete(
                collection_name=self._collection,
                wait=False,
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
                "Deleted document vectors document_id=%s",
                document_id,
            )


        except Exception as exc:

            logger.exception(
                "Failed deleting document vectors",
            )

            raise VectorDeleteError() from exc



    async def delete_user_documents(
        self,
        user_id: int,
    ) -> None:

        logger.info(
            "Deleting user vectors user_id=%s",
            user_id,
        )


        try:

            await self._client.delete(
                collection_name=self._collection,
                wait=False,
                points_selector=FilterSelector(
                    filter=Filter(
                        must=[
                            FieldCondition(
                                key="owner_id",
                                match=MatchValue(
                                    value=user_id,
                                ),
                            ),
                        ],
                    ),
                ),
            )


            logger.info(
                "Deleted user vectors user_id=%s",
                user_id,
            )


        except Exception as exc:

            logger.exception(
                "Failed deleting user vectors",
            )

            raise VectorDeleteError() from exc



    async def healthcheck(
        self,
    ) -> bool:

        try:

            await self._client.get_collection(
                collection_name=self._collection,
            )


            logger.info(
                "Qdrant healthcheck passed collection=%s",
                self._collection,
            )


            return True


        except Exception:

            logger.exception(
                "Qdrant healthcheck failed collection=%s",
                self._collection,
            )

            return False