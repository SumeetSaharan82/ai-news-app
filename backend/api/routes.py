"""
FastAPI routes for news API endpoints
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.api.schemas import NewsResponseData, ArticleResponse, NewsQueryRequest, ErrorResponse, HealthCheckResponse
from backend.core.news_fetcher import NewsFetcher
from backend.core.llm_processor import LLMProcessor
from backend.config.sources import NEWS_CATEGORIES, REGIONS
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["news"])

# Initialize services
fetcher = None
processor = None
settings = get_settings()


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


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.utcnow(),
    )


@router.post("/news", response_model=NewsResponseData)
async def get_news(
    category: str = Query("general", description="News category"),
    region: str = Query("global", description="Geographic region"),
    limit: int = Query(5, ge=1, le=50, description="Number of articles"),
    days: int = Query(1, ge=1, le=30, description="Days to look back"),
) -> NewsResponseData:
    """
    Fetch and summarize news
    
    Query Parameters:
    - category: business, technology, sports, health, entertainment, science, general
    - region: global, india, us, uk
    - limit: 1-50 articles (default: 5)
    - days: 1-30 days (default: 1)
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
        
        # Fetch news
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
                message="No news found for the specified criteria",
                category=category,
                region=region,
            )
        
        # Summarize articles
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
            message="Successfully retrieved and summarized news",
            data=response_articles,
            total_count=len(response_articles),
            category=category,
            region=region,
            generated_at=datetime.utcnow(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching news",
        )


@router.get("/categories")
async def get_categories():
    """Get available news categories"""
    return {
        "categories": NEWS_CATEGORIES,
    }


@router.get("/regions")
async def get_regions():
    """Get available regions"""
    return {
        "regions": REGIONS,
    }


@router.post("/search")
async def search_news(
    query: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(7, ge=1, le=30),
) -> NewsResponseData:
    """
    Search for news by keyword
    
    Query Parameters:
    - query: Search keyword(s)
    - limit: Number of results (1-50)
    - days: Days to search (1-30)
    """
    try:
        fetcher = await get_fetcher()
        articles = await fetcher.search_news(
            query=query,
            limit=limit,
            days=days,
        )
        
        if not articles:
            return NewsResponseData(
                success=False,
                message=f"No news found for query: {query}",
                category="search",
                region="global",
            )
        
        processor = await get_processor()
        summarized_articles = await processor.batch_process(
            articles,
            include_sentiment=True,
        )
        
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
            message=f"Found {len(response_articles)} articles for query: {query}",
            data=response_articles,
            total_count=len(response_articles),
            category="search",
            region="global",
            generated_at=datetime.utcnow(),
        )
    
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while searching news",
        )
