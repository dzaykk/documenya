import logging

from fastapi import Request
from starlette.responses import Response
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.exceptions.base import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> Response:

    logger.warning(
        "%s %s -> %s (%d)",
        request.method,
        request.url.path,
        exc.detail,
        exc.status_code,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
        },
    )


async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
) -> Response:

    logger.exception(
        "Database integrity error on %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=409,
        content={
            "detail": "Resource already exists",
        },
    )