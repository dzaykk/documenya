from unittest.mock import MagicMock, patch

import pytest

from app.core.constants import (
    DOCX_MIME,
    PDF_MIME,
    TXT_MIME,
)
from app.exceptions.document import (
    EmptyDocumentError,
    UnsupportedDocumentTypeError,
)
from app.services.document_parser_service import (
    DocumentParserService,
)


@pytest.fixture
def service():
    return DocumentParserService()


@pytest.mark.asyncio
async def test_extract_txt_success(
    service,
    tmp_path,
):
    file = tmp_path / "document.txt"

    file.write_text(
        "  hello world  \n\n second line ",
        encoding="utf-8",
    )

    result = await service.extract_text(
        str(file),
        TXT_MIME,
    )

    assert result == (
        "hello world\nsecond line"
    )


@pytest.mark.asyncio
async def test_extract_txt_file_not_found(
    service,
):
    with pytest.raises(
        FileNotFoundError,
    ):
        await service.extract_text(
            "/tmp/missing.txt",
            TXT_MIME,
        )


@pytest.mark.asyncio
async def test_extract_unsupported_mime_type(
    service,
    tmp_path,
):
    file = tmp_path / "document.bin"

    file.write_text(
        "content",
        encoding="utf-8",
    )

    with pytest.raises(
        UnsupportedDocumentTypeError,
    ):
        await service.extract_text(
            str(file),
            "application/octet-stream",
        )


@pytest.mark.asyncio
async def test_extract_empty_document(
    service,
    tmp_path,
):
    file = tmp_path / "empty.txt"

    file.write_text(
        "",
        encoding="utf-8",
    )

    with pytest.raises(
        EmptyDocumentError,
    ):
        await service.extract_text(
            str(file),
            TXT_MIME,
        )


@pytest.mark.asyncio
async def test_extract_pdf_success(
    service,
    tmp_path,
):
    file = tmp_path / "document.pdf"

    file.touch()

    page_one = MagicMock()
    page_one.extract_text.return_value = (
        "first page"
    )

    page_two = MagicMock()
    page_two.extract_text.return_value = (
        "second page"
    )

    pdf = MagicMock()

    pdf.pages = [
        page_one,
        page_two,
    ]

    pdf_context = MagicMock()

    pdf_context.__enter__.return_value = pdf

    with patch(
        "app.services.document_parser_service.pdfplumber.open",
        return_value=pdf_context,
    ):
        result = await service.extract_text(
            str(file),
            PDF_MIME,
        )

    assert result == (
        "first page\nsecond page"
    )


@pytest.mark.asyncio
async def test_extract_pdf_skips_empty_pages(
    service,
    tmp_path,
):
    file = tmp_path / "document.pdf"

    file.touch()

    page_one = MagicMock()
    page_one.extract_text.return_value = (
        "first page"
    )

    empty_page = MagicMock()
    empty_page.extract_text.return_value = None

    page_two = MagicMock()
    page_two.extract_text.return_value = (
        "second page"
    )

    pdf = MagicMock()

    pdf.pages = [
        page_one,
        empty_page,
        page_two,
    ]

    pdf_context = MagicMock()

    pdf_context.__enter__.return_value = pdf

    with patch(
        "app.services.document_parser_service.pdfplumber.open",
        return_value=pdf_context,
    ):
        result = await service.extract_text(
            str(file),
            PDF_MIME,
        )

    assert result == (
        "first page\nsecond page"
    )


@pytest.mark.asyncio
async def test_extract_pdf_with_empty_pages_raises_error(
    service,
    tmp_path,
):
    file = tmp_path / "empty.pdf"

    file.touch()

    page = MagicMock()

    page.extract_text.return_value = None

    pdf = MagicMock()

    pdf.pages = [
        page,
    ]

    pdf_context = MagicMock()

    pdf_context.__enter__.return_value = pdf

    with patch(
        "app.services.document_parser_service.pdfplumber.open",
        return_value=pdf_context,
    ):
        with pytest.raises(
            EmptyDocumentError,
        ):
            await service.extract_text(
                str(file),
                PDF_MIME,
            )


@pytest.mark.asyncio
async def test_extract_docx_success(
    service,
    tmp_path,
):
    file = tmp_path / "document.docx"

    file.touch()

    paragraph_one = MagicMock()
    paragraph_one.text = "first paragraph"

    empty_paragraph = MagicMock()
    empty_paragraph.text = "   "

    paragraph_two = MagicMock()
    paragraph_two.text = "second paragraph"

    document = MagicMock()

    document.paragraphs = [
        paragraph_one,
        empty_paragraph,
        paragraph_two,
    ]

    with patch(
        "app.services.document_parser_service.Document",
        return_value=document,
    ):
        result = await service.extract_text(
            str(file),
            DOCX_MIME,
        )

    assert result == (
        "first paragraph\nsecond paragraph"
    )


@pytest.mark.asyncio
async def test_extract_docx_empty_document_raises_error(
    service,
    tmp_path,
):
    file = tmp_path / "empty.docx"

    file.touch()

    document = MagicMock()

    document.paragraphs = []

    with patch(
        "app.services.document_parser_service.Document",
        return_value=document,
    ):
        with pytest.raises(
            EmptyDocumentError,
        ):
            await service.extract_text(
                str(file),
                DOCX_MIME,
            )


def test_normalize_removes_empty_lines(
    service,
):
    result = service._normalize_text(
        """
        line one


        line two

        """
    )

    assert result == (
        "line one\nline two"
    )