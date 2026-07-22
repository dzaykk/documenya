from pydantic import BaseModel, Field

from app.schemas.types import SearchQuery


class DocumentQueryParams(BaseModel):

    search: SearchQuery | None = None

    page: int = Field(
        default=1,
        ge=1,
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )