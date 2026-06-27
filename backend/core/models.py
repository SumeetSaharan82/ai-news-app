"""
Data models for news articles and related entities
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    """Base model for a news article"""

    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    source_name: str
    source_id: str
    published_at: datetime
    category: str = "general"
    region: str = "global"
    author: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Tech Giant Announces New AI Feature",
                "description": "Latest developments in artificial intelligence",
                "content": "Full article content here...",
                "url": "https://example.com/article",
                "image_url": "https://example.com/image.jpg",
                "source_name": "Reuters",
                "source_id": "reuters",
                "published_at": "2024-01-15T10:30:00",
                "category": "technology",
                "region": "global",
                "author": "John Doe",
            }
        }


class SummarizedArticle(BaseModel):
    """Model for a summarized news article"""

    id: Optional[str] = None
    title: str
    summary: str = Field(..., description="AI-generated summary (5-10 sentences)")
    original_article: NewsArticle
    summary_length: int = Field(default=150, description="Character count of summary")
    category: str
    region: str
    published_at: datetime
    sentiment: Optional[str] = None
    key_points: Optional[list[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "article_123",
                "title": "Tech Giant Announces New AI Feature",
                "summary": "A major tech company has unveiled a groundbreaking AI feature...",
                "original_article": {},
                "summary_length": 145,
                "category": "technology",
                "region": "global",
                "published_at": "2024-01-15T10:30:00",
                "sentiment": "positive",
                "key_points": ["AI feature", "Innovation", "Market impact"],
                "created_at": "2024-01-15T11:00:00",
            }
        }


class NewsQuery(BaseModel):
    """Model for news query parameters"""

    category: str = Field(default="general", description="News category")
    region: str = Field(default="global", description="Geographic region")
    limit: int = Field(default=5, ge=1, le=50, description="Number of articles")
    days: int = Field(default=1, ge=1, le=30, description="Number of days to look back")
    search_query: Optional[str] = None
    sort_by: str = Field(default="recent", description="Sort by: recent, popular, relevant")

    class Config:
        json_schema_extra = {
            "example": {
                "category": "technology",
                "region": "india",
                "limit": 5,
                "days": 1,
                "search_query": "AI startups",
                "sort_by": "recent",
            }
        }


class NewsResponse(BaseModel):
    """Model for API response"""

    success: bool
    message: str
    data: list[SummarizedArticle] = []
    total_count: int = 0
    category: str
    region: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully retrieved and summarized news",
                "data": [],
                "total_count": 5,
                "category": "technology",
                "region": "india",
                "generated_at": "2024-01-15T11:00:00",
            }
        }


class ErrorResponse(BaseModel):
    """Model for error response"""

    success: bool = False
    message: str
    error_code: str
    details: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Failed to fetch news",
                "error_code": "FETCH_ERROR",
                "details": "API key not configured",
            }
        }
