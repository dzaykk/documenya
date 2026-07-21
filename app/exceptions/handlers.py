from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.auth import (
    EmailAlreadyRegistered,
    UsernameAlreadyTaken,
    InvalidCredentials,
)

from app.exceptions.document import (
    DocumentNotFoundError,
    DocumentAlreadyProcessingError,
    DocumentAlreadyProcessedError,
    UnsupportedDocumentTypeError,
    EmptyDocumentError,
)


# AUTH

async def email_exists_handler(
    request: Request,
    exc: EmailAlreadyRegistered,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Email already registered"
        },
    )


async def username_taken_handler(
    request: Request,
    exc: UsernameAlreadyTaken,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Username already taken"
        },
    )


async def invalid_credentials_handler(
    request: Request,
    exc: InvalidCredentials,
):
    return JSONResponse(
        status_code=401,
        content={
            "detail": "Invalid credentials"
        },
    )

# DOCUMENT

async def document_not_found_handler(
    request: Request,
    exc: DocumentNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Document not found",
        },
    )


async def document_processing_handler(
    request: Request,
    exc: DocumentAlreadyProcessingError,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Document is already processing",
        },
    )


async def document_processed_handler(
    request: Request,
    exc: DocumentAlreadyProcessedError,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Document is already processed",
        },
    )


async def unsupported_document_handler(
    request: Request,
    exc: UnsupportedDocumentTypeError,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )


async def empty_document_handler(
    request: Request,
    exc: EmptyDocumentError,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )