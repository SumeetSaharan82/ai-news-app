# AI News App - Development Setup Guide

## 🎯 Complete Setup Instructions

### Part 1: System Prerequisites

#### Option A: Using Docker (Recommended)
```bash
# Install Docker
# Visit: https://docs.docker.com/get-docker/

# Verify installation
docker --version
docker-compose --version
```

#### Option B: Manual Installation

**macOS**:
```bash
# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install Redis
brew install redis
brew services start redis

# Install Python
brew install python@3.11
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip python3-venv
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y redis-server

sudo systemctl start postgresql
sudo systemctl start redis-server
```

**Windows**:
- Python: https://www.python.org/downloads/
- PostgreSQL: https://www.postgresql.org/download/windows/
- Redis: https://github.com/microsoftarchive/redis/releases

### Part 2: Project Setup

```bash
# 1. Clone repository
git clone https://github.com/SumeetSaharan82/ai-news-app.git
cd ai-news-app

# 2. Create virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env

# 5. Edit .env with your API keys (see Part 3)
```

### Part 3: API Keys Setup

#### NewsAPI.org
1. Visit https://newsapi.org/register
2. Sign up (free tier: 100 requests/day)
3. Copy API key from dashboard
4. Add to `.env`: `NEWSAPI_KEY=your_key`

#### New York Times API
1. Visit https://developer.nytimes.com/accounts/create
2. Register developer account
3. Create app and request "Top Stories API" access
4. Copy API key
5. Add to `.env`: `NYT_API_KEY=your_key`

#### The Guardian API
1. Visit https://open-platform.theguardian.com/register/developer
2. Create account and register app
3. Get API key from email
4. Add to `.env`: `GUARDIAN_API_KEY=your_key`

#### OpenAI API (Recommended)
1. Visit https://platform.openai.com/signup
2. Create account
3. Go to https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Add to `.env`:
```
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4-turbo-preview
LLM_PROVIDER=openai
```
6. Add payment method ($5+ credit for testing)

#### OR Anthropic Claude
1. Visit https://console.anthropic.com
2. Create account
3. Go to API keys section
4. Create new API key
5. Add to `.env`:
```
ANTHROPIC_API_KEY=your_key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
LLM_PROVIDER=anthropic
```

#### Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres psql

CREATE DATABASE ai_news_app;
CREATE USER newsapp WITH PASSWORD 'secure_password';
ALTER ROLE newsapp SET client_encoding TO 'utf8';
ALTER ROLE newsapp SET default_transaction_isolation TO 'read committed';
ALTER ROLE newsapp SET default_transaction_deferrable TO on;
ALTER ROLE newsapp SET default_transaction_read_only TO off;
GRANT ALL PRIVILEGES ON DATABASE ai_news_app TO newsapp;
\q
```

Update `.env`:
```
DATABASE_URL=postgresql://newsapp:secure_password@localhost:5432/ai_news_app
```

### Part 4: Running the Application

```bash
# Terminal 1: Make sure Redis is running
redis-server

# Terminal 2: Start FastAPI server
python -m backend.main

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application started successfully
```

### Part 5: Testing

```bash
# Open in browser or use curl
curl http://localhost:8000/api/v1/health

# Should return:
# {"status":"healthy","app_name":"AI News App","version":"0.1.0","timestamp":"..."}

# Get top 5 technology news
curl "http://localhost:8000/api/v1/news?category=technology&region=global&limit=5"

# Access Swagger UI
# Visit: http://localhost:8000/docs
```

## 🐳 Docker Deployment (Optional)

```bash
# Build Docker image
docker build -t ai-news-app .

# Run with docker-compose
docker-compose up

# Or run standalone
docker run -p 8000:8000 --env-file .env ai-news-app
```

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'backend'"
**Solution**: Make sure you're in the project root directory and virtual environment is activated
```bash
cd ai-news-app
source venv/bin/activate
```

### Issue: "NEWSAPI_KEY not configured"
**Solution**: Check your `.env` file has all required keys
```bash
cat .env | grep API_KEY
```

### Issue: "PostgreSQL connection refused"
**Solution**: Ensure PostgreSQL is running
```bash
# macOS
brew services start postgresql@15

# Ubuntu
sudo systemctl start postgresql
```

### Issue: "Redis connection refused"
**Solution**: Start Redis server
```bash
# macOS
brew services start redis

# Ubuntu
sudo systemctl start redis-server

# Or run directly
redis-server
```

## 📈 Performance Monitoring

```bash
# Monitor API response times
watch -n 1 'curl -s http://localhost:8000/api/v1/health'

# Check Redis cache hit rate
redis-cli info stats

# Monitor database connections
sudo -u postgres psql -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

## 🚀 Production Checklist

- [ ] All environment variables configured
- [ ] Database backups configured
- [ ] Redis persistence enabled
- [ ] Rate limiting implemented
- [ ] Error logging setup
- [ ] Health checks working
- [ ] API documentation complete
- [ ] Tests passing
- [ ] Security headers added
- [ ] HTTPS configured

## 📚 Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install new package
pip install package_name
# Update requirements.txt
pip freeze > requirements.txt

# Run tests
pytest

# Format code
black backend/

# Lint code
flake8 backend/

# Check for security issues
bandit -r backend/
```
