"""
FastAPI routes for API-based news endpoints
Separate from RSS endpoints for independent testing and validation
Uses NewsAPI, NYT, and Guardian APIs
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.api.schemas import NewsResponseData, ArticleResponse
from backend.core.news_fetcher import NewsFetcher
from backend.core.llm_processor import LLMProcessor
from backend.config.sources import NEWS_CATEGORIES, REGIONS
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)
router_api = APIRouter(prefix="/api/v1/news", tags=["API-based News"])

settings = get_settings()

# Initialize services
fetcher = None
processor = None


async def get_fetcher() -> NewsFetcher:
    """Get or initialize news fetcher"""
    global fetcher
    if fetcher is None:
        fetcher = NewsFetcher()
        await fetcher.initialize()
    return fetcher


async def get_processor() -> LLMProcessor:
    """Get or initialize LLM processor"""
    global processor
    if processor is None:
        processor = LLMProcessor()
    return processor


@router_api.get("/api", response_model=NewsResponseData)
async def get_news_from_api(
    category: str = Query("general", description="News category"),
    region: str = Query("global", description="Geographic region"),
    limit: int = Query(5, ge=1, le=50, description="Number of articles"),
    days: int = Query(1, ge=1, le=30, description="Days to look back"),
) -> NewsResponseData:
    """
    Fetch and summarize news from API sources
    
    This endpoint uses structured APIs (NewsAPI, NYT, Guardian)
    which provide pre-formatted articles.
    
    Query Parameters:
    - category: business, technology, sports, health, entertainment, science, general
    - region: global, india, us, uk
    - limit: 1-50 articles (default: 5)
    - days: 1-30 days to look back (default: 1)
    """
    try:
        # Validate inputs
        if category not in NEWS_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Supported: {list(NEWS_CATEGORIES.keys())}",
            )
        
        if region not in REGIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid region. Supported: {list(REGIONS.keys())}",
            )
        
        # Fetch news from APIs
        fetcher = await get_fetcher()
        articles = await fetcher.fetch_news(
            category=category,
            region=region,
            limit=limit,
            days=days,
        )
        
        if not articles:
            return NewsResponseData(
                success=False,
                message="No articles found from API sources for the specified criteria",
                category=category,
                region=region,
                generated_at=datetime.utcnow(),
            )
        
        # Summarize articles with LLM (standard processor - allows some analysis)
        processor = await get_processor()
        summarized_articles = await processor.batch_process(
            articles,
            include_sentiment=True,
            include_key_points=True,
        )
        
        # Convert to response format
        response_articles = [
            ArticleResponse(
                title=article.title,
                summary=article.summary,
                category=article.category,
                region=article.region,
                published_at=article.published_at,
                source_name=article.original_article.source_name,
                url=article.original_article.url,
                image_url=article.original_article.image_url,
            )
            for article in summarized_articles
        ]
        
        return NewsResponseData(
            success=True,
            message="Successfully retrieved and summarized news from APIs",
            data=response_articles,
            total_count=len(response_articles),
            category=category,
            region=region,
            generated_at=datetime.utcnow(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching API news: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching API news",
        )


@router_api.get("/api/sources")
async def get_api_sources():
    """
    Get list of available API sources
    """
    from backend.config.sources import GLOBAL_NEWS_SOURCES
    
    api_sources = {
        key: value
        for key, value in GLOBAL_NEWS_SOURCES.items()
        if value.get("api") == "newsapi" or value.get("api") == "nyt" or value.get("api") == "guardian"
    }
    
    return {
        "total_sources": len(api_sources),
        "sources": api_sources,
    }
