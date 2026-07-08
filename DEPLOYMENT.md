# Production Deployment Guide

This guide explains how to deploy the AI News App to production using **Vercel** (frontend) and **Railway** (backend) free tiers, suitable for 10-20 users.

## Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐
│   Vercel        │         │   Railway       │
│   (Frontend)    │◄────────┤   (Backend)     │
│   Free Tier     │  HTTPS  │   Free Tier     │
└─────────────────┘         └─────────────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │   Railway       │
                             │   PostgreSQL    │
                             │   (Database)    │
                             └─────────────────┘
```

## Prerequisites

- GitHub account
- Vercel account (free)
- Railway account (free)
- Git installed locally

## Step 1: Prepare Your Repository

### 1.1 Initialize Git (if not already done)

```bash
cd /Users/sumeetsaharan/ai-news-app/ai-news-app
git init
git add .
git commit -m "Initial commit - Phase 2 complete with frontend"
```

### 1.2 Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it `ai-news-app`
3. Don't initialize with README (we already have one)
4. Copy the repository URL

### 1.3 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-news-app.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy Backend to Railway

### 2.1 Create Railway Account

1. Go to [Railway](https://railway.app)
2. Sign up with GitHub
3. Verify your email

### 2.2 Deploy from GitHub

1. Click "New Project" → "Deploy from GitHub repo"
2. Select your `ai-news-app` repository
3. Railway will automatically detect the Python project
4. Click "Deploy"

### 2.3 Configure Environment Variables

1. Go to your Railway project
2. Click on your service
3. Go to "Variables" tab
4. Add these variables:

```env
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=your-secure-random-string-here
CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
SQLALCHEMY_POOL_SIZE=5
SQLALCHEMY_MAX_OVERFLOW=10
```

### 2.4 Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` environment variable
4. Note the database URL (it will be auto-configured)

### 2.5 Add Redis (Optional for Caching)

1. In your Railway project, click "New Service"
2. Select "Database" → "Redis"
3. Railway will automatically set `REDIS_URL` environment variable

### 2.6 Get Your Backend URL

1. Go to your Railway service
2. Copy the domain (e.g., `https://your-app.railway.app`)
3. Save this URL - you'll need it for the frontend

### 2.7 Test Backend Deployment

```bash
curl https://your-app.railway.app/api/v1/health
```

You should see:
```json
{
  "status": "healthy",
  "app_name": "AI News App",
  "version": "0.2.0"
}
```

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account

1. Go to [Vercel](https://vercel.com)
2. Sign up with GitHub
3. Verify your email

### 3.2 Deploy Frontend

1. Click "Add New Project"
2. Select your `ai-news-app` repository
3. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
4. Click "Deploy"

### 3.3 Update Frontend API URL

1. Go to your Vercel project
2. Go to "Settings" → "Environment Variables"
3. Add variable:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-railway-app.railway.app`

**Note:** The frontend code is already configured to use this environment variable. No code changes needed.

### 3.4 Redeploy Frontend

1. Go to your Vercel project
2. Click "Deployments"
3. Click the three dots → "Redeploy"

### 3.5 Get Your Frontend URL

1. Go to your Vercel project
2. Copy the domain (e.g., `https://your-app.vercel.app`)
3. This is your production URL!

## Step 4: Update CORS Configuration

### 4.1 Update Railway Environment Variables

1. Go to your Railway project
2. Go to "Variables" tab
3. Update `CORS_ORIGINS`:

```env
CORS_ORIGINS=["https://your-app.vercel.app"]
```

### 4.2 Redeploy Backend

1. Go to your Railway service
2. Click "Redeploy"

## Step 5: Test Production Deployment

### 5.1 Test Frontend

1. Open your Vercel URL in browser
2. Test category selection
3. Test news loading
4. Test user registration/login

### 5.2 Test Backend API

```bash
# Health check
curl https://your-app.railway.app/api/v1/health

# Get categories
curl https://your-app.railway.app/api/v1/categories

# Get news
curl https://your-app.railway.app/api/v1/news?category=technology
```

## Step 6: Monitor and Scale

### Railway Free Tier Limits

- **CPU**: 512 MB RAM
- **Storage**: 1 GB
- **Bandwidth**: 100 GB/month
- **Build Time**: 500 minutes/month

### Vercel Free Tier Limits

- **Bandwidth**: 100 GB/month
- **Build Time**: 6,000 minutes/month
- **Serverless Functions**: Unlimited
- **Edge Network**: Global

### For 10-20 Users

The free tiers are sufficient for:
- 10-20 concurrent users
- ~1,000-2,000 page views per day
- ~10-20 API requests per minute

### Monitoring

1. **Railway**: Built-in metrics and logs
2. **Vercel**: Analytics and deployment logs
3. **Database**: Monitor PostgreSQL usage in Railway

## Step 7: Optional Enhancements

### 7.1 Add Custom Domain

**Vercel:**
1. Go to "Settings" → "Domains"
2. Add your custom domain
3. Update DNS records

**Railway:**
1. Go to "Settings" → "Domains"
2. Add your custom domain
3. Update DNS records

### 7.2 Enable Email Notifications

Add these to Railway environment variables:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_USE_TLS=true
```

### 7.3 Enable LLM Features

Add these to Railway environment variables:

```env
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4-turbo-preview
LLM_PROVIDER=openai
```

## Troubleshooting

### Backend Not Starting

- Check Railway logs for errors
- Verify environment variables are set
- Ensure DATABASE_URL is correctly configured

### Frontend Can't Connect to Backend

- Verify CORS_ORIGINS includes your Vercel domain
- Check backend is running and accessible
- Verify API_BASE_URL in frontend is correct

### Database Connection Issues

- Ensure PostgreSQL service is running in Railway
- Check DATABASE_URL environment variable
- Verify database credentials

### Build Failures

- Check requirements.txt has correct versions
- Verify Python version compatibility
- Check Railway build logs for specific errors

## Security Checklist

- [ ] Change SECRET_KEY to a secure random string
- [ ] Enable HTTPS (automatic on Vercel/Railway)
- [ ] Set DEBUG=False in production
- [ ] Hide API docs in production (already configured)
- [ ] Use environment variables for sensitive data
- [ ] Enable CORS only for your domain
- [ ] Regularly update dependencies

## Cost Summary

**Free Tier Costs: $0/month**

- Vercel: Free (sufficient for 10-20 users)
- Railway: Free (sufficient for 10-20 users)
- PostgreSQL: Free (included in Railway)
- Redis: Free (included in Railway)

**Estimated Costs for Scaling:**

If you exceed free tiers:
- Railway: $5-20/month (Standard tier)
- Vercel: $20/month (Pro tier)
- Total: $25-40/month

## Backup Strategy

Railway automatically backs up PostgreSQL databases. To manually backup:

```bash
# From Railway dashboard, go to PostgreSQL service
# Click "Backup" to create manual backups
```

## Performance Optimization

The app is already optimized for production:
- Database connection pooling (5 connections, 10 overflow)
- API response caching
- Efficient database queries
- Frontend static asset optimization
- CDN delivery via Vercel

## Next Steps

1. Deploy using this guide
2. Test with 10-20 users
3. Monitor usage metrics
4. Gather user feedback
5. Plan Phase 3 features based on feedback

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **GitHub Issues**: Report issues in your repository

## Rollback Procedure

If something goes wrong:

**Vercel:**
1. Go to "Deployments"
2. Click on a previous successful deployment
3. Click "Promote to Production"

**Railway:**
1. Go to "Deployments"
2. Click on a previous successful deployment
3. Click "Redeploy"

## Maintenance

**Weekly:**
- Check usage metrics
- Review logs for errors
- Monitor database size

**Monthly:**
- Update dependencies
- Review security advisories
- Test backup restoration

**Quarterly:**
- Performance audit
- Security audit
- Cost optimization review
