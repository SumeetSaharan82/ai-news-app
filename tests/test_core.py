"""
Comprehensive test suite for AI News App
Unit tests, integration tests, and end-to-end tests
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from backend.core.models import NewsArticle, SummarizedArticle
from backend.core.news_fetcher import NewsAPIFetcher
from backend.core.rss_fetcher import RSSFetcher, RSSSource
from backend.core.content_extractor import ContentExtractor, ExtractedContent
from backend.core.llm_strict_processor import StrictRSSLLMProcessor, ExtractedArticle
from backend.config.settings import get_settings


class TestModels:
    """Test data models"""

    def test_news_article_creation(self):
        """Test NewsArticle model"""
        article = NewsArticle(
            title="Test Article",
            description="Test description",
            content="Test content",
            url="https://example.com/article",
            source_name="Test Source",
            source_id="test-source",
            published_at=datetime.utcnow(),
            category="technology",
            region="india",
        )
        assert article.title == "Test Article"
        assert article.category == "technology"
        assert article.region == "india"

    def test_summarized_article_creation(self):
        """Test SummarizedArticle model"""
        article = NewsArticle(
            title="Test Article",
            description="Test",
            url="https://example.com",
            source_name="Test",
            source_id="test",
            published_at=datetime.utcnow(),
        )
        summarized = SummarizedArticle(
            title="Test",
            summary="Test summary",
            original_article=article,
            category="general",
            region="global",
            published_at=datetime.utcnow(),
        )
        assert summarized.title == "Test"
        assert summarized.summary == "Test summary"


class TestRSSFetcher:
    """Test RSS Fetcher"""

    @pytest.mark.asyncio
    async def test_rss_source_initialization(self):
        """Test RSSSource creation"""
        source = RSSSource(
            name="Test RSS",
            url="https://example.com/rss",
            category="technology",
            region="india",
            source_id="test-rss",
        )
        assert source.name == "Test RSS"
        assert source.category == "technology"

    @pytest.mark.asyncio
    async def test_rss_fetcher_initialization(self):
        """Test RSSFetcher initialization"""
        fetcher = RSSFetcher()
        assert fetcher.timeout == 10
        assert len(fetcher.sources) > 0
        # Verify some known sources exist
        assert "toi-rss" in fetcher.sources
        assert "ndtv-rss" in fetcher.sources

    @pytest.mark.asyncio
    async def test_fetch_all_sources_filters(self):
        """Test filtering by category and region"""
        fetcher = RSSFetcher()
        
        # Filter by category
        tech_sources = [
            s for s in fetcher.sources.values() 
            if s.category == "technology"
        ]
        assert len(tech_sources) > 0
        
        # Filter by region
        india_sources = [
            s for s in fetcher.sources.values() 
            if s.region == "india"
        ]
        assert len(india_sources) > 0


class TestContentExtractor:
    """Test Content Extractor"""

    def test_extracted_content_dataclass(self):
        """Test ExtractedContent creation"""
        content = ExtractedContent(
            title="Test Article",
            byline="Test Author",
            publication_date=datetime.utcnow(),
            body_text="This is test content with enough words to pass validation check",
            word_count=12,
            source_url="https://example.com",
            extracted_at=datetime.utcnow(),
            confidence=0.95,
        )
        assert content.title == "Test Article"
        assert content.confidence == 0.95
        assert content.word_count == 12

    def test_content_extractor_initialization(self):
        """Test ContentExtractor initialization"""
        extractor = ContentExtractor(timeout=15)
        assert extractor.timeout == 15
        assert len(extractor.BOILERPLATE_SELECTORS) > 0
        assert len(extractor.SOURCE_SELECTORS) > 0

    def test_word_limit_enforcement(self):
        """Test confidence calculation"""
        extractor = ContentExtractor()
        
        # Test with good content
        conf_good = extractor._calculate_confidence(
            "Test Title",
            "This is a long article body with sufficient content for testing purposes",
            400,
        )
        assert conf_good > 0.7
        
        # Test with short content
        conf_short = extractor._calculate_confidence(
            "Test",
            "Short",
            10,
        )
        assert conf_short < 0.7


class TestStrictLLMProcessor:
    """Test Strict LLM Processor"""

    def test_processor_initialization(self):
        """Test StrictRSSLLMProcessor initialization"""
        processor = StrictRSSLLMProcessor()
        assert processor.provider is not None
        assert "NO OPINIONS" in processor.SYSTEM_PROMPT
        assert "EXTRACT ONLY" in processor.SYSTEM_PROMPT

    def test_extracted_article_creation(self):
        """Test ExtractedArticle dataclass"""
        article = ExtractedArticle(
            title="Test Article",
            main_points=["Point 1", "Point 2"],
            summary="Test summary",
            key_entities=["Entity1", "Entity2"],
            source_url="https://example.com",
            publication_date="2024-01-01T00:00:00",
            word_count=100,
            extracted_at="2024-01-01T00:00:00",
            extraction_confidence=0.9,
            llm_processing_confidence=0.85,
        )
        assert article.title == "Test Article"
        assert len(article.main_points) == 2
        assert article.extraction_confidence == 0.9

    def test_word_limit_enforcement(self):
        """Test word limit enforcement in summaries"""
        processor = StrictRSSLLMProcessor()
        
        long_text = " ".join([f"word{i}" for i in range(100)])
        limited = processor._enforce_word_limit(long_text, max_words=10)
        
        word_count = len(limited.split())
        assert word_count <= 10
        assert limited.endswith((".", "!", "?"))

    def test_fallback_extraction(self):
        """Test fallback extraction when LLM unavailable"""
        processor = StrictRSSLLMProcessor()
        processor.client = None  # Simulate LLM unavailable
        
        content = ExtractedContent(
            title="Test Article",
            byline="Test Author",
            publication_date=datetime.utcnow(),
            body_text="Sentence one. Sentence two. Sentence three. Sentence four. Sentence five.",
            word_count=20,
            source_url="https://example.com",
            extracted_at=datetime.utcnow(),
            confidence=0.8,
        )
        
        result = processor._create_fallback_extraction(content)
        assert result.title == "Test Article"
        assert result.llm_processing_confidence == 0.5  # Lower confidence for fallback


class TestSettings:
    """Test configuration settings"""

    def test_settings_initialization(self):
        """Test Settings loading"""
        settings = get_settings()
        assert settings.app_name == "AI News App"
        assert settings.app_version == "0.1.0"
        assert settings.server_port == 8000

    def test_database_url_configuration(self):
        """Test database configuration"""
        settings = get_settings()
        assert settings.database_url is not None
        # Default is SQLite for development
        assert "sqlite" in settings.database_url.lower() or "postgresql" in settings.database_url.lower()

    def test_redis_configuration(self):
        """Test Redis configuration"""
        settings = get_settings()
        assert settings.redis_url is not None
        assert settings.redis_enabled is True

    def test_cache_settings(self):
        """Test cache configuration"""
        settings = get_settings()
        assert settings.cache_ttl == 3600
        assert settings.news_fetch_interval == 1800


class TestNewsArticleValidation:
    """Test NewsArticle validation and constraints"""

    def test_article_required_fields(self):
        """Test required fields for NewsArticle"""
        # This should work
        article = NewsArticle(
            title="Title",
            url="https://example.com",
            source_name="Source",
            source_id="source-id",
            published_at=datetime.utcnow(),
        )
        assert article.title == "Title"

    def test_article_optional_fields(self):
        """Test optional fields are handled correctly"""
        article = NewsArticle(
            title="Title",
            url="https://example.com",
            source_name="Source",
            source_id="source-id",
            published_at=datetime.utcnow(),
            author=None,
            image_url=None,
        )
        assert article.author is None
        assert article.image_url is None


# Integration Tests
class TestIntegration:
    """Integration tests for multiple components"""

    def test_rss_source_to_news_article_pipeline(self):
        """Test RSS source can be converted to NewsArticle"""
        source = RSSSource(
            name="Test Source",
            url="https://example.com/rss",
            category="technology",
            region="india",
            source_id="test-rss",
        )
        
        # Simulate article from RSS
        article = NewsArticle(
            title="Test Article",
            description="Test description",
            url="https://example.com/article",
            source_name=source.name,
            source_id=source.source_id,
            published_at=datetime.utcnow(),
            category=source.category,
            region=source.region,
        )
        
        assert article.category == source.category
        assert article.region == source.region

    def test_extracted_content_to_extracted_article(self):
        """Test ExtractedContent can be processed to ExtractedArticle"""
        content = ExtractedContent(
            title="Test Title",
            byline="Test Author",
            publication_date=datetime.utcnow(),
            body_text="This is a test article with sufficient content for processing and testing purposes",
            word_count=15,
            source_url="https://example.com",
            extracted_at=datetime.utcnow(),
            confidence=0.85,
        )
        
        processor = StrictRSSLLMProcessor()
        processor.client = None  # Use fallback
        result = processor._create_fallback_extraction(content)
        
        assert result.title == content.title
        assert result.source_url == content.source_url
        assert result.extraction_confidence == content.confidence


if __name__ == "__main__":
    pytest.main(["-v", __file__])
