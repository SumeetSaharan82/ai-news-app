"""
Strict LLM processor for RSS-sourced content
Operates purely as extractor and condenser
Prevents LLM from adding opinions or interpretations
Outputs deterministic JSON format
"""

import logging
import json
from typing import Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass, asdict

from backend.config.settings import get_settings
from backend.core.content_extractor import ExtractedContent

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ExtractedArticle:
    """Strictly extracted article data"""
    title: str
    main_points: List[str]
    summary: str
    key_entities: List[str]
    source_url: str
    publication_date: Optional[str]
    word_count: int
    extracted_at: str
    extraction_confidence: float
    llm_processing_confidence: float


class StrictRSSLLMProcessor:
    """
    Process RSS-sourced articles with strict prompts
    Ensures LLM acts as extractor, not opinion generator
    """

    SYSTEM_PROMPT = """You are a NEWS EXTRACTION AND CONDENSING TOOL, NOT a journalist or analyst.

=== CORE RULES (NON-NEGOTIABLE) ===

1. EXTRACT ONLY: Report facts exactly as stated in source text
2. NO OPINIONS: Never add interpretations, analysis, or speculation
3. NO PREDICTIONS: Do not forecast or hypothesize outcomes
4. NO CONTEXT: Do not add information not explicitly in the article
5. NO HEDGING: Avoid "may", "could", "likely", "suggests", "appears"
6. NO EDITORIAL: No "this is important", "notably", "significant"

=== OUTPUT FORMAT (STRICT JSON) ===

{
  "title": "Exact headline from article",
  "main_points": ["Fact 1", "Fact 2", "Fact 3"],
  "summary": "60-word maximum factual summary",
  "key_entities": ["Person", "Company", "Location"],
  "extraction_confidence": 0.95
}
"""

    def __init__(self):
        self.settings = get_settings()
        self.provider = self.settings.llm_provider
        self.initialize_client()

    def initialize_client(self):
        """Initialize LLM client based on provider"""
        if self.provider == "openai":
            try:
                import openai
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

    async def process_extracted_content(
        self, content: ExtractedContent
    ) -> Optional[ExtractedArticle]:
        """
        Process extracted article content with strict LLM
        """
        if not self.client:
            logger.warning("LLM client not initialized, returning fallback")
            return self._create_fallback_extraction(content)

        try:
            user_prompt = f"""Extract and condense this article following STRICT rules:

Title: {content.title}
Byline: {content.byline}

{content.body_text}

Respond with ONLY valid JSON."""

            llm_response = await self._call_llm_strict(user_prompt=user_prompt)

            if not llm_response:
                return self._create_fallback_extraction(content)

            try:
                extracted_data = json.loads(llm_response)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from LLM, using fallback")
                return self._create_fallback_extraction(content)

            return ExtractedArticle(
                title=extracted_data.get("title", content.title),
                main_points=extracted_data.get("main_points", [])[:5],
                summary=self._enforce_word_limit(
                    extracted_data.get("summary", ""), max_words=60
                ),
                key_entities=extracted_data.get("key_entities", [])[:10],
                source_url=content.source_url,
                publication_date=content.publication_date.isoformat()
                if content.publication_date
                else None,
                word_count=content.word_count,
                extracted_at=content.extracted_at.isoformat(),
                extraction_confidence=content.confidence,
                llm_processing_confidence=extracted_data.get(
                    "extraction_confidence", 0.85
                ),
            )

        except Exception as e:
            logger.error(f"Error processing with strict LLM: {e}")
            return self._create_fallback_extraction(content)

    async def _call_llm_strict(self, user_prompt: str, temperature: float = 0.3) -> Optional[str]:
        """
        Call LLM with strict parameters
        """
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                    max_tokens=800,
                )
                return response.choices[0].message.content.strip()

            elif self.provider == "anthropic":
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=800,
                    temperature=temperature,
                    system=self.SYSTEM_PROMPT,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ],
                )
                return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Error calling strict LLM: {e}")
            return None

    def _create_fallback_extraction(self, content: ExtractedContent) -> ExtractedArticle:
        """
        Fallback extraction when LLM unavailable
        """
        sentences = content.body_text.split(".")[:5]
        main_points = [s.strip() + "." for s in sentences if s.strip()]
        summary = " ".join(main_points[:2])
        summary = self._enforce_word_limit(summary, max_words=60)

        return ExtractedArticle(
            title=content.title,
            main_points=main_points[:5],
            summary=summary,
            key_entities=[],
            source_url=content.source_url,
            publication_date=content.publication_date.isoformat()
            if content.publication_date
            else None,
            word_count=content.word_count,
            extracted_at=content.extracted_at.isoformat(),
            extraction_confidence=content.confidence,
            llm_processing_confidence=0.5,
        )

    def _enforce_word_limit(self, text: str, max_words: int = 60) -> str:
        """
        Enforce maximum word count
        """
        words = text.split()
        if len(words) <= max_words:
            return text

        truncated = " ".join(words[:max_words])
        if not truncated.endswith((".", "!", "?")):
            truncated += "."
        return truncated
