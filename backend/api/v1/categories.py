"""
Categories endpoints
Returns available news categories and regions
"""

from fastapi import APIRouter
from typing import List

router = APIRouter()

# Available news categories
CATEGORIES = [
    "technology",
    "business",
    "sports",
    "health",
    "science",
    "entertainment",
    "politics",
    "world",
    "finance",
    "general"
]

# Available regions
REGIONS = [
    "us",
    "gb",
    "ca",
    "au",
    "in",
    "de",
    "fr",
    "it",
    "es",
    "nl"
]


@router.get("/categories", response_model=List[str])
async def get_categories():
    """
    Get available news categories
    Returns a list of all supported news categories
    """
    return CATEGORIES


@router.get("/regions", response_model=List[str])
async def get_regions():
    """
    Get available regions
    Returns a list of all supported regions for news filtering
    """
    return REGIONS
