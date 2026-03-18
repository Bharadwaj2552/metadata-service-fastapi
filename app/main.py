"""Main FastAPI application"""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import datasets_routes, lineage_routes, search_routes


# Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup - gracefully handle database connection failures
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("   App will run in read-only mode without database persistence")
        print("   To enable database features, start MySQL and restart the app")
    yield
    # Shutdown


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)


# Include routers
app.include_router(datasets_routes.router)
app.include_router(lineage_routes.router)
app.include_router(search_routes.router)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "details": exc.errors()
        }
    )


# Health check endpoint
@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    responses={200: {"description": "Service is healthy"}}
)
def health_check():
    """Check if the API service is running"""
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get(
    "/",
    tags=["info"],
    summary="API information",
    responses={200: {"description": "API information"}}
)
def root():
    """Get API information and available endpoints"""
    return {
        "message": "Metadata Management Service",
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "datasets": "/api/v1/datasets",
            "lineage": "/api/v1/lineage",
            "search": "/api/v1/search"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
