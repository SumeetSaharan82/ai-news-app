"""
News endpoints
Handles news fetching, processing, and analysis
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from backend.core.rss_fetcher import RSSFetcher, RSS_SOURCES
from backend.api.v1.auth import get_current_user
from backend.core.user_models import User, UserPreferences

router = APIRouter()

# Region code mapping to match RSS source regions
REGION_CODE_MAP = {
    'in': 'india',
    'us': 'us',
    'gb': 'gb',
    'ca': 'ca',
    'au': 'au',
    'de': 'de',
    'fr': 'fr',
    'it': 'it',
    'es': 'es',
    'nl': 'nl',
    'global': 'global'
}


class NewsArticle(BaseModel):
    """News article response model"""
    id: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    source: str
    url: str
    image_url: Optional[str] = None
    published_at: datetime
    category: str
    region: str
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    sentiment: Optional[str] = None


class NewsResponse(BaseModel):
    """News list response model"""
    total: int
    page: int
    per_page: int
    articles: List[NewsArticle]


@router.get("/news/rss")
async def get_rss_news(
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region"),
    limit: int = Query(10, ge=1, le=50, description="Articles per source")
):
    """
    Fetch news from RSS feeds
    Returns articles from RSS sources with optional filtering
    """
    try:
        fetcher = RSSFetcher()
        articles = await fetcher.fetch_all_sources(
            category=category,
            region=region,
            limit=limit
        )
        
        # Convert to response format
        article_list = []
        for article in articles:
            article_list.append({
                "id": article.source_id,
                "title": article.title,
                "description": article.description,
                "content": article.content,
                "source": article.source_name,
                "url": article.url,
                "image_url": article.image_url,
                "published_at": article.published_at.isoformat(),
                "category": article.category,
                "region": article.region,
                "author": article.author
            })
        
        return {
            "total": len(article_list),
            "articles": article_list,
            "category": category or "all",
            "region": region or "all"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching RSS news: {str(e)}")


@router.get("/news/personalized")
async def get_personalized_news(
    limit: int = Query(20, ge=1, le=100, description="Number of articles"),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized news based on user preferences
    Requires authentication
    """
    # Get user preferences
    user_prefs = UserPreferences.from_dict(
        current_user.preferences or UserPreferences().to_dict()
    )
    
    # Fetch news for each preferred category and region
    all_articles = []
    fetcher = RSSFetcher()
    
    # Limit per category to avoid too many articles
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
            except Exception as e:
                # Continue with other categories if one fails
                continue
    
    # Remove duplicates based on URL
    unique_articles = {}
    for article in all_articles:
        if article.url not in unique_articles:
            unique_articles[article.url] = article
    
    # Sort by published date
    sorted_articles = sorted(
        unique_articles.values(),
        key=lambda x: x.published_at,
        reverse=True
    )
    
    # Limit total articles
    final_articles = sorted_articles[:limit]
    
    # Convert to response format
    article_list = []
    for article in final_articles:
        article_list.append({
            "id": article.source_id,
            "title": article.title,
            "description": article.description,
            "content": article.content,
            "source": article.source_name,
            "url": article.url,
            "image_url": article.image_url,
            "published_at": article.published_at.isoformat(),
            "category": article.category,
            "region": article.region,
            "author": article.author
        })
    
    return {
        "total": len(article_list),
        "articles": article_list,
        "preferences": {
            "categories": user_prefs.categories,
            "regions": user_prefs.regions
        }
    }


@router.get("/news", response_model=NewsResponse)
async def get_news(
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query"),
    days: int = Query(7, ge=1, le=30, description="News from last N days"),
    sort_by: Optional[str] = Query("recent", description="Sort by: recent, popular, relevant"),
    source: Optional[str] = Query(None, description="Filter by source name"),
    exclude_sources: Optional[str] = Query(None, description="Comma-separated list of sources to exclude"),
    min_length: Optional[int] = Query(None, ge=0, description="Minimum content length"),
    has_image: Optional[bool] = Query(None, description="Filter by articles with images")
):
    """
    Get news articles with advanced filtering options
    
    Query Parameters:
    - category: Filter by news category (technology, business, sports, etc.)
    - region: Filter by region (us, gb, ca, etc.)
    - page: Pagination page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    - search: Search articles by keyword or phrase
    - days: Get news from last N days (default: 7, max: 30)
    - sort_by: Sort by recent, popular, or relevant (default: recent)
    - source: Filter by specific source name
    - exclude_sources: Comma-separated list of sources to exclude
    - min_length: Minimum content length in characters
    - has_image: Filter by articles with images
    """
    try:
        # Map region code to full name for RSS sources
        mapped_region = REGION_CODE_MAP.get(region, region)
        
        fetcher = RSSFetcher()
        articles = await fetcher.fetch_all_sources(
            category=category,
            region=mapped_region,
            limit=per_page * 2  # Fetch more for filtering
        )
        
        # Apply advanced filters
        filtered_articles = []
        
        for article in articles:
            # Source filter
            if source and article.source_name.lower() != source.lower():
                continue
            
            # Exclude sources filter
            if exclude_sources:
                excluded = [s.strip().lower() for s in exclude_sources.split(',')]
                if article.source_name.lower() in excluded:
                    continue
            
            # Min length filter
            if min_length and len(article.content or '') < min_length:
                continue
            
            # Has image filter
            if has_image is not None:
                has_img = bool(article.image_url)
                if has_image and not has_img:
                    continue
                if not has_image and has_img:
                    continue
            
            # Search filter
            if search:
                search_lower = search.lower()
                title_match = search_lower in article.title.lower()
                desc_match = search_lower in (article.description or '').lower()
                content_match = search_lower in (article.content or '').lower()
                
                if not (title_match or desc_match or content_match):
                    continue
            
            filtered_articles.append(article)
        
        # Sort articles
        if sort_by == "recent":
            filtered_articles.sort(key=lambda x: x.published_at, reverse=True)
        elif sort_by == "popular":
            # Placeholder - would need popularity metrics
            filtered_articles.sort(key=lambda x: x.published_at, reverse=True)
        elif sort_by == "relevant":
            # Placeholder - would need relevance scoring
            filtered_articles.sort(key=lambda x: x.published_at, reverse=True)
        
        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_articles = filtered_articles[start_idx:end_idx]
        
        # Convert to response format
        article_list = []
        for article in paginated_articles:
            article_list.append({
                "id": article.source_id,
                "title": article.title,
                "description": article.description,
                "content": article.content,
                "source": article.source_name,
                "url": article.url,
                "image_url": article.image_url,
                "published_at": article.published_at.isoformat(),
                "category": article.category,
                "region": article.region,
                "author": article.author
            })
        
        return {
            "total": len(filtered_articles),
            "page": page,
            "per_page": per_page,
            "articles": article_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")


@router.get("/news/{article_id}", response_model=NewsArticle)
async def get_news_detail(article_id: str):
    """
    Get detailed information about a specific news article
    Includes full content and AI-generated analysis
    """
    # This is a placeholder implementation
    # Will be implemented in Phase 1b
    raise HTTPException(status_code=404, detail="Article not found")


@router.post("/news/analyze")
async def analyze_article(
    url: str = Query(..., description="Article URL to analyze"),
    deep_analysis: bool = Query(False, description="Perform deep AI analysis")
):
    """
    Analyze a news article URL
    Extracts content and generates AI-powered summary and insights
    """
    # This is a placeholder implementation
    # Will integrate with RSS extraction and LLM analysis in Phase 1b
    return {
        "url": url,
        "status": "pending",
        "message": "Analysis queued for processing"
    }


@router.get("/news/feed/rss")
async def get_rss_feeds(
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get configured RSS feeds and their status
    Returns list of active RSS feed sources
    """
    feeds = []
    for source in RSS_SOURCES:
        if region and source.region != region:
            continue
        if category and source.category != category:
            continue
        feeds.append({
            "source_id": source.source_id,
            "name": source.name,
            "url": source.url,
            "category": source.category,
            "region": source.region
        })
    
    return {
        "feeds": feeds,
        "total": len(feeds),
        "last_update": datetime.utcnow().isoformat()
    }


@router.post("/news/feed/add")
async def add_rss_feed(
    feed_url: str = Query(..., description="RSS feed URL"),
    category: str = Query(..., description="Category for this feed")
):
    """
    Add a new RSS feed source
    Validates feed URL and adds it to the collection
    """
    # This is a placeholder implementation
    # Will validate and add RSS feeds in Phase 1b
    return {
        "status": "added",
        "feed_url": feed_url,
        "category": category
    }
