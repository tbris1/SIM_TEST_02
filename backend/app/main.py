"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

# Import API routers
from .api import sessions, actions, ehr

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="REST API for medical on-call simulation training platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


@app.get("/")
async def root():
    """API health check endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.version,
        "api_prefix": settings.api_prefix,
    }


# Register API routers
app.include_router(sessions.router, prefix=settings.api_prefix, tags=["sessions"])
app.include_router(actions.router, prefix=settings.api_prefix, tags=["actions"])
app.include_router(ehr.router, prefix=settings.api_prefix, tags=["ehr"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
