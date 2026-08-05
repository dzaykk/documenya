import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.api import auth, documents, users, query
from app.core.config import settings
from app.core.logging import setup_logging
from app.exceptions.base import AppException
from app.exceptions.handlers import (
    app_exception_handler,
    integrity_error_handler,
)

setup_logging()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    logger.info(
        "Application starting",
    )

    yield

    logger.info(
        "Application stopped",
    )


def create_app() -> FastAPI:

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Exception handlers
    app.add_exception_handler(
        AppException,
        app_exception_handler, # type: ignore[arg-type]
    )

    app.add_exception_handler(
        IntegrityError,
        integrity_error_handler, # type: ignore[arg-type]
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
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(documents.router)
    app.include_router(query.router)

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

    return app


app = create_app()