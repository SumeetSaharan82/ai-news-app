"""
LLM-based news summarization and analysis
Supports OpenAI GPT and Anthropic Claude
"""

import logging
import asyncio
from typing import List, Optional
from datetime import datetime

from backend.config.settings import get_settings
from backend.core.models import NewsArticle, SummarizedArticle
from backend.config.sources import SUMMARIZATION_CONFIG

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMProcessor:
    """Process and summarize news articles using LLMs"""

    def __init__(self):
        self.settings = get_settings()
        self.provider = self.settings.llm_provider
        self.initialize_client()

    def initialize_client(self):
        """Initialize LLM client based on provider"""
        if self.provider == "openai":
            try:
                import openai
                openai.api_key = self.settings.openai_api_key
                self.client = openai.AsyncOpenAI(
                    api_key=self.settings.openai_api_key
                )
                self.model = self.settings.openai_model
            except ImportError:
                logger.warning("OpenAI package not installed")
                self.client = None
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(
                    api_key=self.settings.anthropic_api_key
                )
                self.model = self.settings.anthropic_model
            except ImportError:
                logger.warning("Anthropic package not installed")
                self.client = None
        else:
            logger.error(f"Unknown LLM provider: {self.provider}")
            self.client = None

    async def summarize_article(self, article: NewsArticle) -> SummarizedArticle:
        """Summarize a single article using LLM"""
        if not self.client:
            # Fallback: use description if LLM unavailable
            return SummarizedArticle(
                title=article.title,
                summary=article.description or article.content[:150],
                original_article=article,
                summary_length=len(article.description or article.content[:150]),
                category=article.category,
                region=article.region,
                published_at=article.published_at,
            )

        try:
            prompt = self._build_summarization_prompt(article)
            summary = await self._call_llm(prompt)
            
            return SummarizedArticle(
                title=article.title,
                summary=summary,
                original_article=article,
                summary_length=len(summary),
                category=article.category,
                region=article.region,
                published_at=article.published_at,
            )
        except Exception as e:
            logger.error(f"Error summarizing article: {e}")
            # Fallback
            return SummarizedArticle(
                title=article.title,
                summary=article.description or article.content[:150],
                original_article=article,
                summary_length=len(article.description or article.content[:150]),
                category=article.category,
                region=article.region,
                published_at=article.published_at,
            )

    async def summarize_articles(
        self, articles: List[NewsArticle]
    ) -> List[SummarizedArticle]:
        """Summarize multiple articles concurrently"""
        tasks = [self.summarize_article(article) for article in articles]
        summaries = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        return [
            s for s in summaries 
            if isinstance(s, SummarizedArticle)
        ]

    async def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        if not self.client:
            return "neutral"

        try:
            prompt = f"""Analyze the sentiment of this text and respond with only one word: positive, negative, or neutral.

Text: {text}

Sentiment:"""
            sentiment = await self._call_llm(prompt)
            return sentiment.lower().strip()
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return "neutral"

    async def extract_key_points(self, article: NewsArticle) -> List[str]:
        """Extract key points from article"""
        if not self.client:
            return []

        try:
            text = f"{article.title}\n{article.description}\n{article.content}"
            prompt = f"""Extract 3-5 key points from this article text:

{text}

Key Points (as a numbered list):"""
            response = await self._call_llm(prompt)
            
            # Parse key points
            lines = response.strip().split("\n")
            key_points = [
                line.replace(f"{i}. ", "").strip()
                for i, line in enumerate(lines, 1)
                if line.strip()
            ]
            return key_points[:5]
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return []

    def _build_summarization_prompt(self, article: NewsArticle) -> str:
        """Build summarization prompt for LLM"""
        max_length = SUMMARIZATION_CONFIG.get("max_summary_length", 150)
        tone = SUMMARIZATION_CONFIG.get("tone", "concise and informative")
        
        content = article.content or article.description or ""
        
        return f"""Summarize the following news article in a {tone} manner. 
The summary should be approximately {max_length} characters and highlight the most important information.

Title: {article.title}

Content: {content}

Summary:"""

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM with prompt"""
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=500,
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == "anthropic":
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            raise

    async def batch_process(
        self,
        articles: List[NewsArticle],
        include_sentiment: bool = True,
        include_key_points: bool = True,
    ) -> List[SummarizedArticle]:
        """Process multiple articles with sentiment and key points"""
        summarized_articles = await self.summarize_articles(articles)
        
        if include_sentiment or include_key_points:
            for article in summarized_articles:
                if include_sentiment:
                    article.sentiment = await self.analyze_sentiment(
                        f"{article.title} {article.summary}"
                    )
                if include_key_points:
                    article.key_points = await self.extract_key_points(
                        article.original_article
                    )
        
        return summarized_articles
