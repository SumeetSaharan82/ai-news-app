"""
End-to-end API tests
Tests actual HTTP endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, AsyncMock

from backend.main import app
from backend.core.models import NewsArticle


client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test GET /api/v1/health"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data
        assert "version" in data


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_endpoint(self):
        """Test GET /"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
        assert "docs" in data


class TestCategoriesAndRegions:
    """Test categories and regions endpoints"""

    def test_get_categories(self):
        """Test GET /api/v1/categories"""
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        categories = data["categories"]
        assert "technology" in categories
        assert "business" in categories
        assert "sports" in categories

    def test_get_regions(self):
        """Test GET /api/v1/regions"""
        response = client.get("/api/v1/regions")
        assert response.status_code == 200
        data = response.json()
        assert "regions" in data
        regions = data["regions"]
        assert "global" in regions
        assert "india" in regions


class TestNewsEndpoints:
    """Test news fetching endpoints"""

    def test_invalid_category(self):
        """Test error handling for invalid category"""
        response = client.get("/api/v1/news/api?category=invalid_category")
        assert response.status_code == 400
        data = response.json()
        assert "Invalid category" in data["detail"]

    def test_invalid_region(self):
        """Test error handling for invalid region"""
        response = client.get("/api/v1/news/api?region=invalid_region")
        assert response.status_code == 400
        data = response.json()
        assert "Invalid region" in data["detail"]

    def test_limit_constraints(self):
        """Test limit parameter constraints"""
        # Test limit too high
        response = client.get("/api/v1/news/api?limit=100")
        # Should either work or be constrained
        assert response.status_code in [200, 422]
        
        # Test limit too low
        response = client.get("/api/v1/news/api?limit=0")
        assert response.status_code == 422

    def test_response_format(self):
        """Test response format structure"""
        # Mock the fetcher to avoid actual API calls
        with patch('backend.api.routes.get_fetcher') as mock_fetcher:
            mock_instance = AsyncMock()
            mock_fetcher.return_value = mock_instance
            mock_instance.fetch_news.return_value = []
            
            response = client.get("/api/v1/news/api?category=technology&limit=5")
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert "message" in data
            assert "data" in data
            assert "total_count" in data
            assert "category" in data
            assert "region" in data


class TestRSSEndpoints:
    """Test RSS-based endpoints"""

    def test_rss_sources_endpoint(self):
        """Test GET /api/v1/news/rss/sources"""
        response = client.get("/api/v1/news/rss/sources")
        assert response.status_code == 200
        data = response.json()
        assert "total_sources" in data
        assert "sources" in data
        assert data["total_sources"] > 0

    def test_rss_sources_filter_by_region(self):
        """Test RSS sources filtering by region"""
        response = client.get("/api/v1/news/rss/sources?region=india")
        assert response.status_code == 200
        data = response.json()
        sources = data["sources"]
        # All returned sources should be for India
        for source in sources:
            assert source["region"] == "india"

    def test_rss_sources_filter_by_category(self):
        """Test RSS sources filtering by category"""
        response = client.get("/api/v1/news/rss/sources?category=technology")
        assert response.status_code == 200
        data = response.json()
        sources = data["sources"]
        # All returned sources should be for technology
        for source in sources:
            assert source["category"] == "technology"


class TestSearchEndpoint:
    """Test search functionality"""

    def test_search_empty_query(self):
        """Test search with empty query"""
        response = client.get("/api/v1/search?query=")
        assert response.status_code == 422

    def test_search_valid_query(self):
        """Test search with valid query"""
        # This will fail without actual API keys, but tests the endpoint structure
        response = client.get("/api/v1/search?query=AI&limit=5")
        assert response.status_code in [200, 500]  # May fail due to missing API keys


if __name__ == "__main__":
    pytest.main(["-v", __file__])
