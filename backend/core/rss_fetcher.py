"""
RSS Feed fetcher and parser for news sources
Handles RSS parsing, link extraction, and article content retrieval
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Optional
from xml.etree import ElementTree as ET

import feedparser
import aiohttp
from bs4 import BeautifulSoup

from backend.core.models import NewsArticle

logger = logging.getLogger(__name__)


class RSSSource:
    """Configuration for RSS sources"""

    def __init__(
        self,
        name: str,
        url: str,
        category: str,
        region: str,
        source_id: str,
    ):
        self.name = name
        self.url = url
        self.category = category
        self.region = region
        self.source_id = source_id


# RSS Feed sources for Indian and Global news
RSS_SOURCES = [
    # Indian News Sources
    RSSSource(
        name="Times of India - Top Stories",
        url="https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        category="general",
        region="india",
        source_id="toi-rss",
    ),
    RSSSource(
        name="NDTV News",
        url="https://feeds.ndtv.com/ndtv/top-stories",
        category="general",
        region="india",
        source_id="ndtv-rss",
    ),
    RSSSource(
        name="The Hindu - Top Stories",
        url="https://www.thehindu.com/news/national/feeder/default.rss",
        category="general",
        region="india",
        source_id="hindu-rss",
    ),
    RSSSource(
        name="Indian Express - India News",
        url="https://indianexpress.com/feed/",
        category="general",
        region="india",
        source_id="ie-rss",
    ),
    RSSSource(
        name="Business Standard India",
        url="https://www.business-standard.com/rss/home_page_top_stories.rss",
        category="business",
        region="india",
        source_id="bs-rss",
    ),
    RSSSource(
        name="Moneycontrol India",
        url="https://www.moneycontrol.com/rss/latestnews.xml",
        category="business",
        region="india",
        source_id="moneycontrol-rss",
    ),
    RSSSource(
        name="Deccan Herald India",
        url="https://www.deccanherald.com/rss/india.xml",
        category="general",
        region="india",
        source_id="dh-rss",
    ),
    # Technology
    RSSSource(
        name="NDTV Tech",
        url="https://feeds.ndtv.com/ndtv/tech",
        category="technology",
        region="india",
        source_id="ndtv-tech-rss",
    ),
    RSSSource(
        name="The Verge",
        url="https://www.theverge.com/rss/index.xml",
        category="technology",
        region="global",
        source_id="verge-rss",
    ),
    RSSSource(
        name="TechCrunch",
        url="https://techcrunch.com/feed/",
        category="technology",
        region="global",
        source_id="tc-rss",
    ),
    RSSSource(
        name="Ars Technica",
        url="https://feeds.arstechnica.com/arstechnica/index",
        category="technology",
        region="us",
        source_id="ars-rss",
    ),
    RSSSource(
        name="Wired",
        url="https://www.wired.com/feed/rss",
        category="technology",
        region="us",
        source_id="wired-rss",
    ),
    RSSSource(
        name="Engadget",
        url="https://www.engadget.com/rss.xml",
        category="technology",
        region="us",
        source_id="engadget-rss",
    ),
    # Sports
    RSSSource(
        name="Times of India - Sports",
        url="https://timesofindia.indiatimes.com/rssfeeds/4719149.cms",
        category="sports",
        region="india",
        source_id="toi-sports-rss",
    ),
    RSSSource(
        name="NDTV Sports",
        url="https://feeds.ndtv.com/ndtv/sports",
        category="sports",
        region="india",
        source_id="ndtv-sports-rss",
    ),
    RSSSource(
        name="Cricbuzz Cricket",
        url="https://www.cricbuzz.com/feed/rss",
        category="sports",
        region="india",
        source_id="cricbuzz-rss",
    ),
    RSSSource(
        name="Sportskeeda",
        url="https://www.sportskeeda.com/feed",
        category="sports",
        region="india",
        source_id="sportskeeda-rss",
    ),
    RSSSource(
        name="ESPN Cricket",
        url="https://www.espncricinfo.com/feeds/cricket_rss_feeds/v2_2_2_feed.xml",
        category="sports",
        region="global",
        source_id="espn-cricket-rss",
    ),
    RSSSource(
        name="BBC Sport",
        url="http://feeds.bbci.co.uk/sport/rss.xml",
        category="sports",
        region="global",
        source_id="bbc-sport-global-rss",
    ),
    RSSSource(
        name="Reuters Sports",
        url="https://www.reuters.com/rssFeed/sportsNews",
        category="sports",
        region="global",
        source_id="reuters-sports-rss",
    ),
    RSSSource(
        name="ESPN Sports",
        url="https://www.espn.com/espn/rss/news",
        category="sports",
        region="us",
        source_id="espn-sports-rss",
    ),
    RSSSource(
        name="BBC Sport",
        url="http://feeds.bbci.co.uk/sport/rss.xml",
        category="sports",
        region="gb",
        source_id="bbc-sport-rss",
    ),
    RSSSource(
        name="Sky Sports",
        url="https://www.skysports.com/rss/12040",
        category="sports",
        region="gb",
        source_id="sky-sports-rss",
    ),
    RSSSource(
        name="Fox Sports",
        url="https://www.foxsports.com/rss/feed",
        category="sports",
        region="us",
        source_id="fox-sports-rss",
    ),
    # Health & Science
    RSSSource(
        name="The Hindu - Science",
        url="https://www.thehindu.com/sci-tech/feeder/default.rss",
        category="science",
        region="india",
        source_id="hindu-science-rss",
    ),
    RSSSource(
        name="Science Daily",
        url="https://www.sciencedaily.com/rss/top.xml",
        category="science",
        region="global",
        source_id="science-daily-rss",
    ),
    RSSSource(
        name="Nature News",
        url="https://www.nature.com/nature/rss/current.xml",
        category="science",
        region="global",
        source_id="nature-rss",
    ),
    RSSSource(
        name="Science Magazine",
        url="https://www.science.org/rss/news_current.xml",
        category="science",
        region="global",
        source_id="science-mag-rss",
    ),
    # Entertainment
    RSSSource(
        name="NDTV Entertainment",
        url="https://feeds.ndtv.com/ndtv/entertainment",
        category="entertainment",
        region="india",
        source_id="ndtv-ent-rss",
    ),
    RSSSource(
        name="Times of India - Entertainment",
        url="https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms",
        category="entertainment",
        region="india",
        source_id="toi-ent-rss",
    ),
    RSSSource(
        name="BBC Entertainment",
        url="https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        category="entertainment",
        region="global",
        source_id="bbc-ent-global-rss",
    ),
    RSSSource(
        name="Reuters Entertainment",
        url="https://www.reuters.com/rssFeed/lifestyle",
        category="entertainment",
        region="global",
        source_id="reuters-ent-rss",
    ),
    RSSSource(
        name="Bollywood Hungama",
        url="https://www.bollywoodhungama.com/feed/news/",
        category="entertainment",
        region="india",
        source_id="bollywood-rss",
    ),
    RSSSource(
        name="Times of India - Politics",
        url="https://timesofindia.indiatimes.com/rssfeeds/5450618.cms",
        category="politics",
        region="india",
        source_id="toi-politics-rss",
    ),
    RSSSource(
        name="BBC Politics",
        url="https://feeds.bbci.co.uk/news/politics/rss.xml",
        category="politics",
        region="global",
        source_id="bbc-politics-global-rss",
    ),
    RSSSource(
        name="Reuters Politics",
        url="https://www.reuters.com/rssFeed/politicsNews",
        category="politics",
        region="global",
        source_id="reuters-politics-rss",
    ),
    RSSSource(
        name="The Hindu - Politics",
        url="https://www.thehindu.com/news/national/?service=rss",
        category="politics",
        region="india",
        source_id="hindu-politics-rss",
    ),
    RSSSource(
        name="The Hindu - Business",
        url="https://www.thehindu.com/business/?service=rss",
        category="business",
        region="india",
        source_id="hindu-business-rss",
    ),
    RSSSource(
        name="Economic Times",
        url="https://economictimes.indiatimes.com/rssfeeds/default.cms",
        category="business",
        region="india",
        source_id="et-business-rss",
    ),
    RSSSource(
        name="Moneycontrol",
        url="https://www.moneycontrol.com/rss/latestnews.xml",
        category="finance",
        region="india",
        source_id="moneycontrol-rss",
    ),
    RSSSource(
        name="The Hindu - Science",
        url="https://www.thehindu.com/sci-tech/feeder/default.rss",
        category="technology",
        region="india",
        source_id="hindu-tech-rss",
    ),
    RSSSource(
        name="Gadgets360",
        url="https://gadgets.ndtv.com/rss/feed",
        category="technology",
        region="india",
        source_id="gadgets360-rss",
    ),
    RSSSource(
        name="The Hindu - Health",
        url="https://www.thehindu.com/sci-tech/health/?service=rss",
        category="health",
        region="india",
        source_id="hindu-health-rss",
    ),
    RSSSource(
        name="NDTV - Health",
        url="https://feeds.feedburner.com/ndtvhealth",
        category="health",
        region="india",
        source_id="ndtv-health-rss",
    ),
    RSSSource(
        name="BBC Entertainment",
        url="https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        category="entertainment",
        region="gb",
        source_id="bbc-ent-rss",
    ),
    RSSSource(
        name="Sky Entertainment",
        url="https://news.sky.com/feeds/rss/entertainment.xml",
        category="entertainment",
        region="gb",
        source_id="sky-ent-rss",
    ),
    RSSSource(
        name="Variety",
        url="https://variety.com/feed/",
        category="entertainment",
        region="us",
        source_id="variety-rss",
    ),
    RSSSource(
        name="Hollywood Reporter",
        url="https://www.hollywoodreporter.com/feed/",
        category="entertainment",
        region="us",
        source_id="hr-rss",
    ),
    RSSSource(
        name="Entertainment Weekly",
        url="https://ew.com/feed/",
        category="entertainment",
        region="us",
        source_id="ew-rss",
    ),
    RSSSource(
        name="Deadline",
        url="https://deadline.com/feed/",
        category="entertainment",
        region="us",
        source_id="deadline-rss",
    ),
    # Global News
    RSSSource(
        name="BBC News",
        url="http://feeds.bbc.co.uk/news/rss.xml",
        category="general",
        region="global",
        source_id="bbc-rss",
    ),
    RSSSource(
        name="Reuters Top News",
        url="https://www.reuters.com/newmedia/rss/newsrss.rss",
        category="general",
        region="global",
        source_id="reuters-rss",
    ),
    RSSSource(
        name="CNN News",
        url="http://feeds.cnn.com/rss/edition.rss",
        category="general",
        region="us",
        source_id="cnn-rss",
    ),
    RSSSource(
        name="Bloomberg",
        url="https://feeds.bloomberg.com/markets/news.rss",
        category="finance",
        region="us",
        source_id="bloomberg-rss",
    ),
    RSSSource(
        name="CNBC",
        url="https://www.cnbc.com/id/100003114/device/rss/rss.html",
        category="finance",
        region="us",
        source_id="cnbc-rss",
    ),
    RSSSource(
        name="Yahoo Finance",
        url="https://finance.yahoo.com/news/rssindex",
        category="finance",
        region="us",
        source_id="yahoo-finance-rss",
    ),
    RSSSource(
        name="The Guardian",
        url="https://www.theguardian.com/international/rss",
        category="general",
        region="global",
        source_id="guardian-rss",
    ),
    RSSSource(
        name="BBC UK",
        url="http://feeds.bbci.co.uk/news/uk/rss.xml",
        category="general",
        region="gb",
        source_id="bbc-uk-rss",
    ),
    RSSSource(
        name="Sky News",
        url="https://news.sky.com/feeds/rss/world.xml",
        category="general",
        region="gb",
        source_id="sky-news-rss",
    ),
    RSSSource(
        name="Al Jazeera",
        url="https://www.aljazeera.com/xml/rss/all.xml",
        category="general",
        region="global",
        source_id="aljazeera-rss",
    ),
    RSSSource(
        name="DW News",
        url="https://rss.dw.com/xml/rss-en-all",
        category="general",
        region="global",
        source_id="dw-rss",
    ),
]


class RSSFetcher:
    """Fetch and parse RSS feeds"""

    def __init__(self):
        self.session = None
        self.timeout = 10
        self.sources = {source.source_id: source for source in RSS_SOURCES}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_feed(
        self, source_id: str, limit: int = 10
    ) -> List[NewsArticle]:
        """
        Fetch articles from a specific RSS feed

        Args:
            source_id: RSS source identifier
            limit: Maximum articles to fetch

        Returns:
            List of NewsArticle objects
        """
        if source_id not in self.sources:
            logger.warning(f"Unknown RSS source: {source_id}")
            return []

        source = self.sources[source_id]

        try:
            # Parse RSS feed
            feed = feedparser.parse(source.url)

            if feed.bozo:
                logger.warning(f"RSS feed parsing error for {source.name}: {feed.bozo_exception}")

            articles = []
            for entry in feed.entries[:limit]:
                try:
                    article = self._parse_entry(entry, source)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"Error parsing RSS entry: {e}")
                    continue

            return articles

        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching RSS feed: {source.name}")
            return []
        except Exception as e:
            logger.error(f"Error fetching RSS feed {source.name}: {e}")
            return []

    async def fetch_all_sources(
        self,
        category: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 5,
    ) -> List[NewsArticle]:
        """
        Fetch from multiple RSS sources

        Args:
            category: Filter by category
            region: Filter by region
            limit: Articles per source

        Returns:
            Combined list of articles from all matching sources
        """
        # Filter sources by category and region
        filtered_sources = [
            source
            for source in RSS_SOURCES
            if (category is None or source.category == category)
            and (region is None or source.region == region)
        ]

        # Fetch from all sources concurrently
        tasks = [
            self.fetch_feed(source.source_id, limit) for source in filtered_sources
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results and remove duplicates
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Error in fetch task: {result}")

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

        return sorted_articles

    async def extract_content_from_link(
        self, url: str, source_id: str = "unknown"
    ) -> tuple[str, str]:
        """
        Extract article content from a URL
        Uses BeautifulSoup for parsing HTML content

        Args:
            url: Article URL
            source_id: Source identifier for content extraction rules

        Returns:
            Tuple of (title, content)
        """
        try:
            async with self.session.get(url, timeout=self.timeout) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to fetch content from {url}: {resp.status}")
                    return "", ""

                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")

                # Extract title
                title = ""
                title_tag = soup.find("h1") or soup.find("title")
                if title_tag:
                    title = title_tag.get_text(strip=True)

                # Extract main content
                content = self._extract_main_content(soup, source_id)

                return title, content

        except asyncio.TimeoutError:
            logger.warning(f"Timeout extracting content from {url}")
            return "", ""
        except Exception as e:
            logger.warning(f"Error extracting content from {url}: {e}")
            return "", ""

    def _parse_entry(self, entry, source: RSSSource) -> Optional[NewsArticle]:
        """
        Parse RSS entry to NewsArticle

        Args:
            entry: Parsed RSS entry
            source: RSS source configuration

        Returns:
            NewsArticle object or None
        """
        try:
            # Extract basic fields
            title = entry.get("title", "")
            url = entry.get("link", "")
            description = entry.get("summary", "")

            # Extract published date
            published_at = datetime.utcnow()  # Default to now
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            elif entry.get("published"):
                try:
                    published_at = datetime.fromisoformat(
                        entry["published"].replace("Z", "+00:00")
                    )
                except:
                    pass

            # Extract image - try multiple methods
            image_url = ""
            
            # Method 1: media_content
            if entry.get("media_content"):
                image_url = entry["media_content"][0].get("url", "")
            
            # Method 2: image href
            elif entry.get("image"):
                image_url = entry["image"].get("href", "")
            
            # Method 3: enclosures (common in RSS)
            elif entry.get("enclosures"):
                for enclosure in entry["enclosures"]:
                    if enclosure.get("type", "").startswith("image/"):
                        image_url = enclosure.get("href", "")
                        break
            
            # Method 4: extract from description/summary HTML
            if not image_url and description:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(description, "html.parser")
                img_tag = soup.find("img")
                if img_tag and img_tag.get("src"):
                    image_url = img_tag.get("src")
            
            # Method 5: try content field
            if not image_url and entry.get("content"):
                content = entry["content"][0] if isinstance(entry["content"], list) else entry["content"]
                if isinstance(content, dict) and content.get("value"):
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content["value"], "html.parser")
                    img_tag = soup.find("img")
                    if img_tag and img_tag.get("src"):
                        image_url = img_tag.get("src")

            # Extract author
            author = entry.get("author", "")

            if not title or not url:
                return None

            return NewsArticle(
                title=title,
                description=description,
                content=description,
                url=url,
                image_url=image_url,
                source_name=source.name,
                source_id=source.source_id,
                published_at=published_at,
                category=source.category,
                region=source.region,
                author=author,
            )

        except Exception as e:
            logger.warning(f"Error parsing RSS entry: {e}")
            return None

    def _extract_main_content(self, soup: BeautifulSoup, source_id: str) -> str:
        """
        Extract main article content using source-specific rules

        Args:
            soup: BeautifulSoup parser object
            source_id: Source ID for extraction rules

        Returns:
            Extracted content text
        """
        # Common content selectors
        content_selectors = [
            "article",
            "main",
            ".article-content",
            ".post-content",
            ".entry-content",
            ".content",
            "div[class*='content']",
            "div[class*='article']",
        ]

        # Source-specific selectors
        source_selectors = {
            "toi-rss": ["div.articlebodydesc"],
            "ndtv-rss": ["div.pText"],
            "hindu-rss": ["div.article-full-body"],
            "ie-rss": ["div.article_content"],
            "bbc-rss": ["article", "div#story-body"],
            "reuters-rss": ["article"],
        }

        # Try source-specific selectors first
        if source_id in source_selectors:
            for selector in source_selectors[source_id]:
                content = soup.select_one(selector)
                if content:
                    return content.get_text(separator="\n", strip=True)

        # Try common selectors
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                # Remove script and style tags
                for script in content(["script", "style"]):
                    script.decompose()
                return content.get_text(separator="\n", strip=True)

        # Fallback: get body text
        body = soup.find("body")
        if body:
            return body.get_text(separator="\n", strip=True)

        return ""
