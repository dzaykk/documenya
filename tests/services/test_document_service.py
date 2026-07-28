from unittest.mock import AsyncMock, patch

import pytest

from app.exceptions.document import (
    DocumentNotFoundError,
)
from app.schemas.document import (
    DocumentUpdate,
)
from app.services.document_service import (
    DocumentService,
)


@pytest.fixture
def service(
    uow,
    storage_service,
):
    return DocumentService(
        uow=uow,
        storage_service=storage_service,
    )


@pytest.mark.asyncio
async def test_create_document_success(
    service,
    uow,
    storage_service,
    upload_file,
    user,
):
    storage_service.save_file.return_value = (
        "stored.txt",
        "/tmp/stored.txt",
        123,
    )

    uow.documents.create.side_effect = (
        lambda document: document
    )

    with patch(
        "app.services.document_service.FileValidationService.validate",
        new=AsyncMock(),
    ):
        result = await service.create_document(
            title="My document",
            file=upload_file,
            user=user,
        )

    assert result.title == "My document"
    assert result.filename == "stored.txt"
    assert result.file_path == "/tmp/stored.txt"
    assert result.file_size == 123
    assert result.owner_id == user.id

    storage_service.save_file.assert_awaited_once_with(
        upload_file,
    )

    uow.documents.create.assert_awaited_once()

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_document_validation_failed(
    service,
    storage_service,
    upload_file,
    user,
):
    with patch(
        "app.services.document_service.FileValidationService.validate",
        new=AsyncMock(
            side_effect=ValueError(
                "invalid file",
            ),
        ),
    ):
        with pytest.raises(
            ValueError,
        ):
            await service.create_document(
                title="Document",
                file=upload_file,
                user=user,
            )

    storage_service.save_file.assert_not_called()


@pytest.mark.asyncio
async def test_create_document_database_error_removes_uploaded_file(
    service,
    uow,
    storage_service,
    upload_file,
    user,
):
    storage_service.save_file.return_value = (
        "stored.txt",
        "/tmp/stored.txt",
        123,
    )

    uow.documents.create.side_effect = RuntimeError(
        "database error",
    )

    with patch(
        "app.services.document_service.FileValidationService.validate",
        new=AsyncMock(),
    ):
        with pytest.raises(
            RuntimeError,
        ):
            await service.create_document(
                title="Document",
                file=upload_file,
                user=user,
            )

    storage_service.delete_file.assert_awaited_once_with(
        "/tmp/stored.txt",
    )

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_document_success(
    service,
    uow,
    document,
    user,
):
    uow.documents.get_by_id.return_value = (
        document
    )

    result = await service.get_document(
        document.id,
        user,
    )

    assert result is document

    uow.documents.get_by_id.assert_awaited_once_with(
        document.id,
        user.id,
    )


@pytest.mark.asyncio
async def test_get_document_not_found(
    service,
    uow,
    user,
):
    uow.documents.get_by_id.return_value = None

    with pytest.raises(
        DocumentNotFoundError,
    ):
        await service.get_document(
            999,
            user,
        )

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_documents_success(
    service,
    uow,
    document,
    user,
    query_params,
):
    uow.documents.get_user_documents.return_value = [
        document,
    ]

    uow.documents.count_user_documents.return_value = 21

    result = await service.get_user_documents(
        user,
        query_params,
    )

    assert result.total == 21
    assert result.page == 1
    assert result.limit == 20
    assert result.pages == 2

    assert len(result.items) == 1

    item = result.items[0]

    assert item.id == document.id
    assert item.title == document.title
    assert item.filename == document.filename
    assert item.mime_type == document.mime_type
    assert item.file_size == document.file_size

    uow.documents.get_user_documents.assert_awaited_once_with(
        user.id,
        query_params.search,
        query_params.page,
        query_params.limit,
    )


@pytest.mark.asyncio
async def test_update_document_success(
    service,
    uow,
    document,
    user,
):
    uow.documents.get_by_id.return_value = (
        document
    )

    uow.documents.update.return_value = (
        document
    )

    result = await service.update_document(
        document.id,
        DocumentUpdate(
            title="Updated title",
        ),
        user,
    )

    assert result is document

    assert document.title == (
        "Updated title"
    )

    uow.documents.update.assert_awaited_once_with(
        document,
    )

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_document_not_found(
    service,
    uow,
    user,
):
    uow.documents.get_by_id.return_value = None

    with pytest.raises(
        DocumentNotFoundError,
    ):
        await service.update_document(
            999,
            DocumentUpdate(
                title="Updated",
            ),
            user,
        )

    uow.documents.update.assert_not_called()

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_document_success(
    service,
    uow,
    storage_service,
    document,
    user,
):
    uow.documents.get_by_id.return_value = (
        document
    )

    await service.delete_document(
        document.id,
        user,
    )

    uow.documents.delete.assert_awaited_once_with(
        document,
    )

    uow.commit.assert_awaited_once()

    storage_service.delete_file.assert_awaited_once_with(
        document.file_path,
    )


@pytest.mark.asyncio
async def test_delete_document_not_found(
    service,
    uow,
    storage_service,
    user,
):
    uow.documents.get_by_id.return_value = None

    with pytest.raises(
        DocumentNotFoundError,
    ):
        await service.delete_document(
            999,
            user,
        )

    uow.documents.delete.assert_not_called()

    storage_service.delete_file.assert_not_called()


@pytest.mark.asyncio
async def test_delete_document_storage_failure_after_commit(
    service,
    uow,
    storage_service,
    document,
    user,
):
    uow.documents.get_by_id.return_value = (
        document
    )

    storage_service.delete_file.side_effect = (
        RuntimeError(
            "storage error",
        )
    )

    with pytest.raises(
        RuntimeError,
    ):
        await service.delete_document(
            document.id,
            user,
        )

    uow.documents.delete.assert_awaited_once_with(
        document,
    )

    uow.commit.assert_awaited_once()