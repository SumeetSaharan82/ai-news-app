"""
Updated FastAPI application entry point
Includes separate routers for API and RSS endpoints
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.responses import JSONResponse

from backend.config.settings import get_settings
from backend.api.routes import router as router_unified
from backend.api.routes_api import router_api
from backend.api.routes_rss import router_rss
from backend.core.database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()
db_manager = DatabaseManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("Starting AI News App...")
    try:
        await db_manager.initialize()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Error starting application: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI News App...")
    await db_manager.close()
    logger.info("Application shut down successfully")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered news aggregation with API and RSS sources",
    version=settings.app_version,
    lifespan=lifespan,
    debug=settings.debug,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZIPMiddleware, minimum_size=1000)

# Include routers
app.include_router(router_api)  # API-based endpoints
app.include_router(router_rss)   # RSS-based endpoints
app.include_router(router_unified)  # Unified endpoints (Phase 1c)


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def root():
    """Root endpoint with documentation"""
    return {
        "message": "AI News App API",
        "version": settings.app_version,
        "endpoints": {
            "api_based_news": "/api/v1/news/api",
            "rss_based_news": "/api/v1/news/rss",
            "unified_news": "/api/v1/news/unified",
            "api_sources": "/api/v1/news/api/sources",
            "rss_sources": "/api/v1/news/rss/sources",
            "categories": "/api/v1/categories",
            "regions": "/api/v1/regions",
            "search": "/api/v1/search",
            "health": "/api/v1/health",
        },
        "docs": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main_modular:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
    )
