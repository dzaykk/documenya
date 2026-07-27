import logging

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
    ):
        self.uow = uow
        self.parser = parser

    async def process_document(
        self,
        document_id: int,
    ) -> None:

        logger.info(
            "Starting processing for document %s",
            document_id,
        )

        async with self.uow:

            document = await self.uow.documents.get_by_id_unscoped(
                document_id,
            )

            if document is None:

                logger.warning(
                    "Document %s not found",
                    document_id,
                )

                return

            logger.info(
                "Extracting text from document %s",
                document.id,
            )

            try:

                document.content = (
                    await self.parser.extract_text(
                        document.file_path,
                        document.mime_type,
                    )
                )

                document.status = (
                    DocumentStatus.COMPLETED.value
                )

                document.processing_error = None

                logger.info(
                    "Document %s processed successfully",
                    document.id,
                )

            except Exception as exc:

                logger.exception(
                    "Failed to process document %s",
                    document.id,
                )

                document.status = (
                    DocumentStatus.FAILED.value
                )

                document.processing_error = str(
                    exc,
                )

            await self.uow.documents.update(
                document,
            )

            await self.uow.commit()

        logger.info(
            "Finished processing for document %s",
            document_id,
        )

    async def retry_processing(
        self,
        document_id: int,
        user: User,
    ) -> Document:

        logger.info(
            "User %s requested retry for document %s",
            user.id,
            document_id,
        )

        async with self.uow:

            document = await self.uow.documents.get_by_id(
                document_id,
                user.id,
            )

            if document is None:

                logger.warning(
                    "Document %s not found for user %s",
                    document_id,
                    user.id,
                )

                raise DocumentNotFoundError()

            if (
                document.status
                == DocumentStatus.PROCESSING.value
            ):

                logger.warning(
                    "Document %s is already processing",
                    document.id,
                )

                raise DocumentAlreadyProcessingError()

            document.status = (
                DocumentStatus.PROCESSING.value
            )

            document.processing_error = None
            document.content = None

            document = await self.uow.documents.update(
                document,
            )

            await self.uow.commit()

        logger.info(
            "Document %s queued for reprocessing",
            document.id,
        )

        return document