import logging

from fastapi import UploadFile

from app.core.config import settings
from app.core.constants import ALLOWED_DOCUMENT_TYPES
from app.exceptions.document import (
    FileTooLargeError,
    UnsupportedDocumentTypeError,
)

logger = logging.getLogger(__name__)


class FileValidationService:

    @classmethod
    async def validate(
        cls,
        file: UploadFile,
    ) -> None:

        logger.info(
            "Validating file '%s'",
            file.filename,
        )

        if file.content_type not in ALLOWED_DOCUMENT_TYPES:

            logger.warning(
                "Unsupported content type '%s' for file '%s'",
                file.content_type,
                file.filename,
            )

            raise UnsupportedDocumentTypeError()

        current_position = file.file.tell()

        file.file.seek(0, 2)
        file_size = file.file.tell()

        file.file.seek(current_position)

        if file_size > settings.MAX_FILE_SIZE:

            logger.warning(
                "File '%s' exceeds size limit (%s bytes)",
                file.filename,
                file_size,
            )

            raise FileTooLargeError()

        logger.info(
            "File '%s' passed validation",
            file.filename,
        )