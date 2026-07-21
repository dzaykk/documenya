from pathlib import Path

import pdfplumber
from docx import Document

from app.exceptions.document import (
    EmptyDocumentError,
    UnsupportedDocumentTypeError,
)


DOCX_MIME = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


class DocumentParserService:

    async def extract_text(
        self,
        file_path: str,
        mime_type: str,
    ) -> str:

        path = Path(file_path)

        if mime_type == "text/plain":
            text = self._parse_txt(path)

        elif mime_type == "application/pdf":
            text = self._parse_pdf(path)

        elif mime_type == DOCX_MIME:
            text = self._parse_docx(path)

        else:
            raise UnsupportedDocumentTypeError(
                f"Unsupported file type: {mime_type}"
            )

        text = self._normalize_text(text)

        if not text:
            raise EmptyDocumentError(
                "No text found in document"
            )

        return text

    def _parse_txt(
        self,
        path: Path,
    ) -> str:

        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    def _parse_pdf(
        self,
        path: Path,
    ) -> str:

        pages: list[str] = []

        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                if text:
                    pages.append(text)

        return "\n".join(pages)

    def _parse_docx(
        self,
        path: Path,
    ) -> str:

        document = Document(path)

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)

    def _normalize_text(
        self,
        text: str,
    ) -> str:

        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        return "\n".join(lines)