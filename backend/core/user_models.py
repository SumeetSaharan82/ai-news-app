"""
User database models for authentication and preferences
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """User model for authentication and preferences"""
    
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    
    # Preferences stored as JSON
    preferences = Column(JSON, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class UserPreferences:
    """User preferences structure"""
    
    def __init__(
        self,
        categories: Optional[list[str]] = None,
        regions: Optional[list[str]] = None,
        digest_frequency: str = "daily",
        email_notifications: bool = True,
        dark_mode: bool = False,
        keywords: Optional[list[str]] = None,
    ):
        self.categories = categories or ["general"]
        self.regions = regions or ["global"]
        self.digest_frequency = digest_frequency  # daily, weekly, none
        self.email_notifications = email_notifications
        self.dark_mode = dark_mode
        self.keywords = keywords or []
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            "categories": self.categories,
            "regions": self.regions,
            "digest_frequency": self.digest_frequency,
            "email_notifications": self.email_notifications,
            "dark_mode": self.dark_mode,
            "keywords": self.keywords,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserPreferences":
        """Create from dictionary"""
        return cls(
            categories=data.get("categories"),
            regions=data.get("regions"),
            digest_frequency=data.get("digest_frequency", "daily"),
            email_notifications=data.get("email_notifications", True),
            dark_mode=data.get("dark_mode", False),
            keywords=data.get("keywords"),
        )
