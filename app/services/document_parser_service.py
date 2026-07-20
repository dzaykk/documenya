from pathlib import Path


class DocumentParserService:

    async def extract_text(
        self,
        file_path: str,
        mime_type: str,
    ) -> str:

        path = Path(file_path)

        if mime_type == "text/plain":
            return path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

        raise ValueError(
            f"Unsupported mime type: {mime_type}"
        )