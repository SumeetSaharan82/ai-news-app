"""
Analysis endpoints
Handles sentiment analysis and news trend analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from backend.core.database import get_db
from backend.core.sentiment_analyzer import sentiment_analyzer
from backend.core.rss_fetcher import RSSFetcher
from backend.api.v1.auth import get_current_user
from backend.core.user_models import User

router = APIRouter()


@router.post("/analysis/sentiment")
async def analyze_sentiment(
    text: str = Query(..., description="Text to analyze"),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze sentiment of provided text
    Requires authentication
    """
    result = await sentiment_analyzer.analyze_sentiment(text)
    
    return {
        "text": text[:100] + "..." if len(text) > 100 else text,
        "sentiment": result["sentiment"],
        "score": result["score"],
        "confidence": result["confidence"],
        "analyzed_at": datetime.utcnow().isoformat()
    }


@router.post("/analysis/article-sentiment")
async def analyze_article_sentiment(
    url: str = Query(..., description="Article URL to analyze"),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch article content and analyze its sentiment
    Requires authentication
    """
    try:
        # Fetch article content
        from backend.core.content_extractor import ContentExtractor
        
        async with ContentExtractor() as extractor:
            content = await extractor.extract(url)
            
            if not content:
                raise HTTPException(
                    status_code=404,
                    detail="Could not extract content from URL"
                )
        
        # Analyze sentiment
        text_to_analyze = f"{content.title}\n\n{content.body_text}"
        result = await sentiment_analyzer.analyze_sentiment(text_to_analyze)
        
        return {
            "url": url,
            "title": content.title,
            "sentiment": result["sentiment"],
            "score": result["score"],
            "confidence": result["confidence"],
            "word_count": content.word_count,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing article: {str(e)}"
        )


@router.get("/analysis/trends")
async def get_news_trends(
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region"),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze news trends over time
    Requires authentication
    """
    try:
        fetcher = RSSFetcher()
        articles = await fetcher.fetch_all_sources(
            category=category,
            region=region,
            limit=100
        )
        
        # Filter by date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_articles = [
            a for a in articles 
            if a.published_at and a.published_at >= cutoff_date
        ]
        
        # Analyze trends
        # Count articles by category
        category_counts = {}
        for article in recent_articles:
            cat = article.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Count articles by source
        source_counts = {}
        for article in recent_articles:
            source = article.source_name
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Group by date
        date_counts = {}
        for article in recent_articles:
            if article.published_at:
                date_key = article.published_at.strftime("%Y-%m-%d")
                date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        # Analyze sentiment distribution
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for article in recent_articles[:20]:  # Analyze sentiment for top 20
            text = f"{article.title} {article.description or ''}"
            result = await sentiment_analyzer.analyze_sentiment(text)
            sentiment_counts[result["sentiment"]] += 1
        
        return {
            "period": {
                "days": days,
                "from": cutoff_date.isoformat(),
                "to": datetime.utcnow().isoformat()
            },
            "total_articles": len(recent_articles),
            "category_distribution": category_counts,
            "source_distribution": source_counts,
            "daily_distribution": date_counts,
            "sentiment_distribution": sentiment_counts,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing trends: {str(e)}"
        )


@router.get("/analysis/keywords")
async def get_trending_keywords(
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region"),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    limit: int = Query(10, ge=1, le=50, description="Number of keywords to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Extract trending keywords from recent news
    Requires authentication
    """
    try:
        fetcher = RSSFetcher()
        articles = await fetcher.fetch_all_sources(
            category=category,
            region=region,
            limit=50
        )
        
        # Filter by date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_articles = [
            a for a in articles 
            if a.published_at and a.published_at >= cutoff_date
        ]
        
        # Extract keywords from titles and descriptions
        from collections import Counter
        import re
        
        words = []
        for article in recent_articles:
            # Combine title and description
            text = f"{article.title} {article.description or ''}"
            
            # Extract words (lowercase, alphanumeric)
            extracted = re.findall(r'\b[a-z]{3,}\b', text.lower())
            words.extend(extracted)
        
        # Count word frequency
        word_counts = Counter(words)
        
        # Filter out common words
        common_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been', 'this',
            'that', 'with', 'they', 'from', 'what', 'when', 'which', 'their',
            'will', 'more', 'about', 'than', 'into', 'over', 'after', 'news',
            'said', 'says', 'new', 'first', 'last', 'time', 'year', 'just'
        }
        
        filtered_counts = {
            word: count for word, count in word_counts.items()
            if word not in common_words and count > 1
        }
        
        # Get top keywords
        top_keywords = sorted(
            filtered_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return {
            "period": {
                "days": days,
                "from": cutoff_date.isoformat(),
                "to": datetime.utcnow().isoformat()
            },
            "total_articles_analyzed": len(recent_articles),
            "keywords": [
                {"keyword": word, "count": count}
                for word, count in top_keywords
            ],
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting keywords: {str(e)}"
        )
