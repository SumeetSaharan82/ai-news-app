"""
News source configurations for different regions and categories
"""

# Global news sources configuration
GLOBAL_NEWS_SOURCES = {
    "reuters": {
        "name": "Reuters",
        "api": "newsapi",
        "country": "global",
        "language": "en",
        "api_key_env": "NEWSAPI_KEY",
        "priority": 1,
    },
    "bbc_news": {
        "name": "BBC News",
        "api": "newsapi",
        "country": "global",
        "language": "en",
        "api_key_env": "NEWSAPI_KEY",
        "priority": 2,
    },
    "times_of_india": {
        "name": "Times of India",
        "api": "newsapi",
        "country": "in",
        "language": "en",
        "api_key_env": "NEWSAPI_KEY",
        "priority": 1,
        "source_id": "times-of-india",
    },
    "indian_express": {
        "name": "Indian Express",
        "api": "newsapi",
        "country": "in",
        "language": "en",
        "api_key_env": "NEWSAPI_KEY",
        "priority": 2,
        "source_id": "indian-express-in",
    },
    "the_hindu": {
        "name": "The Hindu",
        "api": "newsapi",
        "country": "in",
        "language": "en",
        "api_key_env": "NEWSAPI_KEY",
        "priority": 2,
        "source_id": "the-hindu",
    },
    "business_today": {
        "name": "Business Today India",
        "api": "newsapi",
        "country": "in",
        "language": "en",
        "api_key_env": "NEWSAPI_KEY",
        "priority": 3,
        "source_id": "business-today-in",
    },
    "nyt": {
        "name": "New York Times",
        "api": "nyt",
        "country": "us",
        "language": "en",
        "api_key_env": "NYT_API_KEY",
        "priority": 1,
    },
    "cnn": {
        "name": "CNN",
        "api": "newsapi",
        "country": "us",
        "language": "en",
        "api_key_env": "NEWSAPI_KEY",
        "priority": 2,
        "source_id": "cnn",
    },
    "guardian": {
        "name": "The Guardian",
        "api": "guardian",
        "country": "uk",
        "language": "en",
        "api_key_env": "GUARDIAN_API_KEY",
        "priority": 2,
    },
    "bbc_uk": {
        "name": "BBC UK",
        "api": "newsapi",
        "country": "uk",
        "language": "en",
        "api_key_env": "NEWSAPI_KEY",
        "priority": 1,
        "source_id": "bbc-news",
    },
}

# Supported news categories
NEWS_CATEGORIES = {
    "business": {
        "label": "Business & Finance",
        "icon": "📊",
    },
    "technology": {
        "label": "Technology",
        "icon": "💻",
    },
    "sports": {
        "label": "Sports",
        "icon": "⚽",
    },
    "health": {
        "label": "Health & Science",
        "icon": "🏥",
    },
    "entertainment": {
        "label": "Entertainment",
        "icon": "🎬",
    },
    "science": {
        "label": "Science",
        "icon": "🔬",
    },
    "general": {
        "label": "General News",
        "icon": "📰",
    },
}

# Supported regions
REGIONS = {
    "global": {
        "label": "Global",
        "sources": ["reuters", "bbc_news"],
        "priority": 1,
    },
    "india": {
        "label": "India",
        "country_code": "in",
        "sources": ["times_of_india", "indian_express", "the_hindu", "business_today"],
        "priority": 1,
    },
    "us": {
        "label": "United States",
        "country_code": "us",
        "sources": ["nyt", "cnn"],
        "priority": 2,
    },
    "uk": {
        "label": "United Kingdom",
        "country_code": "gb",
        "sources": ["bbc_uk", "guardian"],
        "priority": 2,
    },
}

# LLM Summarization preferences
SUMMARIZATION_CONFIG = {
    "max_summary_length": 150,  # characters
    "max_headline_length": 100,
    "tone": "concise and informative",
    "language": "en",
    "include_sentiment": True,
}

# API rate limiting
RATE_LIMITS = {
    "newsapi": {
        "requests_per_day": 100,
        "requests_per_minute": 5,
    },
    "nyt": {
        "requests_per_day": 4000,
        "requests_per_second": 0.5,
    },
    "guardian": {
        "requests_per_second": 1,
    },
}

# Cache configuration
CACHE_CONFIG = {
    "news_ttl": 3600,  # 1 hour
    "summary_ttl": 7200,  # 2 hours
    "category_ttl": 1800,  # 30 minutes
}
