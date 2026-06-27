"""
News fetcher module - Handles fetching news from multiple API sources
Supports: NewsAPI, New York Times API, Guardian API
"""

import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio

from .models import NewsArticle
from backend.config.settings import get_settings
from backend.config.sources import GLOBAL_NEWS_SOURCES, RATE_LIMITS

logger = logging.getLogger(__name__)
settings = get_settings()


class NewsAPIFetcher:
    """Fetcher for NewsAPI.org"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_by_category(
        self,
        category: str,
        country: Optional[str] = None,
        limit: int = 10,
        days: int = 1,
    ) -> List[NewsArticle]:
        """
        Fetch news by category and optional country
        
        Args:
            category: News category (business, technology, sports, health, etc.)
            country: Country code (us, in, gb, etc.)
            limit: Number of articles to fetch
            days: How many days back to search
            
        Returns:
            List of NewsArticle objects
        """
        try:
            from_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            params = {
                "apiKey": self.api_key,
                "sortBy": "publishedAt",
                "pageSize": limit,
                "language": "en",
            }

            if category and category != "general":
                params["category"] = category

            if country:
                # Use top-headlines endpoint for country filtering
                endpoint = f"{self.base_url}/top-headlines"
                params["country"] = country
            else:
                # Use everything endpoint for global news
                endpoint = f"{self.base_url}/everything"
                params["from"] = from_date

            async with self.session.get(endpoint, params=params, timeout=10) as resp:
                if resp.status != 200:
                    logger.error(f"NewsAPI error: {resp.status}")
                    return []

                data = await resp.json()
                articles = []

                for article in data.get("articles", []):
                    try:
                        news_article = NewsArticle(
                            title=article.get("title", ""),
                            description=article.get("description", ""),
                            content=article.get("content", ""),
                            url=article.get("url", ""),
                            image_url=article.get("urlToImage", ""),
                            source_name=article.get("source", {}).get("name", "Unknown"),
                            source_id=article.get("source", {}).get("id", "unknown"),
                            published_at=datetime.fromisoformat(
                                article.get("publishedAt", "").replace("Z", "+00:00")
                            ),
                            category=category or "general",
                            author=article.get("author", ""),
                        )
                        articles.append(news_article)
                    except Exception as e:
                        logger.warning(f"Error parsing article: {e}")
                        continue

                return articles

        except asyncio.TimeoutError:
            logger.error("NewsAPI request timeout")
            return []
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
            return []

    async def search_news(
        self,
        query: str,
        limit: int = 10,
        days: int = 7,
        sort_by: str = "publishedAt",
    ) -> List[NewsArticle]:
        """
        Search for news by keyword
        
        Args:
            query: Search query
            limit: Number of results
            days: Days to search back
            sort_by: Sort order
            
        Returns:
            List of NewsArticle objects
        """
        try:
            from_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            params = {
                "q": query,
                "apiKey": self.api_key,
                "sortBy": sort_by,
                "pageSize": limit,
                "language": "en",
                "from": from_date,
            }

            async with self.session.get(
                f"{self.base_url}/everything", params=params, timeout=10
            ) as resp:
                if resp.status != 200:
                    logger.error(f"NewsAPI search error: {resp.status}")
                    return []

                data = await resp.json()
                articles = []

                for article in data.get("articles", []):
                    try:
                        news_article = NewsArticle(
                            title=article.get("title", ""),
                            description=article.get("description", ""),
                            content=article.get("content", ""),
                            url=article.get("url", ""),
                            image_url=article.get("urlToImage", ""),
                            source_name=article.get("source", {}).get("name", "Unknown"),
                            source_id=article.get("source", {}).get("id", "unknown"),
                            published_at=datetime.fromisoformat(
                                article.get("publishedAt", "").replace("Z", "+00:00")
                            ),
                            category="general",
                            author=article.get("author", ""),
                        )
                        articles.append(news_article)
                    except Exception as e:
                        logger.warning(f"Error parsing article: {e}")
                        continue

                return articles

        except asyncio.TimeoutError:
            logger.error("NewsAPI search timeout")
            return []
        except Exception as e:
            logger.error(f"Error searching NewsAPI: {e}")
            return []


class NYTFetcher:
    """Fetcher for New York Times API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.nytimes.com/svc/topstories/v2"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_by_section(
        self, section: str = "home", limit: int = 10
    ) -> List[NewsArticle]:
        """
        Fetch top stories from a section
        
        Args:
            section: NYT section (home, world, us, business, technology, etc.)
            limit: Number of articles
            
        Returns:
            List of NewsArticle objects
        """
        try:
            params = {
                "api-key": self.api_key,
            }

            async with self.session.get(
                f"{self.base_url}/{section}.json", params=params, timeout=10
            ) as resp:
                if resp.status != 200:
                    logger.error(f"NYT API error: {resp.status}")
                    return []

                data = await resp.json()
                articles = []

                for article in data.get("results", [])[:limit]:
                    try:
                        # Get image URL
                        image_url = ""
                        if article.get("multimedia"):
                            image_url = article["multimedia"][0].get("url", "")

                        # Map NYT section to category
                        category_map = {
                            "business": "business",
                            "technology": "technology",
                            "sports": "sports",
                            "health": "health",
                            "arts": "entertainment",
                            "world": "general",
                        }
                        category = category_map.get(section, "general")

                        news_article = NewsArticle(
                            title=article.get("title", ""),
                            description=article.get("abstract", ""),
                            content=article.get("lead_paragraph", ""),
                            url=article.get("url", ""),
                            image_url=image_url,
                            source_name="New York Times",
                            source_id="nyt",
                            published_at=datetime.fromisoformat(
                                article.get("published_date", "")
                            ),
                            category=category,
                            author=article.get("byline", ""),
                        )
                        articles.append(news_article)
                    except Exception as e:
                        logger.warning(f"Error parsing NYT article: {e}")
                        continue

                return articles

        except asyncio.TimeoutError:
            logger.error("NYT API request timeout")
            return []
        except Exception as e:
            logger.error(f"Error fetching from NYT API: {e}")
            return []


class GuardianFetcher:
    """Fetcher for The Guardian API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://open-platform.theguardian.com/live"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_by_section(
        self, section: str = "world", limit: int = 10
    ) -> List[NewsArticle]:
        """
        Fetch articles from a section
        
        Args:
            section: Guardian section
            limit: Number of articles
            
        Returns:
            List of NewsArticle objects
        """
        try:
            params = {
                "section": section,
                "api-key": self.api_key,
                "page-size": limit,
                "show-fields": "byline,thumbnail",
            }

            async with self.session.get(
                self.base_url, params=params, timeout=10
            ) as resp:
                if resp.status != 200:
                    logger.error(f"Guardian API error: {resp.status}")
                    return []

                data = await resp.json()
                articles = []

                for article in data.get("response", {}).get("results", []):
                    try:
                        news_article = NewsArticle(
                            title=article.get("webTitle", ""),
                            description=article.get("fields", {}).get("trailText", ""),
                            url=article.get("webUrl", ""),
                            image_url=article.get("fields", {}).get("thumbnail", ""),
                            source_name="The Guardian",
                            source_id="guardian",
                            published_at=datetime.fromisoformat(
                                article.get("webPublicationDate", "").replace("Z", "+00:00")
                            ),
                            category=section,
                            author=article.get("fields", {}).get("byline", ""),
                        )
                        articles.append(news_article)
                    except Exception as e:
                        logger.warning(f"Error parsing Guardian article: {e}")
                        continue

                return articles

        except asyncio.TimeoutError:
            logger.error("Guardian API request timeout")
            return []
        except Exception as e:
            logger.error(f"Error fetching from Guardian API: {e}")
            return []


class NewsFetcher:
    """Main news fetcher orchestrator"""

    def __init__(self):
        self.settings = get_settings()
        self.newsapi_fetcher = None
        self.nyt_fetcher = None
        self.guardian_fetcher = None

    async def initialize(self):
        """Initialize all fetchers"""
        if self.settings.newsapi_key:
            self.newsapi_fetcher = NewsAPIFetcher(self.settings.newsapi_key)
            await self.newsapi_fetcher.__aenter__()

        if self.settings.nyt_api_key:
            self.nyt_fetcher = NYTFetcher(self.settings.nyt_api_key)
            await self.nyt_fetcher.__aenter__()

        if self.settings.guardian_api_key:
            self.guardian_fetcher = GuardianFetcher(self.settings.guardian_api_key)
            await self.guardian_fetcher.__aenter__()

    async def cleanup(self):
        """Cleanup all fetchers"""
        if self.newsapi_fetcher:
            await self.newsapi_fetcher.__aexit__(None, None, None)
        if self.nyt_fetcher:
            await self.nyt_fetcher.__aexit__(None, None, None)
        if self.guardian_fetcher:
            await self.guardian_fetcher.__aexit__(None, None, None)

    async def fetch_news(
        self,
        category: str = "general",
        region: str = "global",
        limit: int = 10,
        days: int = 1,
    ) -> List[NewsArticle]:
        """
        Fetch news from all available sources
        
        Args:
            category: News category
            region: Geographic region
            limit: Number of articles
            days: Days to search back
            
        Returns:
            Combined list of articles from all sources
        """
        all_articles = []

        # Determine country code from region
        country_map = {
            "india": "in",
            "us": "us",
            "uk": "gb",
            "global": None,
        }
        country = country_map.get(region)

        # Fetch from NewsAPI
        if self.newsapi_fetcher:
            try:
                articles = await self.newsapi_fetcher.fetch_by_category(
                    category=category,
                    country=country,
                    limit=limit,
                    days=days,
                )
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error fetching from NewsAPI: {e}")

        # Fetch from NYT (US only)
        if self.nyt_fetcher and region in ["us", "global"]:
            try:
                nyt_section_map = {
                    "business": "business",
                    "technology": "technology",
                    "sports": "sports",
                    "health": "health",
                    "entertainment": "arts",
                    "general": "home",
                }
                section = nyt_section_map.get(category, "home")
                articles = await self.nyt_fetcher.fetch_by_section(
                    section=section, limit=limit
                )
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error fetching from NYT: {e}")

        # Fetch from Guardian
        if self.guardian_fetcher:
            try:
                articles = await self.guardian_fetcher.fetch_by_section(
                    section=category if category != "general" else "world",
                    limit=limit,
                )
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error fetching from Guardian: {e}")

        # Remove duplicates based on URL
        unique_articles = {}
        for article in all_articles:
            if article.url not in unique_articles:
                unique_articles[article.url] = article

        # Sort by published date (most recent first)
        sorted_articles = sorted(
            unique_articles.values(),
            key=lambda x: x.published_at,
            reverse=True,
        )

        return sorted_articles[:limit]

    async def search_news(
        self, query: str, limit: int = 10, days: int = 7
    ) -> List[NewsArticle]:
        """
        Search for news across all sources
        
        Args:
            query: Search query
            limit: Number of results
            days: Days to search back
            
        Returns:
            List of matching articles
        """
        articles = []

        if self.newsapi_fetcher:
            try:
                results = await self.newsapi_fetcher.search_news(
                    query=query, limit=limit, days=days
                )
                articles.extend(results)
            except Exception as e:
                logger.error(f"Error searching NewsAPI: {e}")

        # Remove duplicates and sort
        unique_articles = {}
        for article in articles:
            if article.url not in unique_articles:
                unique_articles[article.url] = article

        sorted_articles = sorted(
            unique_articles.values(),
            key=lambda x: x.published_at,
            reverse=True,
        )

        return sorted_articles[:limit]
