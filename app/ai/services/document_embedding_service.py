from __future__ import annotations

import logging
import time

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

        started_at = time.perf_counter()

        logger.info(
            "Document indexing started document_id=%s owner_id=%s",
            document.id,
            document.owner_id,
        )

        try:

            await self._uow.chunks.delete_document_chunks(
                document.id,
            )

            await self._vector_store.delete_document(
                document.id,
            )

            logger.debug(
                "Old document data removed document_id=%s",
                document.id,
            )


            chunks = await self._chunking.chunk_document(
                document,
            )


            logger.info(
                "Document chunking completed document_id=%s chunks=%s",
                document.id,
                len(chunks),
            )


            if not chunks:

                logger.warning(
                    "Document produced no chunks document_id=%s",
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
                "Document chunks saved document_id=%s chunks=%s",
                document.id,
                len(db_chunks),
            )


            embedding_started = time.perf_counter()

            embedded_chunks = await self._embeddings.embed_documents(
                EmbeddingRequest(
                    chunks=chunks,
                ),
            )


            logger.info(
                "Embeddings generated document_id=%s embeddings=%s duration_ms=%s",
                document.id,
                len(embedded_chunks),
                round(
                    (time.perf_counter() - embedding_started) * 1000,
                ),
            )


            await self._vector_store.upsert_embeddings(
                embedded_chunks,
            )


            logger.info(
                "Vectors stored document_id=%s vectors=%s",
                document.id,
                len(embedded_chunks),
            )


            await self._uow.chunks.update_vector_ids(
                {
                    embedded.chunk.id: str(
                        embedded.chunk.id,
                    )
                    for embedded in embedded_chunks
                },
            )


            await self._uow.commit()


            logger.info(
                "Document indexing completed document_id=%s duration_ms=%s",
                document.id,
                round(
                    (time.perf_counter() - started_at) * 1000,
                ),
            )


        except Exception:

            logger.exception(
                "Document indexing failed document_id=%s",
                document.id,
            )

            raise