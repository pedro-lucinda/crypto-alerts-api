"""
Application factory and startup for the Crypto Alerts API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import alerts, auth
from app.core.config import settings


def create_app() -> FastAPI:
    """
    Create and configure a FastAPI application instance.

    - Sets metadata (title, versioned docs URLs).
    - Applies CORS middleware.
    - Includes authentication and alerts routers under the v1 API prefix.
    """
    app_settings = FastAPI(
        title=settings.app_name,
        openapi_url=f"{settings.api_v1_str}/openapi.json",
        docs_url=f"{settings.api_v1_str}/docs",
    )

    # CORS middleware
    app_settings.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backends_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app_settings.include_router(
        auth.router,
        prefix=f"{settings.api_v1_str}/auth",
        tags=["auth"],
    )
    app_settings.include_router(
        alerts.router,
        prefix=f"{settings.api_v1_str}/alerts",
        tags=["alerts"],
    )

    return app_settings


# Instantiate the application for Uvicorn to discover
app = create_app()
