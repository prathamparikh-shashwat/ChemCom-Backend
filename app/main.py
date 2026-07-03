from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup behavior: auto-create tables for SQLite development environment
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown behavior (if any required)


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include core routing
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["status"])
def root():
    """Root endpoint welcoming users."""
    return {
        "message": "Welcome to the standard FastAPI Backend template.",
        "docs_url": "/docs"
    }


@app.get("/health", tags=["status"])
def health_check():
    """Simple API health check endpoint."""
    return {
        "status": "healthy",
        "project_name": settings.PROJECT_NAME
    }
