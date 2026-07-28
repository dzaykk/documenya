from io import BytesIO

import pytest
from fastapi import UploadFile

from app.core.config import settings
from app.exceptions.document import (
    FileTooLargeError,
    UnsupportedDocumentTypeError,
)
from app.services.file_validation_service import (
    FileValidationService,
)


@pytest.mark.asyncio
async def test_validate_supported_file_success():
    file = UploadFile(
        filename="document.txt",
        file=BytesIO(
            b"hello world",
        ),
        headers={
            "content-type": "text/plain",
        },
    )

    result = await FileValidationService.validate(
        file,
    )

    assert result is None


@pytest.mark.asyncio
async def test_validate_pdf_file_success():
    file = UploadFile(
        filename="document.pdf",
        file=BytesIO(
            b"pdf-content",
        ),
        headers={
            "content-type": "application/pdf",
        },
    )

    result = await FileValidationService.validate(
        file,
    )

    assert result is None


@pytest.mark.asyncio
async def test_validate_docx_file_success():
    file = UploadFile(
        filename="document.docx",
        file=BytesIO(
            b"docx-content",
        ),
        headers={
            "content-type": (
                "application/"
                "vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
        },
    )

    result = await FileValidationService.validate(
        file,
    )

    assert result is None


@pytest.mark.asyncio
async def test_validate_unsupported_mime_type():
    file = UploadFile(
        filename="malware.exe",
        file=BytesIO(
            b"content",
        ),
        headers={
            "content-type": "application/octet-stream",
        },
    )

    with pytest.raises(
        UnsupportedDocumentTypeError,
    ):
        await FileValidationService.validate(
            file,
        )


@pytest.mark.asyncio
async def test_validate_missing_content_type():
    file = UploadFile(
        filename="unknown",
        file=BytesIO(
            b"content",
        ),
        headers={},
    )

    with pytest.raises(
        UnsupportedDocumentTypeError,
    ):
        await FileValidationService.validate(
            file,
        )


@pytest.mark.asyncio
async def test_validate_file_too_large(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "MAX_FILE_SIZE",
        5,
    )

    file = UploadFile(
        filename="large.txt",
        file=BytesIO(
            b"too large",
        ),
        headers={
            "content-type": "text/plain",
        },
    )

    with pytest.raises(
        FileTooLargeError,
    ):
        await FileValidationService.validate(
            file,
        )


@pytest.mark.asyncio
async def test_validate_file_exact_max_size(
    monkeypatch,
):
    content = b"12345"

    monkeypatch.setattr(
        settings,
        "MAX_FILE_SIZE",
        len(content),
    )

    file = UploadFile(
        filename="exact.txt",
        file=BytesIO(
            content,
        ),
        headers={
            "content-type": "text/plain",
        },
    )

    result = await FileValidationService.validate(
        file,
    )

    assert result is None


@pytest.mark.asyncio
async def test_validate_preserves_current_file_position():
    file_object = BytesIO(
        b"hello world",
    )

    file_object.seek(5)

    file = UploadFile(
        filename="document.txt",
        file=file_object,
        headers={
            "content-type": "text/plain",
        },
    )

    await FileValidationService.validate(
        file,
    )

    assert file.file.tell() == 5