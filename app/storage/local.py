import logging
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.storage.base import StorageBackend

logger = logging.getLogger(__name__)


class LocalStorageBackend(StorageBackend):

    def __init__(self):

        self.upload_dir = Path(
            settings.UPLOAD_DIR,
        )

        self.upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger.info(
            "Storage initialized: %s",
            self.upload_dir,
        )

    async def save_file(
        self,
        file: UploadFile,
    ) -> tuple[str, str, int]:

        extension = Path(
            file.filename or "",
        ).suffix

        filename = f"{uuid4()}{extension}"

        path = self.upload_dir / filename

        file_size = 0

        logger.info(
            "Saving file '%s'",
            file.filename or "unknown",
        )

        with path.open("wb") as buffer:

            while chunk := await file.read(
                1024 * 1024,
            ):

                file_size += len(
                    chunk,
                )

                buffer.write(
                    chunk,
                )

        await file.seek(
            0,
        )

        logger.info(
            "File saved: %s (%d bytes)",
            path,
            file_size,
        )

        return (
            filename,
            str(path),
            file_size,
        )

    async def delete_file(
        self,
        file_path: str,
    ) -> None:

        path = Path(
            file_path,
        )

        if path.exists():

            path.unlink()

            logger.info(
                "Deleted file '%s'",
                file_path,
            )

        else:

            logger.warning(
                "File '%s' does not exist",
                file_path,
            )

    def exists(
        self,
        file_path: str,
    ) -> bool:

        exists = Path(
            file_path,
        ).exists()

        logger.debug(
            "File exists check '%s': %s",
            file_path,
            exists,
        )

        return exists