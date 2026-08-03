from __future__ import annotations

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 120
MIN_CHUNK_SIZE = 50

PARAGRAPH_SEPARATOR = "\n\n"
LINE_SEPARATOR = "\n"

SENTENCE_SEPARATORS = (
    ". ",
    "! ",
    "? ",
)

RECURSIVE_SEPARATORS = (
    PARAGRAPH_SEPARATOR,
    LINE_SEPARATOR,
    ". ",
    "! ",
    "? ",
    "; ",
    ", ",
    " ",
)