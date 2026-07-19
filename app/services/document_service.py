from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.storage_service import StorageService

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
    ) -> list[Document]:

        return await self.document_repository.get_user_documents(
            user.id
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