"""
Health check endpoints
"""

from fastapi import APIRouter
from datetime import datetime
from backend.config.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns application status and basic information
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat()
    }
