from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class StorageService:

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)

        self.upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )


    async def save_file(
        self,
        file: UploadFile,
    ) -> tuple[str, str, int]:

        extension = Path(
            file.filename
        ).suffix

        filename = (
            f"{uuid4()}{extension}"
        )

        file_path = (
            self.upload_dir / filename
        )

        content = await file.read()

        file_path.write_bytes(content)

        return (
            filename,
            str(file_path),
            len(content),
        )