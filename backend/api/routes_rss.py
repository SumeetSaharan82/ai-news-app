"""
FastAPI routes for RSS-based news endpoints
Separate from API-based endpoints for independent testing
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.api.schemas import NewsResponseData, ArticleResponse
from backend.core.rss_fetcher import RSSFetcher
from backend.core.content_extractor import ContentExtractor
from backend.core.llm_strict_processor import StrictRSSLLMProcessor
from backend.config.sources import NEWS_CATEGORIES, REGIONS
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)
router_rss = APIRouter(prefix="/api/v1/news", tags=["RSS News"])

settings = get_settings()

# Initialize services
rss_fetcher = None
content_extractor = None
llm_processor = None


async def get_rss_fetcher() -> RSSFetcher:
    """Get or initialize RSS fetcher"""
    global rss_fetcher
    if rss_fetcher is None:
        rss_fetcher = RSSFetcher()
    return rss_fetcher


async def get_content_extractor() -> ContentExtractor:
    """Get or initialize content extractor"""
    global content_extractor
    if content_extractor is None:
        content_extractor = ContentExtractor()
    return content_extractor


async def get_llm_processor() -> StrictRSSLLMProcessor:
    """Get or initialize strict LLM processor"""
    global llm_processor
    if llm_processor is None:
        llm_processor = StrictRSSLLMProcessor()
    return llm_processor


@router_rss.get("/rss", response_model=NewsResponseData)
async def get_news_from_rss(
    category: str = Query("general", description="News category"),
    region: str = Query("global", description="Geographic region"),
    limit: int = Query(5, ge=1, le=50, description="Number of articles"),
) -> NewsResponseData:
    """
    Fetch news from RSS feeds
    
    This endpoint:
    1. Fetches RSS feeds
    2. Extracts article content from links
    3. Processes with strict LLM (no opinions)
    4. Returns clean, factual summaries
    
    Query Parameters:
    - category: business, technology, sports, health, entertainment, science, general
    - region: global, india, us, uk
    - limit: 1-50 articles (default: 5)
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
        
        # Fetch from RSS feeds
        fetcher = await get_rss_fetcher()
        rss_articles = await fetcher.fetch_all_sources(
            category=category,
            region=region,
            limit=limit,
        )
        
        if not rss_articles:
            return NewsResponseData(
                success=False,
                message="No RSS articles found for the specified criteria",
                category=category,
                region=region,
                generated_at=datetime.utcnow(),
            )
        
        # Extract content from article links
        extractor = await get_content_extractor()
        extracted_contents = []
        
        for article in rss_articles:
            content = await extractor.extract(article.url)
            if content and content.confidence > 0.4:  # Only keep confident extractions
                extracted_contents.append(content)
        
        if not extracted_contents:
            return NewsResponseData(
                success=False,
                message="Failed to extract content from RSS articles",
                category=category,
                region=region,
                generated_at=datetime.utcnow(),
            )
        
        # Process with strict LLM
        processor = await get_llm_processor()
        processed_articles = []
        
        for content in extracted_contents[:limit]:
            extracted_article = await processor.process_extracted_content(content)
            if extracted_article:
                processed_articles.append(extracted_article)
        
        if not processed_articles:
            return NewsResponseData(
                success=False,
                message="Failed to process articles with LLM",
                category=category,
                region=region,
                generated_at=datetime.utcnow(),
            )
        
        # Convert to response format
        response_articles = [
            ArticleResponse(
                title=article.title,
                summary=article.summary,
                category=category,
                region=region,
                published_at=datetime.fromisoformat(article.publication_date)
                if article.publication_date
                else datetime.utcnow(),
                source_name="RSS Feed",
                url=article.source_url,
                image_url=None,
            )
            for article in processed_articles
        ]
        
        return NewsResponseData(
            success=True,
            message=f"Successfully fetched and processed {len(response_articles)} articles from RSS feeds",
            data=response_articles,
            total_count=len(response_articles),
            category=category,
            region=region,
            generated_at=datetime.utcnow(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching RSS news: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching RSS news",
        )


@router_rss.get("/rss/sources")
async def get_rss_sources(
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """
    Get list of available RSS sources
    
    Query Parameters:
    - region: Optional filter by region
    - category: Optional filter by category
    """
    from backend.core.rss_fetcher import RSS_SOURCES
    
    sources = RSS_SOURCES
    
    if region:
        sources = [s for s in sources if s.region == region]
    
    if category:
        sources = [s for s in sources if s.category == category]
    
    return {
        "total_sources": len(sources),
        "sources": [
            {
                "name": source.name,
                "source_id": source.source_id,
                "category": source.category,
                "region": source.region,
                "url": source.url,
            }
            for source in sources
        ],
    }


@router_rss.get("/rss/extraction-stats")
async def get_extraction_stats():
    """
    Get statistics about content extraction
    Useful for monitoring extraction quality
    """
    return {
        "message": "Extraction statistics endpoint",
        "note": "Track extraction confidence, success rates, and performance metrics here",
        "metrics": {
            "total_extractions": 0,  # To be implemented with metrics collection
            "average_confidence": 0.0,
            "success_rate": 0.0,
            "average_extraction_time_ms": 0.0,
        },
    }
