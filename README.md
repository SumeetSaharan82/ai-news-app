# AI News App

An AI-powered news aggregation and analysis platform that fetches news from multiple sources (APIs and RSS feeds), extracts content, and processes it with LLMs to provide clean, factual summaries without opinions.

## 🚀 Features

### Phase 1 (Current)
- **Multi-Source News Aggregation**
  - NewsAPI integration for global news coverage
  - RSS feed support for 15+ sources across multiple regions
  - Category-based filtering (technology, business, sports, health, science, entertainment)
  - Region-based filtering (global, India, US, UK, Canada, Australia, Germany)

- **Content Extraction**
  - Automated article content extraction from source URLs
  - Confidence scoring for extraction quality
  - Fallback mechanisms for failed extractions

- **AI-Powered Processing**
  - LLM integration (OpenAI GPT-4 and Anthropic Claude)
  - Strict factual summarization (no opinions or bias)
  - Key entity extraction
  - Main point summarization
  - Configurable LLM provider switching

- **API Endpoints**
  - Health check endpoint
  - Categories and regions listing
  - RSS sources management
  - News fetching from APIs
  - News fetching from RSS feeds
  - Search functionality
  - Interactive Swagger UI documentation

- **Data Management**
  - SQLite database (default) with PostgreSQL support
  - Article storage and retrieval
  - Caching with Redis support
  - Configurable cache TTL

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI 0.139.0
- **Server**: Uvicorn 0.49.0
- **Data Validation**: Pydantic 2.13.4
- **Database**: SQLAlchemy 2.0.23
- **HTTP Client**: aiohttp 3.14.1, httpx2
- **Content Parsing**: BeautifulSoup4 4.15.0, feedparser 6.0.12

### AI/ML
- **OpenAI**: GPT-4 Turbo
- **Anthropic**: Claude 3 Sonnet
- **NewsAPI**: News aggregation service

### Testing
- **Framework**: pytest 9.1.1
- **Async Testing**: pytest-asyncio 1.4.0
- **Coverage**: pytest-cov 7.1.0

### Development
- **Code Formatting**: black 23.12.0
- **Linting**: flake8 6.1.0

## 📋 Prerequisites

- Python 3.14+
- pip3 (or pip)
- API keys (optional for full functionality):
  - NewsAPI Key
  - OpenAI API Key (or Anthropic API Key)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-news-app
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Set Up Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# App Configuration
APP_NAME=AI News App
APP_VERSION=0.1.0
DEBUG=False
LOG_LEVEL=INFO

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# API Keys (optional but recommended)
NEWSAPI_KEY=your_newsapi_key_here
NYT_API_KEY=your_nyt_api_key_here
GUARDIAN_API_KEY=your_guardian_api_key_here

# LLM Configuration
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4-turbo-preview
ANTHROPIC_API_KEY=your_anthropic_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
LLM_PROVIDER=openai

# Database Configuration
DATABASE_URL=sqlite:///./news_app.db
SQLALCHEMY_ECHO=False

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=True

# Cache Settings
CACHE_TTL=3600
NEWS_FETCH_INTERVAL=1800
```

## 🚀 Running the Application

### Start the Server
```bash
python3 -m backend.main
```

Or using uvicorn directly:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: http://localhost:8000

### Access API Documentation
Visit http://localhost:8000/docs for interactive Swagger UI documentation

## 📡 API Endpoints

### Health Check
```bash
GET /api/v1/health
```

### Categories
```bash
GET /api/v1/categories
```

### Regions
```bash
GET /api/v1/regions
```

### RSS Sources
```bash
GET /api/v1/news/rss/sources
GET /api/v1/news/rss/sources?region=india
GET /api/v1/news/rss/sources?category=technology
```

### Fetch News from APIs
```bash
GET /api/v1/news/api?category=technology&region=india&limit=5
```

### Fetch News from RSS
```bash
GET /api/v1/news/rss?category=technology&region=india&limit=5
```

### Search News
```bash
GET /api/v1/search?query=AI%20startup&limit=5&days=7
```

## 🧪 Testing

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

For detailed testing instructions, see [TESTING.md](TESTING.md)

## 📁 Project Structure

```
ai-news-app/
├── backend/
│   ├── api/
│   │   └── v1/
│   │       ├── health.py
│   │       ├── categories.py
│   │       └── news.py
│   ├── config/
│   │   └── settings.py
│   ├── core/
│   │   ├── models.py
│   │   ├── rss_fetcher.py
│   │   ├── content_extractor.py
│   │   └── llm_strict_processor.py
│   └── main.py
├── tests/
│   ├── test_core.py
│   └── test_api.py
├── requirements.txt
├── .env.example
├── README.md
└── TESTING.md
```

## 🔐 Configuration

### Database
- **Default**: SQLite (`sqlite:///./news_app.db`)
- **Production**: PostgreSQL (configure via `DATABASE_URL`)

### Caching
- **Default**: In-memory
- **Production**: Redis (configure via `REDIS_URL`)

### LLM Provider
- **Options**: OpenAI or Anthropic
- **Default**: OpenAI
- **Switch via**: `LLM_PROVIDER` environment variable

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'backend'"
**Solution**: Ensure you're in the project root directory and dependencies are installed.

### Issue: "API keys not configured"
**Solution**: Add your API keys to the `.env` file. Some features may work without keys but with limited functionality.

### Issue: "Connection refused" on localhost:8000
**Solution**: Start the server with `python3 -m backend.main`

### Issue: Tests fail with deprecation warnings
**Solution**: These are warnings about deprecated Python/Pydantic features. The code still works but should be updated in future versions.

## 📝 Development Roadmap

### Phase 1 (Current) ✅
- [x] Basic FastAPI setup
- [x] NewsAPI integration
- [x] RSS feed support
- [x] Content extraction
- [x] LLM processing (OpenAI/Anthropic)
- [x] SQLite database
- [x] Basic API endpoints
- [x] Testing framework

### Phase 2 (Planned)
- [ ] User authentication
- [ ] Personalized news feeds
- [ ] Email notifications
- [ ] Advanced search filters
- [ ] News trend analysis
- [ ] Sentiment analysis
- [ ] Mobile app API

### Phase 3 (Future)
- [ ] Machine learning recommendations
- [ ] Real-time news alerts
- [ ] Social media integration
- [ ] Multi-language support
- [ ] Admin dashboard

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support, please open an issue in the repository or contact the maintainers.

---

Built with ❤️ using FastAPI, Python, and AI
