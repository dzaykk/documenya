from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequest(
    BaseModel,
):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
    )

    owner_id: int


class QueryResponse(
    BaseModel,
):
    answer: str

    sources: list[int]