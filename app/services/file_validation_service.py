from fastapi import UploadFile

from app.core.config import settings
from app.core.constants import ALLOWED_DOCUMENT_TYPES

from app.exceptions.document import (
    UnsupportedDocumentTypeError,
    FileTooLargeError,
)


class FileValidationService:

    @classmethod
    async def validate(
        cls,
        file: UploadFile,
    ) -> None:

        if file.content_type not in ALLOWED_DOCUMENT_TYPES:
            raise UnsupportedDocumentTypeError()

        content = await file.read()

        if len(content) > settings.MAX_FILE_SIZE:
            if len(content) > settings.MAX_FILE_SIZE:
                raise FileTooLargeError()

        await file.seek(0)