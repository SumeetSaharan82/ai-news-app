"""
Test configuration and fixtures
"""

import pytest
import os
from dotenv import load_dotenv

# Load test environment
load_dotenv()


@pytest.fixture(scope="session")
def test_settings():
    """Provide test settings"""
    from backend.config.settings import get_settings
    return get_settings()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_article():
    """Provide a sample NewsArticle for testing"""
    from backend.core.models import NewsArticle
    from datetime import datetime
    
    return NewsArticle(
        title="Test News Article",
        description="This is a test article description",
        content="This is the full content of the test article with enough text for processing",
        url="https://example.com/article",
        image_url="https://example.com/image.jpg",
        source_name="Test Source",
        source_id="test-source",
        published_at=datetime.utcnow(),
        category="technology",
        region="india",
        author="Test Author",
    )


@pytest.fixture
def sample_extracted_content():
    """Provide sample ExtractedContent for testing"""
    from backend.core.content_extractor import ExtractedContent
    from datetime import datetime
    
    return ExtractedContent(
        title="Extracted Article Title",
        byline="Article Author Name",
        publication_date=datetime.utcnow(),
        body_text="This is the extracted article body with sufficient content for testing and validation purposes.",
        word_count=15,
        source_url="https://example.com/article",
        extracted_at=datetime.utcnow(),
        confidence=0.85,
    )


pytestmark = pytest.mark.asyncio
