"""
Sentiment analysis for news articles
Uses LLM to analyze sentiment of news content
"""

import logging
from typing import Optional
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SentimentAnalyzer:
    """Analyzes sentiment of news articles using LLM"""
    
    def __init__(self):
        self.llm_provider = settings.llm_provider
        self.openai_client = None
        self.anthropic_client = None
        
        if settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        if settings.anthropic_api_key:
            self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    async def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
        
        Returns:
            dict: Sentiment analysis results with score and label
        """
        if not text or len(text.strip()) < 50:
            return {
                "sentiment": "neutral",
                "score": 0.5,
                "confidence": 0.0
            }
        
        try:
            if self.llm_provider == "openai" and self.openai_client:
                return await self._analyze_with_openai(text)
            elif self.llm_provider == "anthropic" and self.anthropic_client:
                return await self._analyze_with_anthropic(text)
            else:
                return self._analyze_fallback(text)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return self._analyze_fallback(text)
    
    async def _analyze_with_openai(self, text: str) -> dict:
        """Analyze sentiment using OpenAI"""
        prompt = f"""Analyze the sentiment of this news article text. Respond with ONLY a JSON object in this exact format:
{{
    "sentiment": "positive" or "negative" or "neutral",
    "score": number between 0 and 1 (0 = very negative, 1 = very positive),
    "confidence": number between 0 and 1
}}

Text to analyze:
{text[:2000]}
"""
        
        response = await self.openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a sentiment analysis expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        import json
        result_text = response.choices[0].message.content.strip()
        return json.loads(result_text)
    
    async def _analyze_with_anthropic(self, text: str) -> dict:
        """Analyze sentiment using Anthropic"""
        prompt = f"""Analyze the sentiment of this news article text. Respond with ONLY a JSON object in this exact format:
{{
    "sentiment": "positive" or "negative" or "neutral",
    "score": number between 0 and 1 (0 = very negative, 1 = very positive),
    "confidence": number between 0 and 1
}}

Text to analyze:
{text[:2000]}
"""
        
        response = await self.anthropic_client.messages.create(
            model=settings.anthropic_model,
            max_tokens=100,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        import json
        result_text = response.content[0].text.strip()
        return json.loads(result_text)
    
    def _analyze_fallback(self, text: str) -> dict:
        """
        Simple rule-based sentiment analysis as fallback
        """
        positive_words = [
            'good', 'great', 'excellent', 'positive', 'success', 'growth',
            'increase', 'profit', 'win', 'benefit', 'improve', 'gain',
            'breakthrough', 'innovation', 'achievement', 'celebrate'
        ]
        
        negative_words = [
            'bad', 'terrible', 'negative', 'failure', 'loss', 'decrease',
            'decline', 'crisis', 'disaster', 'threat', 'risk', 'concern',
            'problem', 'issue', 'struggle', 'collapse', 'warning'
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count
        
        if total == 0:
            return {
                "sentiment": "neutral",
                "score": 0.5,
                "confidence": 0.3
            }
        
        score = positive_count / total
        
        if score > 0.6:
            sentiment = "positive"
        elif score < 0.4:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": min(0.5 + (total * 0.05), 0.8)
        }


# Global sentiment analyzer instance
sentiment_analyzer = SentimentAnalyzer()
