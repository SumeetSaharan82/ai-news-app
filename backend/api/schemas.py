"""
Pydantic schemas for API request/response validation
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class NewsQueryRequest(BaseModel):
    """Request schema for fetching news"""

    category: str = Field(default="general", description="News category")
    region: str = Field(default="global", description="Geographic region")
    limit: int = Field(default=5, ge=1, le=50)
    days: int = Field(default=1, ge=1, le=30)
    search_query: Optional[str] = None


class ArticleResponse(BaseModel):
    """Response schema for a single article"""

    title: str
    summary: str
    category: str
    region: str
    published_at: datetime
    source_name: str
    url: str
    image_url: Optional[str] = None


class NewsResponseData(BaseModel):
    """Response schema for news endpoint"""

    success: bool
    message: str
    data: List[ArticleResponse]
    total_count: int
    generated_at: datetime


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str
    app_name: str
    version: str
    timestamp: datetime
