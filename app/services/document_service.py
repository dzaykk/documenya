import logging

from fastapi import UploadFile

from app.exceptions.document import DocumentNotFoundError
from app.models.document import Document
from app.models.user import User
from app.schemas.document import (
    DocumentList,
    DocumentUpdate,
)
from app.schemas.query import DocumentQueryParams
from app.services.file_validation_service import (
    FileValidationService,
)
from app.storage.service import StorageService
from app.uow.base import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        storage_service: StorageService,
    ):
        self.uow = uow
        self.storage_service = storage_service

    async def create_document(
        self,
        title: str,
        file: UploadFile,
        user: User,
    ) -> Document:

        logger.info(
            "User %s uploads '%s'",
            user.id,
            title,
        )

        await FileValidationService.validate(file)

        logger.info(
            "File '%s' passed validation",
            file.filename,
        )

        file_path: str | None = None

        try:

            filename, file_path, file_size = (
                await self.storage_service.save_file(file)
            )

            logger.info(
                "File saved to '%s'",
                file_path,
            )

            document = Document(
                title=title,
                filename=filename,
                file_path=file_path,
                mime_type=file.content_type,
                file_size=file_size,
                owner_id=user.id,
            )

            async with self.uow:

                document = await self.uow.documents.create(
                    document,
                )

                await self.uow.commit()

            logger.info(
                "Document %s created",
                document.id,
            )

            return document

        except Exception:

            logger.exception(
                "Document creation failed for user %s",
                user.id,
            )

            if file_path is not None:

                logger.info(
                    "Removing uploaded file '%s'",
                    file_path,
                )

                await self.storage_service.delete_file(
                    file_path,
                )

            raise

    async def get_document(
        self,
        document_id: int,
        user: User,
    ) -> Document:

        logger.info(
            "User %s requests document %s",
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

            logger.info(
                "Document %s returned to user %s",
                document.id,
                user.id,
            )

            return document

    async def get_user_documents(
        self,
        user: User,
        params: DocumentQueryParams,
    ) -> DocumentList:

        logger.info(
            "User %s requests document list",
            user.id,
        )

        async with self.uow:

            items = await self.uow.documents.get_user_documents(
                user.id,
                params.search,
                params.page,
                params.limit,
            )

            total = await self.uow.documents.count_user_documents(
                user.id,
                params.search,
            )

        pages = (
            total + params.limit - 1
        ) // params.limit

        logger.info(
            "Returned %s of %s documents for user %s",
            len(items),
            total,
            user.id,
        )

        return DocumentList(
            items=items,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=pages,
        )

    async def update_document(
        self,
        document_id: int,
        data: DocumentUpdate,
        user: User,
    ) -> Document:

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

            logger.info(
                "Changing title of document %s",
                document.id,
            )

            document.title = data.title

            document = await self.uow.documents.update(
                document,
            )

            await self.uow.commit()

        logger.info(
            "Document %s updated by user %s",
            document.id,
            user.id,
        )

        return document

    async def delete_document(
        self,
        document_id: int,
        user: User,
    ) -> None:

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

            file_path = document.file_path

            await self.uow.documents.delete(
                document,
            )

            await self.uow.commit()

        logger.info(
            "Removing file '%s'",
            file_path,
        )

        await self.storage_service.delete_file(
            file_path,
        )

        logger.info(
            "File '%s' removed",
            file_path,
        )

        logger.info(
            "Document %s deleted by user %s",
            document_id,
            user.id,
        )