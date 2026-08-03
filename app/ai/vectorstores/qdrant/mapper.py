from __future__ import annotations

from qdrant_client.models import PointStruct

from app.ai.embeddings.dto import EmbeddedChunk
from app.ai.vectorstores.dto import (
    VectorPoint,
    VectorSearchResult,
)


class QdrantMapper:
    @staticmethod
    def to_vector_point(
        chunk: EmbeddedChunk,
    ) -> VectorPoint:

        return VectorPoint(
            id=chunk.chunk.id,
            vector=chunk.vector,
            payload={
                "document_id": chunk.chunk.metadata.document_id,
                "owner_id": chunk.chunk.metadata.owner_id,
                "chunk_index": chunk.chunk.metadata.chunk_index,
                "page": chunk.chunk.metadata.page,
                "title": chunk.chunk.metadata.title,
                "section": chunk.chunk.metadata.section,
                "text": chunk.chunk.text,
            },
        )

    @staticmethod
    def to_qdrant_point(
        point: VectorPoint,
    ) -> PointStruct:

        return PointStruct(
            id=str(point.id),
            vector=list(point.vector),
            payload=dict(point.payload),
        )

    @staticmethod
    def to_search_result(
        point,
    ) -> VectorSearchResult:

        return VectorSearchResult(
            id=point.id,
            score=point.score,
            payload=point.payload or {},
        )