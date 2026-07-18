from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate
from app.models.user import User


class DocumentService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.document_repository = DocumentRepository(
            session
        )


    async def create_document(
        self,
        data: DocumentCreate,
        user: User,
        filename: str,
        file_path: str,
        mime_type: str,
        file_size: int,
    ) -> Document:

        document = Document(
            title=data.title,
            filename=filename,
            file_path=file_path,
            mime_type=mime_type,
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