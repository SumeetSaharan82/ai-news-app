"""
User endpoints
Handles user profiles, preferences, and subscriptions
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from backend.core.database import get_db
from backend.core.user_models import User, UserPreferences
from backend.api.v1.auth import get_current_user

router = APIRouter()


class UserProfile(BaseModel):
    """User profile model"""
    id: str
    email: str
    name: Optional[str] = None
    preferences: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class UserPreferencesUpdate(BaseModel):
    """User preferences update model"""
    categories: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    digest_frequency: Optional[str] = None  # daily, weekly, none
    email_notifications: Optional[bool] = None
    dark_mode: Optional[bool] = None
    keywords: Optional[List[str]] = None
    # NOTE: tier is NOT settable by users — only via verified payment webhook (/api/v1/usage/update-tier)


@router.get("/users/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile information
    Requires authentication
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        preferences=current_user.preferences,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.put("/users/profile")
async def update_user_profile(
    name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    Requires authentication
    """
    if name is not None:
        current_user.name = name
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "updated_at": current_user.updated_at.isoformat(),
    }


@router.get("/users/preferences")
async def get_user_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's news preferences
    Requires authentication
    """
    return current_user.preferences or UserPreferences().to_dict()


@router.put("/users/preferences")
async def update_user_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's news preferences
    Requires authentication
    """
    # Get current preferences or create default
    current_prefs = UserPreferences.from_dict(
        current_user.preferences or UserPreferences().to_dict()
    )
    
    # Update only provided fields
    if preferences_update.categories is not None:
        current_prefs.categories = preferences_update.categories
    if preferences_update.regions is not None:
        current_prefs.regions = preferences_update.regions
    if preferences_update.digest_frequency is not None:
        current_prefs.digest_frequency = preferences_update.digest_frequency
    if preferences_update.email_notifications is not None:
        current_prefs.email_notifications = preferences_update.email_notifications
    if preferences_update.dark_mode is not None:
        current_prefs.dark_mode = preferences_update.dark_mode
    if preferences_update.keywords is not None:
        current_prefs.keywords = preferences_update.keywords
    # Save to database
    current_user.preferences = current_prefs.to_dict()
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user.preferences


@router.post("/users/subscribe")
async def subscribe_category(
    category: str = Query(..., description="Category to subscribe to"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Subscribe to a news category
    """
    current_prefs = UserPreferences.from_dict(
        current_user.preferences or UserPreferences().to_dict()
    )
    
    if category not in current_prefs.categories:
        current_prefs.categories.append(category)
        current_user.preferences = current_prefs.to_dict()
        current_user.updated_at = datetime.utcnow()
        db.commit()
    
    return {"status": "subscribed", "category": category, "categories": current_prefs.categories}


@router.post("/users/unsubscribe")
async def unsubscribe_category(
    category: str = Query(..., description="Category to unsubscribe from"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unsubscribe from a news category
    """
    current_prefs = UserPreferences.from_dict(
        current_user.preferences or UserPreferences().to_dict()
    )
    
    if category in current_prefs.categories:
        current_prefs.categories.remove(category)
        current_user.preferences = current_prefs.to_dict()
        current_user.updated_at = datetime.utcnow()
        db.commit()
    
    return {"status": "unsubscribed", "category": category, "categories": current_prefs.categories}
