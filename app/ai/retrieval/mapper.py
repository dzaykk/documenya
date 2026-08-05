from app.ai.chunking.dto import (
    ChunkDTO,
    ChunkMetadata,
)
from app.ai.retrieval.dto import (
    RetrievedChunk,
)
from app.ai.vectorstores.dto import (
    VectorSearchResult,
)


class RetrievalMapper:

    @staticmethod
    def to_retrieved_chunk(
        result: VectorSearchResult,
    ) -> RetrievedChunk:

        payload = result.payload

        return RetrievedChunk(
            chunk=ChunkDTO(
                id=result.id,
                document_id=payload["document_id"],
                text=payload["text"],
                metadata=ChunkMetadata(
                    document_id=payload["document_id"],
                    owner_id=payload["owner_id"],
                    chunk_index=payload["chunk_index"],
                    page=payload.get(
                        "page",
                    ),
                    title=payload.get(
                        "title",
                    ),
                    section=payload.get(
                        "section",
                    ),
                ),
            ),

            score=result.score,
        )