from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.auth import (
    EmailAlreadyRegistered,
    UsernameAlreadyTaken,
    InvalidCredentials,
)


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