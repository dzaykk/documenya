from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.storage_service import StorageService
from app.services.file_validation_service import FileValidationService
from app.schemas.document import DocumentUpdate

from pathlib import Path


class DocumentService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.document_repository = DocumentRepository(
            session
        )

        self.storage_service = StorageService()

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
            owner_id=user.id,
        )

        return await self.document_repository.create(
            document
        )

    async def get_user_documents(
        self,
        user: User,
        search: str | None = None,
    ) -> list[Document]:

        return await self.document_repository.get_user_documents(
            user.id,
            search,
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

        file_path = Path(document.file_path)

        if file_path.exists():
            file_path.unlink()

        await self.document_repository.delete(
            document
        )

        return True