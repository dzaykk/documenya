import pytest

from app.exceptions.document import (
    DocumentAlreadyProcessingError,
    DocumentNotFoundError,
)
from app.models.document import (
    DocumentStatus,
)
from app.services.document_processing_service import (
    DocumentProcessingService,
)


@pytest.fixture
def service(
    uow,
    parser,
):
    return DocumentProcessingService(
        uow=uow,
        parser=parser,
    )


@pytest.mark.asyncio
async def test_process_document_success(
    service,
    uow,
    parser,
    document,
):
    uow.documents.get_by_id_unscoped.return_value = (
        document
    )

    parser.extract_text.return_value = (
        "document content"
    )

    await service.process_document(
        document.id,
    )

    assert document.content == (
        "document content"
    )

    assert document.status == (
        DocumentStatus.COMPLETED.value
    )

    assert document.processing_error is None

    parser.extract_text.assert_awaited_once_with(
        document.file_path,
        document.mime_type,
    )

    uow.documents.update.assert_awaited_once_with(
        document,
    )

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_document_parser_failure(
    service,
    uow,
    parser,
    document,
):
    uow.documents.get_by_id_unscoped.return_value = (
        document
    )

    parser.extract_text.side_effect = RuntimeError(
        "parser failed",
    )

    await service.process_document(
        document.id,
    )

    assert document.status == (
        DocumentStatus.FAILED.value
    )

    assert document.processing_error == (
        "parser failed"
    )

    assert document.content is None

    uow.documents.update.assert_awaited_once_with(
        document,
    )

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_document_file_error_saved(
    service,
    uow,
    parser,
    document,
):
    uow.documents.get_by_id_unscoped.return_value = (
        document
    )

    parser.extract_text.side_effect = FileNotFoundError(
        "missing file",
    )

    await service.process_document(
        document.id,
    )

    assert document.status == (
        DocumentStatus.FAILED.value
    )

    assert document.processing_error == (
        "missing file"
    )

    uow.documents.update.assert_awaited_once_with(
        document,
    )


@pytest.mark.asyncio
async def test_process_document_missing_document(
    service,
    uow,
):
    uow.documents.get_by_id_unscoped.return_value = None

    await service.process_document(
        999,
    )

    uow.documents.update.assert_not_called()

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_retry_processing_success(
    service,
    uow,
    document,
    user,
):
    document.status = (
        DocumentStatus.FAILED.value
    )

    document.content = (
        "old content"
    )

    document.processing_error = (
        "old error"
    )

    uow.documents.get_by_id.return_value = (
        document
    )

    uow.documents.update.return_value = (
        document
    )

    result = await service.retry_processing(
        document.id,
        user,
    )

    assert result is document

    assert document.status == (
        DocumentStatus.PROCESSING.value
    )

    assert document.content is None

    assert document.processing_error is None

    uow.documents.update.assert_awaited_once_with(
        document,
    )

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_retry_processing_document_not_found(
    service,
    uow,
    user,
):
    uow.documents.get_by_id.return_value = None

    with pytest.raises(
        DocumentNotFoundError,
    ):
        await service.retry_processing(
            999,
            user,
        )

    uow.documents.update.assert_not_called()

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_retry_processing_when_already_processing(
    service,
    uow,
    document,
    user,
):
    document.status = (
        DocumentStatus.PROCESSING.value
    )

    uow.documents.get_by_id.return_value = (
        document
    )

    with pytest.raises(
        DocumentAlreadyProcessingError,
    ):
        await service.retry_processing(
            document.id,
            user,
        )

    uow.documents.update.assert_not_called()

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_retry_processing_completed_document(
    service,
    uow,
    document,
    user,
):
    document.status = (
        DocumentStatus.COMPLETED.value
    )

    uow.documents.get_by_id.return_value = (
        document
    )

    uow.documents.update.return_value = (
        document
    )

    result = await service.retry_processing(
        document.id,
        user,
    )

    assert result.status == (
        DocumentStatus.PROCESSING.value
    )

    uow.documents.update.assert_awaited_once_with(
        document,
    )

    uow.commit.assert_awaited_once()