from fastapi import UploadFile

from app.storage.local import LocalStorageBackend


class StorageService:
    def __init__(self):
        self.backend = LocalStorageBackend()

    async def save_file(
        self,
        file: UploadFile,
    ) -> tuple[str, str, int]:
        return await self.backend.save_file(file)

    async def delete_file(
        self,
        file_path: str,
    ) -> None:
        await self.backend.delete_file(file_path)

    def exists(
        self,
        file_path: str,
    ) -> bool:
        return self.backend.exists(file_path)