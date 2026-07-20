import logging

from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import (
    Document,
    DocumentStatus,
)

from app.models.user import User

from app.repositories.document_repository import (
    DocumentRepository,
)

from app.services.storage_service import (
    StorageService,
)

from app.services.file_validation_service import (
    FileValidationService,
)

from app.services.document_parser_service import (
    DocumentParserService,
)

from app.schemas.document import (
    DocumentList,
    DocumentUpdate,
)

from app.schemas.query import (
    DocumentQueryParams,
)


logger = logging.getLogger(__name__)


class DocumentService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.document_repository = DocumentRepository(
            session
        )

        self.storage_service = StorageService()
        self.parser_service = DocumentParserService()


    async def create_document(
        self,
        title: str,
        file: UploadFile,
        user: User,
    ) -> Document:

        await FileValidationService.validate(file)

        filename, file_path, file_size = (
            await self.storage_service.save_file(file)
        )

        document = Document(
            title=title,
            filename=filename,
            file_path=file_path,
            mime_type=file.content_type,
            file_size=file_size,
            content=None,
            owner_id=user.id,
            status=DocumentStatus.PROCESSING.value,
        )

        return await self.document_repository.create(
            document
        )


    async def process_document(
        self,
        document_id: int,
    ) -> None:

        document = await self.document_repository.get_by_id_internal(
            document_id
        )

        if not document:
            return

        try:
            content = await self.parser_service.extract_text(
                file_path=document.file_path,
                mime_type=document.mime_type,
            )
            document.content = content
            document.status = DocumentStatus.COMPLETED.value
            document.processing_error = None

        except Exception as e:
            logger.exception(
                "Failed to process document %s",
                document.id,
            )

            document.status = DocumentStatus.FAILED.value
            document.processing_error = str(e)

        await self.document_repository.update(
            document
        )


    async def get_user_documents(
        self,
        user: User,
        params: DocumentQueryParams,
    ) -> DocumentList:

        documents = await self.document_repository.get_user_documents(
            user_id=user.id,
            search=params.search,
            page=params.page,
            limit=params.limit,
        )

        total = await self.document_repository.count_user_documents(
            user_id=user.id,
            search=params.search,
        )

        pages = (
            total + params.limit - 1
        ) // params.limit

        return DocumentList(
            items=documents,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=pages,
        )


    async def get_document(
        self,
        document_id: int,
        user: User,
    ) -> Document | None:

        return await self.document_repository.get_by_id(
            document_id,
            user.id,
        )
    

    async def update_document(
        self,
        document_id: int,
        data: DocumentUpdate,
        user: User,
    ) -> Document | None:

        document = await self.get_document(
            document_id,
            user,
        )

        if not document:
            return None

        document.title = data.title

        return await self.document_repository.update(
            document
        )


    async def delete_document(
        self,
        document_id: int,
        user: User,
    ) -> bool:

        document = await self.get_document(
            document_id,
            user,
        )

        if not document:
            return False

        file_path = Path(
            document.file_path
        )

        if file_path.exists():
            file_path.unlink()

        await self.document_repository.delete(
            document
        )

        return True