from pydantic import BaseModel, Field


class DocumentQueryParams(BaseModel):

    search: str | None = None

    page: int = Field(
        default=1,
        ge=1,
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )