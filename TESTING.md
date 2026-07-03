"""
Local testing guide and examples
How to test the AI News App locally
"""

# TESTING GUIDE FOR AI NEWS APP

## 📋 Prerequisites

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip3 install -r requirements.txt
pip3 install pytest pytest-asyncio pytest-cov

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# - NEWSAPI_KEY
# - NYT_API_KEY
# - GUARDIAN_API_KEY
# - OPENAI_API_KEY (or ANTHROPIC_API_KEY)
# - DATABASE_URL (optional, uses SQLite by default)
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage Report
```bash
pytest --cov=backend --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_core.py
pytest tests/test_api.py
```

### Run Specific Test Class
```bash
pytest tests/test_core.py::TestModels
pytest tests/test_api.py::TestHealthEndpoint
```

### Run Specific Test Function
```bash
pytest tests/test_core.py::TestModels::test_news_article_creation
```

### Run Tests Matching Pattern
```bash
pytest -k "test_health"  # Runs all tests with "health" in name
```

## 🚀 Starting the Application

### Start Local Server
```bash
# From project root
python -m backend.main

# Or using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: http://localhost:8000

## 📊 Testing Endpoints Locally

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health

# Expected Response:
# {"status":"healthy","app_name":"AI News App","version":"0.1.0","timestamp":"..."}
```

### 2. Get Categories
```bash
curl http://localhost:8000/api/v1/categories

# Expected Response shows all categories like technology, business, sports, etc.
```

### 3. Get Regions
```bash
curl http://localhost:8000/api/v1/regions

# Expected Response shows all regions: global, india, us, uk
```

### 4. Get RSS Sources
```bash
curl http://localhost:8000/api/v1/news/rss/sources

# Expected Response: List of 15+ RSS sources
```

### 5. Filter RSS Sources by Region
```bash
curl "http://localhost:8000/api/v1/news/rss/sources?region=india"

# Expected: Only Indian RSS sources
```

### 6. Filter RSS Sources by Category
```bash
curl "http://localhost:8000/api/v1/news/rss/sources?category=technology"

# Expected: Only technology RSS sources
```

### 7. Fetch News from API Sources
```bash
curl "http://localhost:8000/api/v1/news/api?category=technology&region=india&limit=3"

# Expected Response:
# {
#   "success": true,
#   "message": "Successfully retrieved and summarized news from APIs",
#   "data": [...articles...],
#   "total_count": 3,
#   "category": "technology",
#   "region": "india",
#   "generated_at": "..."
# }
```

### 8. Fetch News from RSS Sources
```bash
curl "http://localhost:8000/api/v1/news/rss?category=technology&region=india&limit=3"

# This will:
# 1. Fetch from RSS feeds
# 2. Extract article content from links
# 3. Process with strict LLM (no opinions)
# 4. Return clean factual summaries
```

### 9. Search News
```bash
curl "http://localhost:8000/api/v1/search?query=AI%20startup&limit=5&days=7"
```

### 10. Invalid Parameters (Error Testing)
```bash
# Invalid category
curl "http://localhost:8000/api/v1/news/api?category=invalid"
# Expected: 400 Bad Request

# Invalid region
curl "http://localhost:8000/api/v1/news/api?region=invalid"
# Expected: 400 Bad Request

# Limit too low
curl "http://localhost:8000/api/v1/news/api?limit=0"
# Expected: 422 Unprocessable Entity
```

## 🌐 Interactive Testing with Swagger UI

Visit: http://localhost:8000/docs

This provides an interactive interface to:
- See all endpoints
- Try endpoints with parameters
- See request/response examples
- View data schemas

## 📈 Testing Different Components

### Test RSS Fetcher Only
```python
import asyncio
from backend.core.rss_fetcher import RSSFetcher

async def test_rss():
    fetcher = RSSFetcher()
    articles = await fetcher.fetch_all_sources(
        category="technology",
        region="india",
        limit=3
    )
    print(f"Fetched {len(articles)} articles")
    for article in articles:
        print(f"- {article.title}")

asyncio.run(test_rss())
```

### Test Content Extractor
```python
import asyncio
from backend.core.content_extractor import ContentExtractor

async def test_extraction():
    url = "https://example.com/article"
    async with ContentExtractor() as extractor:
        content = await extractor.extract(url)
        if content:
            print(f"Title: {content.title}")
            print(f"Word Count: {content.word_count}")
            print(f"Confidence: {content.confidence}")
        else:
            print("Extraction failed")

asyncio.run(test_extraction())
```

### Test Strict LLM Processor
```python
import asyncio
from backend.core.llm_strict_processor import StrictRSSLLMProcessor
from backend.core.content_extractor import ExtractedContent
from datetime import datetime

async def test_llm():
    processor = StrictRSSLLMProcessor()
    
    content = ExtractedContent(
        title="Test Article",
        byline="Author",
        publication_date=datetime.utcnow(),
        body_text="Article text here...",
        word_count=100,
        source_url="https://example.com",
        extracted_at=datetime.utcnow(),
        confidence=0.85,
    )
    
    result = await processor.process_extracted_content(content)
    if result:
        print(f"Summary: {result.summary}")
        print(f"Main Points: {result.main_points}")
        print(f"Entities: {result.key_entities}")

asyncio.run(test_llm())
```

## ✅ Database Configuration

### Using SQLite (Default - Local Testing)
```
DATABASE_URL=sqlite:///./news_app.db
```

### Using PostgreSQL (Production)
```
DATABASE_URL=postgresql://user:password@localhost:5432/ai_news_app
```

## 📊 Database: Summary

**Current Setup**: SQLite (lightweight, no setup needed)
**Default File**: `news_app.db` in project root

**Tables Created Automatically**:
- `articles` - Stores all fetched and processed articles

**Can Switch To**: PostgreSQL for production

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'backend'"
**Solution**: Make sure you're in project root and virtual environment is activated

### Issue: "API keys not configured"
**Solution**: Check .env file has:
```
NEWSAPI_KEY=your_key
OPENAI_API_KEY=your_key
```

### Issue: "Connection refused" on localhost:8000
**Solution**: Start the server with:
```bash
python -m backend.main
```

### Issue: Tests fail with "ResourceWarning"
**Solution**: This is normal for async tests, can ignore or use:
```bash
pytest -W ignore::ResourceWarning
```

## 📝 Test Coverage Report

After running tests with coverage:
```bash
pytest --cov=backend --cov-report=html
```

Open `htmlcov/index.html` in browser to see coverage report

## 🎯 Testing Checklist

- [ ] Run all tests: `pytest`
- [ ] Check coverage: `pytest --cov=backend`
- [ ] Start server: `python -m backend.main`
- [ ] Test health check: `curl http://localhost:8000/api/v1/health`
- [ ] Test RSS sources: `curl http://localhost:8000/api/v1/news/rss/sources`
- [ ] Test API sources: `curl http://localhost:8000/api/v1/news/api/sources`
- [ ] Visit Swagger docs: http://localhost:8000/docs
- [ ] Verify RSS fetching works
- [ ] Verify content extraction works
- [ ] Verify LLM processing (no opinions)
- [ ] Check database is created
- [ ] Test with invalid parameters (error handling)

## 🚀 Next Steps

1. ✅ Run all tests locally
2. ✅ Verify endpoints work
3. ✅ Test with Swagger UI
4. ✅ Check database creation
5. ⏳ Set up continuous testing with GitHub Actions
6. ⏳ Deploy to staging
7. ⏳ Deploy to production
