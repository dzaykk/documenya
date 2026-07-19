from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    title: str


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    id: int

    filename: str
    mime_type: str
    file_size: int

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class DocumentList(BaseModel):
    items: list[DocumentRead]

    total: int

    page: int

    limit: int

    pages: int


class DocumentUpdate(BaseModel):
    title: str