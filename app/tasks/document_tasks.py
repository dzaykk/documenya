import asyncio
import logging

from app.db.session import AsyncSessionLocal

from app.services.document_parser_service import (
    DocumentParserService,
)
from app.services.document_processing_service import (
    DocumentProcessingService,
)
from app.uow.sqlalchemy import SQLAlchemyUnitOfWork
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={
        "max_retries": 3,
    },
)
def process_document_task(
    self,
    document_id: int,
) -> None:

    logger.info(
        "Celery task started for document %s",
        document_id,
    )

    try:

        asyncio.run(
            _process_document(
                document_id,
            )
        )

        logger.info(
            "Celery task finished for document %s",
            document_id,
        )

    except Exception:

        logger.exception(
            "Celery task failed for document %s",
            document_id,
        )

        raise


async def _process_document(
    document_id: int,
) -> None:

    logger.debug(
        "Creating processing context for document %s",
        document_id,
    )

    async with AsyncSessionLocal() as session:

        uow = SQLAlchemyUnitOfWork(
            session,
        )

        parser = DocumentParserService()

        service = DocumentProcessingService(
            uow=uow,
            parser=parser,
        )

        await service.process_document(
            document_id,
        )

    logger.debug(
        "Processing context closed for document %s",
        document_id,
    )