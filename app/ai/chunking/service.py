import logging
from uuid import uuid4

from app.ai.chunking.dto import (
    ChunkDTO,
    ChunkMetadata,
)
from app.models.document import Document

from .splitter import RecursiveTextSplitter

logger = logging.getLogger(__name__)


class ChunkingService:
    def __init__(
        self,
        splitter: RecursiveTextSplitter,
    ) -> None:
        self._splitter = splitter

    async def chunk_document(
        self,
        document: Document,
    ) -> list[ChunkDTO]:
        logger.info(
            "Chunking document %s",
            document.id,
        )

        if not document.content:
            logger.warning(
                "Document %s has no content",
                document.id,
            )
            return []

        parts = self._splitter.split(
            document.content,
        )

        logger.info(
            "Document %s split into %s chunks",
            document.id,
            len(parts),
        )

        chunks: list[ChunkDTO] = []

        for index, text in enumerate(parts):
            chunks.append(
                ChunkDTO(
                    id=uuid4(),
                    document_id=document.id,
                    text=text,
                    metadata=ChunkMetadata(
                        document_id=document.id,
                        owner_id=document.owner_id,
                        chunk_index=index,
                        title=document.title,
                    ),
                )
            )

        logger.info(
            "Created %s chunks for document %s",
            len(chunks),
            document.id,
        )

        return chunks