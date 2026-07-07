"""
Notification endpoints
Handles email notifications and preferences
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from backend.core.database import get_db
from backend.core.email_service import email_service
from backend.api.v1.auth import get_current_user
from backend.core.user_models import User, UserPreferences
from backend.core.rss_fetcher import RSSFetcher

router = APIRouter()


@router.post("/notifications/send-digest")
async def send_news_digest(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a news digest email to the current user
    Requires authentication
    """
    # Check if user has email notifications enabled
    user_prefs = UserPreferences.from_dict(
        current_user.preferences or UserPreferences().to_dict()
    )
    
    if not user_prefs.email_notifications:
        raise HTTPException(
            status_code=400,
            detail="Email notifications are disabled for this user"
        )
    
    # Fetch personalized news
    all_articles = []
    fetcher = RSSFetcher()
    
    per_category_limit = 5
    
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
    
    # Remove duplicates
    unique_articles = {}
    for article in all_articles:
        if article.url not in unique_articles:
            unique_articles[article.url] = article
    
    # Sort by date
    sorted_articles = sorted(
        unique_articles.values(),
        key=lambda x: x.published_at,
        reverse=True
    )
    
    # Take top 10 articles
    final_articles = sorted_articles[:10]
    
    # Convert to dict format
    articles_dict = []
    for article in final_articles:
        articles_dict.append({
            "title": article.title,
            "description": article.description,
            "content": article.content,
            "url": article.url,
            "source": article.source_name,
            "category": article.category,
            "published_at": article.published_at.isoformat() if article.published_at else None
        })
    
    # Send email
    success = await email_service.send_news_digest(
        to_email=current_user.email,
        user_name=current_user.name or current_user.email.split('@')[0],
        articles=articles_dict,
        categories=user_prefs.categories
    )
    
    if success:
        return {
            "status": "sent",
            "message": "News digest sent successfully",
            "articles_count": len(articles_dict),
            "sent_at": datetime.utcnow().isoformat()
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send news digest"
        )


@router.post("/notifications/test")
async def test_notification(
    current_user: User = Depends(get_current_user)
):
    """
    Send a test notification email
    Requires authentication
    """
    success = await email_service.send_email(
        to_email=current_user.email,
        subject="AI News App - Test Notification",
        html_content=f"""
        <h1>Test Notification</h1>
        <p>Hello {current_user.name or current_user.email.split('@')[0]},</p>
        <p>This is a test notification from AI News App.</p>
        <p>If you received this, email notifications are working correctly!</p>
        """,
        text_content=f"Test Notification\n\nHello {current_user.name or current_user.email.split('@')[0]},\n\nThis is a test notification from AI News App."
    )
    
    if success:
        return {
            "status": "sent",
            "message": "Test notification sent successfully"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send test notification"
        )


@router.put("/notifications/preferences")
async def update_notification_preferences(
    email_notifications: Optional[bool] = None,
    digest_frequency: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update notification preferences
    Requires authentication
    """
    user_prefs = UserPreferences.from_dict(
        current_user.preferences or UserPreferences().to_dict()
    )
    
    if email_notifications is not None:
        user_prefs.email_notifications = email_notifications
    
    if digest_frequency is not None:
        if digest_frequency not in ["daily", "weekly", "none"]:
            raise HTTPException(
                status_code=400,
                detail="digest_frequency must be one of: daily, weekly, none"
            )
        user_prefs.digest_frequency = digest_frequency
    
    # Save preferences
    current_user.preferences = user_prefs.to_dict()
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "status": "updated",
        "preferences": {
            "email_notifications": user_prefs.email_notifications,
            "digest_frequency": user_prefs.digest_frequency
        }
    }
