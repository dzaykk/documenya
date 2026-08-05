from __future__ import annotations

import logging

from app.ai.retrieval.dto import RetrievalResult


logger = logging.getLogger(__name__)


class ContextBuilder:

    def build(
        self,
        result: RetrievalResult,
    ) -> str:

        logger.debug(
            "Building context from %s chunks",
            len(result.chunks),
        )

        if not result.chunks:

            logger.warning(
                "Context build skipped: no chunks available",
            )

            return ""

        sections: list[str] = []

        for index, item in enumerate(
            result.chunks,
            start=1,
        ):

            title = (
                item.chunk.metadata.title
                or "Untitled"
            )

            sections.append(
                f"""### Source {index}

Title:
{title}

Content:
{item.chunk.text}
"""
            )

        context = "\n\n".join(
            sections,
        )

        logger.info(
            "Context built sources=%s size=%s chars",
            len(sections),
            len(context),
        )

        return context