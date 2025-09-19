"""
Main application entry point for EGRC Core Service.

This module sets up the FastAPI application with GraphQL support
for the core EGRC functionality.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter
from strawberry.schema import Schema

from ..config.settings import settings
from ..core.auth import AuthMiddleware
from ..core.tenant import TenantMiddleware
from ..exceptions.exceptions import EGRCException
from ..logging.utils import get_logger
from .schema import Mutation, Query


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting EGRC Core Service")

    # Initialize services
    try:
        # Initialize database connections
        from .database import main_engine

        await main_engine.connect()

        logger.info("Core services initialized successfully")

    except Exception as e:
        logger.error("Failed to initialize core services", error=str(e))
        raise

    yield

    # Cleanup
    logger.info("Shutting down EGRC Core Service")
    from .database import close_all_connections

    await close_all_connections()
    logger.info("Core service shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="EGRC Core Service",
        description="Core EGRC functionality with GraphQL support",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Add middleware
    setup_middleware(app)

    # Add exception handlers
    setup_exception_handlers(app)

    # Add GraphQL
    setup_graphql(app)

    return app


def setup_middleware(app: FastAPI) -> None:
    """Setup application middleware."""

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted host middleware
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure based on your domain
        )

    # Custom middleware
    app.add_middleware(TenantMiddleware)
    app.add_middleware(AuthMiddleware)


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers."""

    @app.exception_handler(EGRCException)
    async def egrc_exception_handler(request, exc: EGRCException):
        """Handle EGRC exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """Handle general exceptions."""
        logger.error("Unhandled exception", error=str(exc), exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error",
            },
        )


def setup_graphql(app: FastAPI) -> None:
    """Setup GraphQL endpoint."""

    schema = Schema(query=Query, mutation=Mutation)
    graphql_app = GraphQLRouter(schema)

    app.include_router(graphql_app, prefix="/graphql")


# Create application instance
# app = create_app()  # Commented out to avoid import errors


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "egrc_core.main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=settings.is_development,
        log_level=settings.logging.level.lower(),
    )
