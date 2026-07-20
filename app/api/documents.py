from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from app.api.dependencies import (
    get_current_user,
    get_document_service,
)
from app.models.document import DocumentStatus
from app.models.user import User
from app.schemas.document import (
    DocumentContent,
    DocumentList,
    DocumentRead,
    DocumentUpdate,
)
from app.schemas.query import DocumentQueryParams
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "",
    response_model=DocumentList,
    summary="List user documents",
)
async def get_documents(
    params: DocumentQueryParams = Depends(),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
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
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
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


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Get document metadata",
)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    document = await service.get_document(
        document_id,
        current_user,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.get(
    "/{document_id}/content",
    response_model=DocumentContent,
    summary="Get document extracted content",
)
async def get_document_content(
    document_id: int,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    document = await service.get_document(
        document_id,
        current_user,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.status != DocumentStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document processing is not finished yet.",
        )

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
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    document = await service.get_document(
        document_id,
        current_user,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if not Path(document.file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

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
    data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    document = await service.update_document(
        document_id,
        data,
        current_user,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    deleted = await service.delete_document(
        document_id,
        current_user,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )