from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus

class DocumentBase(BaseModel):
    title: str


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(BaseModel):
    id: int
    title: str
    filename: str
    mime_type: str
    file_size: int

    status: DocumentStatus
    processing_error: str | None = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentList(BaseModel):
    items: list[DocumentRead]

    total: int
    page: int
    limit: int
    pages: int


class DocumentUpdate(BaseModel):
    title: str


class DocumentContent(BaseModel):
    id: int
    title: str
    content: str | None
    model_config = ConfigDict(from_attributes=True)