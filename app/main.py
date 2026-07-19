from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, documents, users
from app.core.config import settings

from app.exceptions.auth import (
    EmailAlreadyRegistered,
    UsernameAlreadyTaken,
    InvalidCredentials,
)

from app.exceptions.handlers import (
    email_exists_handler,
    username_taken_handler,
    invalid_credentials_handler,
)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


# Exception handlers
app.add_exception_handler(
    EmailAlreadyRegistered,
    email_exists_handler,
)

app.add_exception_handler(
    UsernameAlreadyTaken,
    username_taken_handler,
)

app.add_exception_handler(
    InvalidCredentials,
    invalid_credentials_handler,
)


# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(
    auth.router
)

app.include_router(
    users.router
)

app.include_router(
    documents.router
)


# Health check
@app.get(
    "/health",
    tags=["Health"],
)
async def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
    }