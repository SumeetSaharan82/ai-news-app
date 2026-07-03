"""
Intelligent article content extraction from URLs
Removes boilerplate (ads, sidebars, footers, recommendations)
Keeps only the actual article content
"""

import logging
import asyncio
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class ExtractedContent:
    """Extracted article content"""
    title: str
    byline: str
    publication_date: Optional[datetime]
    body_text: str
    word_count: int
    source_url: str
    extracted_at: datetime
    confidence: float  # 0.0-1.0 based on extraction quality


class ContentExtractor:
    """
    Extract article content from URLs
    Removes ads, sidebars, recommended articles, footers
    Keeps only the main article text
    """

    # CSS selectors for common boilerplate elements (to remove)
    BOILERPLATE_SELECTORS = [
        # Ads
        "[class*='ad']",
        "[class*='advertisement']",
        "[id*='ad']",
        # Sidebars
        "aside",
        "[class*='sidebar']",
        "[class*='widget']",
        # Related/Recommended articles
        "[class*='related']",
        "[class*='recommended']",
        "[class*='trending']",
        # Navigation
        "nav",
        "[class*='breadcrumb']",
        # Comments
        "[class*='comment']",
        "[class*='discussion']",
        # Footer
        "footer",
        "[class*='footer']",
        # Social sharing
        "[class*='share']",
        "[class*='social']",
    ]

    # Source-specific selectors for main content
    SOURCE_SELECTORS = {
        "timesofindia.indiatimes.com": {
            "title": "h1.headline",
            "byline": "div.byline",
            "date": "span.date",
            "body": "div.article-content",
        },
        "thehindu.com": {
            "title": "h1.title",
            "byline": "div.author-name",
            "date": "span.publish-date",
            "body": "article",
        },
        "indianexpress.com": {
            "title": "h1",
            "byline": "span.author",
            "date": "span.publish-date",
            "body": "div.article-content",
        },
        "ndtv.com": {
            "title": "h1",
            "byline": "span.author-name",
            "date": "span.publish-date",
            "body": "div.article-body",
        },
        "bbc.com": {
            "title": "h1",
            "byline": "span[data-testid='byline']",
            "date": "time",
            "body": "article",
        },
        "reuters.com": {
            "title": "h1",
            "byline": "span.author",
            "date": "div.article-info-meta",
            "body": "article",
        },
        "theguardian.com": {
            "title": "h1",
            "byline": "a[data-link-name='byline']",
            "date": "time",
            "body": "article",
        },
    }

    # Generic fallback selectors
    GENERIC_SELECTORS = {
        "title": ["h1", "[class*='headline']", "[class*='title']"],
        "byline": ["[class*='byline']", "[class*='author']", "span.author"],
        "date": ["time", "[class*='date']", "[class*='publish']"],
        "body": [
            "article",
            "main",
            "[class*='article-content']",
            "[class*='post-content']",
            "[class*='entry-content']",
            "div[class*='content']",
        ],
    }

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def extract(self, url: str) -> Optional[ExtractedContent]:
        """
        Extract article content from URL

        Args:
            url: Article URL to extract from

        Returns:
            ExtractedContent object or None if extraction fails
        """
        try:
            # Fetch HTML
            async with self.session.get(url, timeout=self.timeout) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to fetch {url}: HTTP {resp.status}")
                    return None

                html = await resp.text()

            # Parse and extract
            soup = BeautifulSoup(html, "html.parser")

            # Get domain for source-specific selectors
            domain = urlparse(url).netloc.replace("www.", "")

            # Extract content
            title = self._extract_title(soup, domain)
            byline = self._extract_byline(soup, domain)
            pub_date = self._extract_publication_date(soup, domain)
            body_text = self._extract_body(soup, domain)

            if not body_text or len(body_text.strip()) < 100:
                logger.warning(f"Extracted content too short for {url}")
                return None

            word_count = len(body_text.split())
            confidence = self._calculate_confidence(title, body_text, word_count)

            return ExtractedContent(
                title=title or "[No title found]",
                byline=byline or "Unknown Author",
                publication_date=pub_date,
                body_text=body_text,
                word_count=word_count,
                source_url=url,
                extracted_at=datetime.utcnow(),
                confidence=confidence,
            )

        except asyncio.TimeoutError:
            logger.warning(f"Timeout extracting content from {url}")
            return None
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup, domain: str) -> str:
        """
        Extract article title using source-specific or generic selectors
        """
        # Try source-specific selectors
        if domain in self.SOURCE_SELECTORS:
            selector = self.SOURCE_SELECTORS[domain].get("title")
            if selector:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)

        # Try generic selectors
        for selector in self.GENERIC_SELECTORS["title"]:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if len(text) > 10:
                    return text

        # Last resort: og:title meta tag
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]

        return ""

    def _extract_byline(self, soup: BeautifulSoup, domain: str) -> str:
        """
        Extract author/byline information
        """
        if domain in self.SOURCE_SELECTORS:
            selector = self.SOURCE_SELECTORS[domain].get("byline")
            if selector:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)

        for selector in self.GENERIC_SELECTORS["byline"]:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and len(text) < 200:
                    return text

        return ""

    def _extract_publication_date(self, soup: BeautifulSoup, domain: str) -> Optional[datetime]:
        """
        Extract publication date
        """
        if domain in self.SOURCE_SELECTORS:
            selector = self.SOURCE_SELECTORS[domain].get("date")
            if selector:
                element = soup.select_one(selector)
                if element:
                    date_str = element.get("datetime") or element.get_text(strip=True)
                    try:
                        return self._parse_date(date_str)
                    except:
                        pass

        for selector in self.GENERIC_SELECTORS["date"]:
            element = soup.select_one(selector)
            if element:
                date_str = element.get("datetime") or element.get_text(strip=True)
                try:
                    return self._parse_date(date_str)
                except:
                    pass

        date_meta = soup.find("meta", property="article:published_time")
        if date_meta and date_meta.get("content"):
            try:
                return self._parse_date(date_meta["content"])
            except:
                pass

        return None

    def _extract_body(self, soup: BeautifulSoup, domain: str) -> str:
        """
        Extract main article body text
        Removes boilerplate elements
        """
        content_soup = soup

        for selector in self.BOILERPLATE_SELECTORS:
            for element in content_soup.select(selector):
                element.decompose()

        body_element = None
        if domain in self.SOURCE_SELECTORS:
            selector = self.SOURCE_SELECTORS[domain].get("body")
            if selector:
                body_element = content_soup.select_one(selector)

        if not body_element:
            for selector in self.GENERIC_SELECTORS["body"]:
                body_element = content_soup.select_one(selector)
                if body_element:
                    break

        if not body_element:
            body_element = content_soup.find("body")

        if not body_element:
            return ""

        text = body_element.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        text = "\n".join(lines)

        return text

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse various date string formats
        """
        from dateutil import parser as date_parser
        return date_parser.parse(date_str)

    def _calculate_confidence(self, title: str, body: str, word_count: int) -> float:
        """
        Calculate extraction confidence score (0.0-1.0)
        """
        confidence = 0.7

        if title and len(title) > 20:
            confidence += 0.15

        if word_count > 300:
            confidence += 0.15
        elif word_count > 100:
            confidence += 0.05

        if word_count < 100:
            confidence = max(0.3, confidence - 0.2)

        return min(1.0, confidence)
