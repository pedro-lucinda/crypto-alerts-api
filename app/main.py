from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

load_dotenv()


def create_app() -> FastAPI:
    """
    Create and configure a FastAPI application instance.

    - Sets metadata (title, versioned docs URLs).
    - Applies CORS middleware.
    - Includes all API v1 routers under `settings.api_v1_str`.
    """

    app_with_settings = FastAPI(
        title=settings.app_name,
        openapi_url=f"{settings.app_v1_str}/openapi.json",
        docs_url=f"{settings.app_v1_str}/docs",
    )

    app_with_settings.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backends_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app_with_settings


app = create_app()
