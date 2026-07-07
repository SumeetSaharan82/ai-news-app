"""
Mobile app API endpoints
Optimized for mobile applications with reduced payloads and mobile-specific features
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.core.database import get_db
from backend.core.rss_fetcher import RSSFetcher
from backend.api.v1.auth import get_current_user
from backend.core.user_models import User, UserPreferences

router = APIRouter()


@router.get("/mobile/news/compact")
async def get_compact_news(
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region"),
    limit: int = Query(20, ge=1, le=50, description="Number of articles"),
    current_user: User = Depends(get_current_user)
):
    """
    Get compact news feed optimized for mobile
    Returns minimal data to reduce bandwidth
    """
    try:
        fetcher = RSSFetcher()
        articles = await fetcher.fetch_all_sources(
            category=category,
            region=region,
            limit=limit
        )
        
        # Compact response format
        compact_articles = []
        for article in articles:
            compact_articles.append({
                "id": article.source_id,
                "t": article.title,  # Shortened key
                "s": article.source_name,
                "u": article.url,
                "p": article.published_at.isoformat(),
                "c": article.category,
                "i": article.image_url  # Include image for mobile
            })
        
        return {
            "articles": compact_articles,
            "count": len(compact_articles),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")


@router.get("/mobile/news/personalized")
async def get_mobile_personalized_news(
    limit: int = Query(15, ge=1, le=50, description="Number of articles"),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized news feed optimized for mobile
    """
    user_prefs = UserPreferences.from_dict(
        current_user.preferences or UserPreferences().to_dict()
    )
    
    all_articles = []
    fetcher = RSSFetcher()
    
    per_category_limit = max(1, limit // max(len(user_prefs.categories), 1))
    
    for category in user_prefs.categories:
        for region in user_prefs.regions:
            try:
                articles = await fetcher.fetch_all_sources(
                    category=category,
                    region=region,
                    limit=per_category_limit
                )
                all_articles.extend(articles)
            except Exception:
                continue
    
    # Remove duplicates and sort
    unique_articles = {}
    for article in all_articles:
        if article.url not in unique_articles:
            unique_articles[article.url] = article
    
    sorted_articles = sorted(
        unique_articles.values(),
        key=lambda x: x.published_at,
        reverse=True
    )
    
    final_articles = sorted_articles[:limit]
    
    # Compact format
    compact_articles = []
    for article in final_articles:
        compact_articles.append({
            "id": article.source_id,
            "t": article.title,
            "s": article.source_name,
            "u": article.url,
            "p": article.published_at.isoformat(),
            "c": article.category,
            "i": article.image_url
        })
    
    return {
        "articles": compact_articles,
        "count": len(compact_articles),
        "preferences": {
            "categories": user_prefs.categories,
            "regions": user_prefs.regions
        }
    }


@router.get("/mobile/article/{article_id}")
async def get_mobile_article_detail(
    article_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get article details optimized for mobile reading
    """
    # This would fetch from database or cache
    # For now, return a placeholder
    return {
        "id": article_id,
        "title": "Article Title",
        "content": "Article content here...",
        "source": "Source Name",
        "published_at": datetime.utcnow().isoformat(),
        "readable": True
    }


@router.get("/mobile/categories")
async def get_mobile_categories(
    current_user: User = Depends(get_current_user)
):
    """
    Get categories with user's subscriptions highlighted
    """
    from backend.config.sources import SUPPORTED_CATEGORIES
    
    user_prefs = UserPreferences.from_dict(
        current_user.preferences or UserPreferences().to_dict()
    )
    
    categories = []
    for category in SUPPORTED_CATEGORIES:
        categories.append({
            "name": category,
            "subscribed": category in user_prefs.categories
        })
    
    return {
        "categories": categories
    }


@router.get("/mobile/regions")
async def get_mobile_regions(
    current_user: User = Depends(get_current_user)
):
    """
    Get regions with user's subscriptions highlighted
    """
    from backend.config.sources import SUPPORTED_REGIONS
    
    user_prefs = UserPreferences.from_dict(
        current_user.preferences or UserPreferences().to_dict()
    )
    
    regions = []
    for region in SUPPORTED_REGIONS:
        regions.append({
            "name": region,
            "subscribed": region in user_prefs.regions
        })
    
    return {
        "regions": regions
    }


@router.post("/mobile/preferences")
async def update_mobile_preferences(
    categories: Optional[List[str]] = None,
    regions: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user preferences from mobile app
    Simplified endpoint for mobile
    """
    from backend.api.users import UserPreferencesUpdate
    
    preferences_update = UserPreferencesUpdate(
        categories=categories,
        regions=regions
    )
    
    user_prefs = UserPreferences.from_dict(
        current_user.preferences or UserPreferences().to_dict()
    )
    
    if categories is not None:
        user_prefs.categories = categories
    if regions is not None:
        user_prefs.regions = regions
    
    current_user.preferences = user_prefs.to_dict()
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "status": "updated",
        "preferences": current_user.preferences
    }


@router.get("/mobile/sync")
async def mobile_sync(
    last_sync: Optional[str] = Query(None, description="Last sync timestamp"),
    current_user: User = Depends(get_current_user)
):
    """
    Sync data for mobile app
    Returns only changed data since last sync
    """
    # Parse last sync timestamp
    last_sync_dt = None
    if last_sync:
        try:
            last_sync_dt = datetime.fromisoformat(last_sync)
        except:
            pass
    
    # Get user preferences
    user_prefs = UserPreferences.from_dict(
        current_user.preferences or UserPreferences().to_dict()
    )
    
    # Fetch recent articles if no sync or old sync
    if not last_sync_dt or (datetime.utcnow() - last_sync_dt).total_seconds() > 3600:
        fetcher = RSSFetcher()
        articles = await fetcher.fetch_all_sources(
            category=user_prefs.categories[0] if user_prefs.categories else None,
            region=user_prefs.regions[0] if user_prefs.regions else None,
            limit=10
        )
        
        compact_articles = []
        for article in articles:
            compact_articles.append({
                "id": article.source_id,
                "t": article.title,
                "s": article.source_name,
                "u": article.url,
                "p": article.published_at.isoformat(),
                "c": article.category
            })
    else:
        compact_articles = []
    
    return {
        "sync_timestamp": datetime.utcnow().isoformat(),
        "has_updates": len(compact_articles) > 0,
        "articles": compact_articles,
        "preferences": user_prefs.to_dict()
    }
