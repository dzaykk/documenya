import asyncio
import logging

from app.ai.vectorstores.service import VectorStoreService
from app.exceptions.document import DocumentNotFoundError
from app.models.user import User
from app.storage.service import StorageService
from app.uow.base import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class DocumentCleanupService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        storage_service: StorageService,
        vector_store: VectorStoreService,
        max_concurrent_deletes: int = 20,
    ) -> None:
        self.uow = uow
        self.storage_service = storage_service
        self.vector_store = vector_store
        self.semaphore = asyncio.Semaphore(max_concurrent_deletes)

    async def _safe_delete_file(
        self,
        file_path: str,
    ) -> None:
        if not file_path:
            return

        async with self.semaphore:
            try:
                await self.storage_service.delete_file(file_path)
            except Exception:
                logger.exception(
                    "Failed to remove file '%s' from storage",
                    file_path,
                )

    async def delete_document(
        self,
        document_id: int,
        user: User,
    ) -> None:

        async with self.uow:
            document = await self.uow.documents.get_by_id_and_owner(
                document_id,
                user.id,
            )

            if document is None:
                logger.warning(
                    "Document %s not found for user %s during deletion",
                    document_id,
                    user.id,
                )
                raise DocumentNotFoundError()

            file_path = document.file_path

        await self.vector_store.delete_document(
            document_id=document_id,
        )

        async with self.uow:
            doc_to_delete = await self.uow.documents.get_by_id_and_owner(
                document_id,
                user.id,
            )

            if doc_to_delete:
                await self.uow.documents.delete(doc_to_delete)
                await self.uow.commit()

        if file_path:
            await self._safe_delete_file(file_path)

        logger.info(
            "Document %s and its vectors fully deleted by user %s",
            document_id,
            user.id,
        )

    async def delete_all_user_documents(
        self,
        user: User,
    ) -> int:

        async with self.uow:
            file_paths = await self.uow.documents.get_file_paths_by_owner(
                user.id,
            )

            if not file_paths:
                return 0

        await self.vector_store.delete_user_documents(
            user_id=user.id,
        )

        async with self.uow:
            deleted_count = await self.uow.documents.delete_all_by_owner_id(
                user.id,
            )

            await self.uow.commit()

        if file_paths:
            tasks = [
                self._safe_delete_file(path)
                for path in file_paths
                if path
            ]

            await asyncio.gather(*tasks)

        logger.info(
            "Cleaned up workspace for user %s: %s documents removed",
            user.id,
            deleted_count,
        )

        return deleted_count