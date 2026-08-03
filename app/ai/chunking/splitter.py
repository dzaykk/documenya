from __future__ import annotations

import logging
from collections.abc import Iterable

from .constants import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    MIN_CHUNK_SIZE,
    PARAGRAPH_SEPARATOR,
    RECURSIVE_SEPARATORS,
)

logger = logging.getLogger(__name__)


class RecursiveTextSplitter:
    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size",
            )

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def split(
        self,
        text: str,
    ) -> list[str]:
        text = text.strip()

        if not text:
            logger.debug("Received empty text for splitting")
            return []

        logger.debug(
            "Splitting text length=%s chunk_size=%s overlap=%s",
            len(text),
            self._chunk_size,
            self._chunk_overlap,
        )

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split(PARAGRAPH_SEPARATOR)
            if paragraph.strip()
        ]

        chunks: list[str] = []

        for paragraph in paragraphs:
            if len(paragraph) <= self._chunk_size:
                chunks.append(paragraph)
                continue

            chunks.extend(
                self._recursive_split(
                    paragraph,
                    0,
                )
            )

        result = self._apply_overlap(chunks)

        logger.debug(
            "Generated %s chunks",
            len(result),
        )

        return result

    def _recursive_split(
        self,
        text: str,
        level: int,
    ) -> list[str]:
        if len(text) <= self._chunk_size:
            return [text.strip()]

        if level >= len(RECURSIVE_SEPARATORS):
            logger.debug(
                "No separators left, using hard split. Text length=%s",
                len(text),
            )
            return self._hard_split(text)

        separator = RECURSIVE_SEPARATORS[level]
        parts = text.split(separator)

        if len(parts) == 1:
            return self._recursive_split(
                text,
                level + 1,
            )

        chunks: list[str] = []
        current = ""

        for part in parts:
            candidate = (
                part
                if not current
                else current + separator + part
            )

            if len(candidate) <= self._chunk_size:
                current = candidate
                continue

            if current:
                chunks.extend(
                    self._recursive_split(
                        current,
                        level + 1,
                    )
                )

            current = part

        if current:
            chunks.extend(
                self._recursive_split(
                    current,
                    level + 1,
                )
            )

        return chunks

    def _hard_split(
        self,
        text: str,
    ) -> list[str]:
        chunks: list[str] = []

        step = self._chunk_size - self._chunk_overlap

        start = 0

        while start < len(text):
            end = start + self._chunk_size

            chunks.append(
                text[start:end],
            )

            start += step

        return chunks

    def _apply_overlap(
        self,
        chunks: Iterable[str],
    ) -> list[str]:
        filtered_chunks = [
            chunk.strip()
            for chunk in chunks
            if len(chunk.strip()) >= MIN_CHUNK_SIZE
        ]

        if len(filtered_chunks) <= 1:
            return filtered_chunks

        overlapped_chunks: list[str] = []

        for index, chunk in enumerate(filtered_chunks):
            if index == 0:
                overlapped_chunks.append(chunk)
                continue

            previous_chunk = filtered_chunks[index - 1]

            overlap = previous_chunk[
                -self._chunk_overlap :
            ]

            overlapped_chunks.append(
                overlap + chunk,
            )

        logger.debug(
            "Applied overlap to %s chunks",
            len(overlapped_chunks),
        )

        return overlapped_chunks