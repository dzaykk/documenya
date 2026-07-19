from fastapi import HTTPException, UploadFile, status


class FileValidationService:

    ALLOWED_TYPES = {
        "application/pdf",
        "text/plain",
        "text/markdown",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

    @classmethod
    async def validate(
        cls,
        file: UploadFile,
    ) -> None:

        if file.content_type not in cls.ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file type",
            )

        content = await file.read()

        if len(content) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File is too large",
            )

        await file.seek(0)