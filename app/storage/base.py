from abc import ABC, abstractmethod

from fastapi import UploadFile


class StorageBackend(ABC):

    @abstractmethod
    async def save_file(
        self,
        file: UploadFile,
    ) -> tuple[str, str, int]:
        ...

    @abstractmethod
    async def delete_file(
        self,
        file_path: str,
    ) -> None:
        ...

    @abstractmethod
    def exists(
        self,
        file_path: str,
    ) -> bool:
        ...