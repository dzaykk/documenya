from __future__ import annotations

import logging

from app.ai.services.document_embedding_service import (
    DocumentEmbeddingService,
)
from app.exceptions.document import (
    DocumentAlreadyProcessingError,
    DocumentNotFoundError,
)
from app.models.document import (
    Document,
    DocumentStatus,
)
from app.models.user import User
from app.services.document_parser_service import (
    DocumentParserService,
)
from app.uow.base import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class DocumentProcessingService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        parser: DocumentParserService,
        document_embedding_service: DocumentEmbeddingService,
    ) -> None:

        self.uow = uow
        self.parser = parser
        self.document_embedding_service = document_embedding_service

    async def process_document(
        self,
        document_id: int,
    ) -> None:

        logger.info(
            "Starting document processing %s",
            document_id,
        )

        document: Document | None = None

        async with self.uow:

            document = (
                await self.uow.documents.get_by_id_unscoped(
                    document_id,
                )
            )

            if document is None:

                logger.warning(
                    "Document %s not found",
                    document_id,
                )

                return

            try:

                logger.info(
                    "Extracting text from document %s",
                    document.id,
                )

                document.content = (
                    await self.parser.extract_text(
                        document.file_path,
                        document.mime_type,
                    )
                )

                document.status = (
                    DocumentStatus.PROCESSING
                )

                document.processing_error = None

                await self.uow.documents.update(
                    document,
                )

                await self.uow.commit()

            except Exception as exc:

                logger.exception(
                    "Document extraction failed %s",
                    document.id,
                )

                document.status = (
                    DocumentStatus.FAILED
                )

                document.processing_error = str(
                    exc,
                )

                await self.uow.documents.update(
                    document,
                )

                await self.uow.commit()

                return

        try:

            await self.document_embedding_service.index_document(
                document,
            )

        except Exception as exc:

            logger.exception(
                "Document indexing failed %s",
                document.id,
            )

            async with self.uow:

                failed_document = (
                    await self.uow.documents.get_by_id_unscoped(
                        document.id,
                    )
                )

                if failed_document:

                    failed_document.status = (
                        DocumentStatus.FAILED
                    )

                    failed_document.processing_error = str(
                        exc,
                    )

                    await self.uow.documents.update(
                        failed_document,
                    )

                    await self.uow.commit()

            return

        async with self.uow:

            completed_document = (
                await self.uow.documents.get_by_id_unscoped(
                    document.id,
                )
            )

            if completed_document:

                completed_document.status = (
                    DocumentStatus.COMPLETED
                )

                completed_document.processing_error = None

                await self.uow.documents.update(
                    completed_document,
                )

                await self.uow.commit()

        logger.info(
            "Document processing finished %s",
            document_id,
        )


    async def retry_processing(
        self,
        document_id: int,
        user: User,
    ) -> Document:

        logger.info(
            "User %s retry document %s",
            user.id,
            document_id,
        )

        async with self.uow:

            document = (
                await self.uow.documents.get_by_id(
                    document_id,
                    user.id,
                )
            )

            if document is None:

                raise DocumentNotFoundError()

            if (
                document.status
                == DocumentStatus.PROCESSING
            ):

                raise DocumentAlreadyProcessingError()

            document.status = (
                DocumentStatus.PROCESSING
            )

            document.processing_error = None
            document.content = None

            document = (
                await self.uow.documents.update(
                    document,
                )
            )

            await self.uow.commit()

        return document