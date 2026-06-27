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
    main_points: List[str]  # Factual bullet points only
    summary: str  # 60-word maximum summary
    key_entities: List[str]  # Person, company, location mentions
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

    # CRITICAL: System prompt to prevent opinions
    SYSTEM_PROMPT = """You are a NEWS EXTRACTION AND CONDENSING TOOL, NOT a journalist or analyst.

=== CORE RULES (NON-NEGOTIABLE) ===

1. EXTRACT ONLY: Report facts exactly as stated in source text
2. NO OPINIONS: Never add interpretations, analysis, or speculation
3. NO PREDICTIONS: Do not forecast or hypothesize outcomes
4. NO CONTEXT: Do not add information not explicitly in the article
5. NO HEDGING: Avoid "may", "could", "likely", "suggests", "appears"
6. NO EDITORIAL: No "this is important", "notably", "significant"

=== FORBIDDEN PHRASES ===
"This suggests that..."
"Experts believe..."
"It's likely that..."
"This could lead to..."
"Analysis shows..."
"It appears that..."
"According to sources..."
"Many observers..."
Any superlatives or subjective language

=== OUTPUT FORMAT (STRICT JSON) ===

Respond ONLY with valid JSON, no additional text:

{
  "title": "Exact headline from article",
  "main_points": [
    "Fact 1 stated in article",
    "Fact 2 stated in article",
    "Fact 3 stated in article",
    "Fact 4 stated in article",
    "Fact 5 stated in article"
  ],
  "summary": "60-word maximum factual summary stating who did what when where. Use simple declarative sentences. Quote direct statements. Do not interpret or analyze.",
  "key_entities": ["Person Name", "Company Name", "Location Name"],
  "extraction_confidence": 0.95,
  "notes": "Any data quality issues"
}

=== SUMMARY RULES ===
- Maximum 60 words
- Start with subject + verb
- Use past or present tense only
- When possible, quote direct statements from article
- Include date/location context at end
- NO future tense, NO opinions, NO predictions

=== MAIN_POINTS RULES ===
- Maximum 5 bullet points
- Each point one factual statement
- Use format: "[Subject] [verb] [object]"
- Quote directly when important nuance needed
- No speculation or interpretation

=== KEY_ENTITIES RULES ===
- Extract actual people names mentioned
- Extract company/organization names
- Extract location names (countries, cities, regions)
- Maximum 10 entities
- Use exact names from article
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

        Args:
            content: ExtractedContent from content_extractor

        Returns:
            ExtractedArticle with strictly validated data
        """
        if not self.client:
            logger.warning("LLM client not initialized, returning fallback")
            return self._create_fallback_extraction(content)

        try:
            # Build user prompt with article content
            user_prompt = f"""Extract and condense this article following STRICT rules:

=== ARTICLE CONTENT ===
Title: {content.title}
Byline: {content.byline}
Date: {content.publication_date}

{content.body_text}

=== END ARTICLE ===

Respond with ONLY valid JSON."""

            # Call LLM with strict system prompt
            llm_response = await self._call_llm_strict(
                user_prompt=user_prompt
            )

            if not llm_response:
                return self._create_fallback_extraction(content)

            # Parse JSON response
            try:
                extracted_data = json.loads(llm_response)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from LLM, using fallback")
                return self._create_fallback_extraction(content)

            # Validate and create ExtractedArticle
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

    async def _call_llm_strict(
        self, user_prompt: str, temperature: float = 0.3
    ) -> Optional[str]:
        """
        Call LLM with strict parameters for factual extraction
        Lower temperature = more deterministic output

        Args:
            user_prompt: The article text to process
            temperature: LLM temperature (0.3 = very strict, deterministic)

        Returns:
            JSON string or None
        """
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,  # Lower = more deterministic
                    max_tokens=800,
                    response_format={"type": "json_object"},  # Force JSON
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
        Create fallback extraction when LLM unavailable
        Uses simple heuristics instead of LLM
        """
        # Extract first 5 sentences as main points
        sentences = content.body_text.split(".")[:5]
        main_points = [s.strip() + "." for s in sentences if s.strip()]

        # Create 60-word summary from first 2 sentences
        summary = " ".join(main_points[:2])
        summary = self._enforce_word_limit(summary, max_words=60)

        # Extract entities (simple version)
        key_entities = []
        import re

        # Find capitalized sequences (likely names)
        words = content.body_text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and word not in key_entities and len(word) > 3:
                key_entities.append(word)
                if len(key_entities) >= 10:
                    break

        return ExtractedArticle(
            title=content.title,
            main_points=main_points[:5],
            summary=summary,
            key_entities=key_entities[:10],
            source_url=content.source_url,
            publication_date=content.publication_date.isoformat()
            if content.publication_date
            else None,
            word_count=content.word_count,
            extracted_at=content.extracted_at.isoformat(),
            extraction_confidence=content.confidence,
            llm_processing_confidence=0.5,  # Lower confidence for fallback
        )

    def _enforce_word_limit(self, text: str, max_words: int = 60) -> str:
        """
        Enforce maximum word count by truncating at word boundary
        """
        words = text.split()
        if len(words) <= max_words:
            return text

        truncated = " ".join(words[:max_words])
        # Ensure ends with punctuation
        if not truncated.endswith((".", "!", "?")):
            truncated += "."
        return truncated

    def to_dict(self, article: ExtractedArticle) -> Dict:
        """
        Convert ExtractedArticle to dictionary
        """
        return asdict(article)

    def to_json(self, article: ExtractedArticle) -> str:
        """
        Convert ExtractedArticle to JSON string
        """
        return json.dumps(self.to_dict(article), indent=2)
