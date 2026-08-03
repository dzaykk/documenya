from __future__ import annotations

import logging

from app.ai.chunking.service import ChunkingService
from app.ai.embeddings.dto import EmbeddingRequest
from app.ai.embeddings.service import EmbeddingService
from app.ai.vectorstores.service import VectorStoreService
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.uow.base import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class DocumentEmbeddingService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        chunking: ChunkingService,
        embeddings: EmbeddingService,
        vector_store: VectorStoreService,
    ) -> None:
        self._uow = uow
        self._chunking = chunking
        self._embeddings = embeddings
        self._vector_store = vector_store

    async def index_document(
        self,
        document: Document,
    ) -> None:

        logger.info(
            "Indexing document %s",
            document.id,
        )

        await self._uow.chunks.delete_document_chunks(
            document.id,
        )

        await self._vector_store.delete_document(
            document.id,
        )

        chunks = await self._chunking.chunk_document(
            document,
        )

        if not chunks:
            logger.warning(
                "Document %s produced no chunks",
                document.id,
            )

            await self._uow.commit()
            return

        db_chunks = [
            DocumentChunk(
                id=chunk.id,
                document_id=document.id,
                owner_id=document.owner_id,
                content=chunk.text,
                chunk_index=chunk.metadata.chunk_index,
                page=chunk.metadata.page,
                section=chunk.metadata.section,
            )
            for chunk in chunks
        ]

        await self._uow.chunks.create_many(
            db_chunks,
        )

        await self._uow.commit()

        logger.info(
            "Saved %s chunks for document %s",
            len(db_chunks),
            document.id,
        )

        embedded_chunks = await self._embeddings.embed_documents(
            EmbeddingRequest(
                chunks=chunks,
            ),
        )

        logger.info(
            "Generated %s embeddings",
            len(embedded_chunks),
        )

        await self._vector_store.upsert_embeddings(
            embedded_chunks,
        )

        await self._uow.chunks.update_vector_ids(
            {
                embedded.chunk.id: str(
                    embedded.chunk.id,
                )
                for embedded in embedded_chunks
            }
        )

        await self._uow.commit()

        logger.info(
            "Document %s indexed successfully",
            document.id,
        )