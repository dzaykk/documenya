from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import DocumentRead
from app.services.document_service import DocumentService

from fastapi import APIRouter, Depends, File, Form, UploadFile

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "",
    response_model=DocumentRead,
    status_code=201,
)
async def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(db)

    return await service.create_document(
        title=title,
        file=file,
        user=current_user,
    )


@router.get(
    "",
    response_model=list[DocumentRead],
)
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = DocumentService(db)

    return await service.get_user_documents(
        current_user
    )


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = DocumentService(db)

    document = await service.get_document(
        document_id,
        current_user,
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = DocumentService(db)

    deleted = await service.delete_document(
        document_id,
        current_user,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )