from typing import Annotated
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from app.api.dependencies import (
    CurrentUser,
    DocumentServiceDep,
)
from app.exceptions.document import (
    DocumentAlreadyProcessingError,
    DocumentProcessingFailedError,
    DocumentNotFoundError,
)
from app.models.document import DocumentStatus
from app.schemas.document import (
    DocumentContent,
    DocumentList,
    DocumentRead,
    DocumentUpdate,
)
from app.schemas.query import DocumentQueryParams


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


DocumentParams = Annotated[
    DocumentQueryParams,
    Depends(),
]


@router.get(
    "",
    response_model=DocumentList,
    summary="List user documents",
)
async def get_documents(
    current_user: CurrentUser,
    service: DocumentServiceDep,
    params: DocumentParams,
):
    return await service.get_user_documents(
        current_user,
        params,
    )


@router.post(
    "",
    response_model=DocumentRead,
    summary="Upload document",
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    service: DocumentServiceDep,
    title: str = Form(...),
    file: UploadFile = File(...),
):
    document = await service.create_document(
        title=title,
        file=file,
        user=current_user,
    )

    background_tasks.add_task(
        service.process_document,
        document.id,
    )

    return document


@router.post(
    "/{document_id}/retry",
    response_model=DocumentRead,
    summary="Retry document processing",
)
async def retry_document_processing(
    document_id: int,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    service: DocumentServiceDep,
):
    document = await service.retry_processing(
        document_id,
        current_user,
    )

    background_tasks.add_task(
        service.process_document,
        document.id,
    )

    return document


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Get document metadata",
)
async def get_document(
    document_id: int,
    current_user: CurrentUser,
    service: DocumentServiceDep,
):
    return await service.get_document(
        document_id,
        current_user,
    )


@router.get(
    "/{document_id}/content",
    response_model=DocumentContent,
    summary="Get document extracted content",
)
async def get_document_content(
    document_id: int,
    current_user: CurrentUser,
    service: DocumentServiceDep,
):
    document = await service.get_document(
        document_id,
        current_user,
    )

    if document.status == DocumentStatus.PROCESSING.value:
        raise DocumentAlreadyProcessingError()

    if document.status == DocumentStatus.FAILED.value:
        raise DocumentProcessingFailedError()

    return DocumentContent(
        id=document.id,
        title=document.title,
        content=document.content,
    )


@router.get(
    "/{document_id}/download",
    summary="Download document",
)
async def download_document(
    document_id: int,
    current_user: CurrentUser,
    service: DocumentServiceDep,
):
    document = await service.get_document(
        document_id,
        current_user,
    )

    if not Path(document.file_path).exists():
        raise DocumentNotFoundError()

    return FileResponse(
        path=document.file_path,
        filename=document.filename,
        media_type=document.mime_type,
    )


@router.patch(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Update document",
)
async def update_document(
    document_id: int,
    current_user: CurrentUser,
    service: DocumentServiceDep,
    data: DocumentUpdate,
):
    return await service.update_document(
        document_id,
        data,
        current_user,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
)
async def delete_document(
    document_id: int,
    current_user: CurrentUser,
    service: DocumentServiceDep,
):
    await service.delete_document(
        document_id,
        current_user,
    )