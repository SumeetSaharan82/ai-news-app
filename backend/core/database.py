"""
Database models and operations
"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class StoredArticle(Base):
    """SQLAlchemy model for stored articles"""
    __tablename__ = "articles"

    id = Column(String, primary_key=True, index=True)
    title = Column(String(500), index=True)
    summary = Column(Text)
    content = Column(Text)
    url = Column(String, unique=True, index=True)
    image_url = Column(String, nullable=True)
    source_name = Column(String(100), index=True)
    source_id = Column(String(100))
    category = Column(String(50), index=True)
    region = Column(String(50), index=True)
    author = Column(String(200), nullable=True)
    sentiment = Column(String(20), nullable=True)
    published_at = Column(DateTime, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)
    summarized = Column(Boolean, default=False, index=True)
    read_count = Column(Integer, default=0)


class DatabaseManager:
    """Manage database connections and operations"""

    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.SessionLocal = None

    async def initialize(self):
        """Initialize database connection"""
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.settings.database_url,
                echo=self.settings.sqlalchemy_echo,
                future=True,
                poolclass=NullPool,
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")

    async def get_session(self) -> AsyncSession:
        """Get database session"""
        if not self.SessionLocal:
            await self.initialize()
        return self.SessionLocal()

    async def save_article(self, article: StoredArticle) -> StoredArticle:
        """Save article to database"""
        session = await self.get_session()
        try:
            session.add(article)
            await session.commit()
            await session.refresh(article)
            return article
        except Exception as e:
            await session.rollback()
            logger.error(f"Error saving article: {e}")
            raise
        finally:
            await session.close()

    async def get_article(self, article_id: str) -> Optional[StoredArticle]:
        """Get article by ID"""
        from sqlalchemy import select
        
        session = await self.get_session()
        try:
            result = await session.execute(
                select(StoredArticle).where(StoredArticle.id == article_id)
            )
            return result.scalars().first()
        finally:
            await session.close()

    async def get_articles_by_category(
        self,
        category: str,
        region: Optional[str] = None,
        limit: int = 10,
    ) -> List[StoredArticle]:
        """Get articles by category and optional region"""
        from sqlalchemy import select
        
        session = await self.get_session()
        try:
            query = select(StoredArticle).where(
                StoredArticle.category == category
            )
            
            if region:
                query = query.where(StoredArticle.region == region)
            
            query = query.order_by(StoredArticle.published_at.desc()).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
        finally:
            await session.close()
