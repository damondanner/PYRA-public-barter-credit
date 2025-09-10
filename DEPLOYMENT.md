# PYRA's Barter Credit API - Deployment Guide

This guide covers multiple deployment options for PYRA's Barter Credit API, from simple static hosting to full API servers.

## Quick Deployment Options

### 1. GitHub Pages (Static Files - Easiest)

**Best for:** Simple integrations, static websites, minimal maintenance

```bash
# 1. Fork/clone the repository
git clone https://github.com/yourusername/pyras-public-barter-credit.git
cd pyras-public-barter-credit

# 2. Enable GitHub Pages in repository settings
# Go to Settings > Pages > Source: GitHub Actions

# 3. The workflow will automatically:
# - Generate static JSON files daily
# - Deploy to GitHub Pages
# - Update URLs in examples
```

**Access your data at:**
- `https://yourusername.github.io/pyras-public-barter-credit/barter-credit.json`
- `https://yourusername.github.io/pyras-public-barter-credit/index.html`

### 2. Heroku (Full API - Recommended)

**Best for:** Full API functionality, automatic scaling, easy maintenance

```bash
# 1. Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login and create app
heroku login
heroku create your-pyra-credit-api

# 3. Set environment variables
heroku config:set COINGECKO_API_KEY=your_api_key_here
heroku config:set UPDATE_INTERVAL=300

# 4. Deploy
git push heroku main

# 5. Open your API
heroku open
```

**Your API will be available at:**
- `https://your-pyra-credit-api.herokuapp.com/api/barter-credit`

### 3. Railway (Modern Alternative)

**Best for:** Modern deployment, great developer experience

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and deploy
railway login
railway up

# 3. Set environment variables in Railway dashboard
# COINGECKO_API_KEY=your_key_here
```

### 4. Vercel (Serverless)

**Best for:** Serverless deployment, global CDN

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy
vercel

# 3. Set environment variables in Vercel dashboard
```

### 5. Docker (Any Platform)

**Best for:** Consistent deployment across platforms

```bash
# 1. Build image
docker build -t pyra-barter-credit .

# 2. Run container
docker run -p 5000:5000 \
  -e COINGECKO_API_KEY=your_key_here \
  pyra-barter-credit

# 3. Access at http://localhost:5000
```

## Detailed Deployment Instructions

### GitHub Pages Setup (Static)

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone
   git clone https://github.com/yourusername/pyras-public-barter-credit.git
   cd pyras-public-barter-credit
   ```

2. **Configure GitHub Actions**
   - Go to your repository settings
   - Navigate to "Pages"
   - Set Source to "GitHub Actions"
   - The workflow in `.github/workflows/deploy.yml` will handle the rest

3. **Add Secrets (Optional)**
   - Go to Settings > Secrets and Variables > Actions
   - Add `COINGECKO_API_KEY` for higher rate limits

4. **Access Your Data**
   - JSON: `https://yourusername.github.io/pyras-public-barter-credit/barter-credit.json`
   - HTML: `https://yourusername.github.io/pyras-public-barter-credit/index.html`
   - Embed: `https://yourusername.github.io/pyras-public-barter-credit/embed.js`

### Heroku Deployment (Full API)

1. **Prerequisites**
   - Heroku account
   - Heroku CLI installed
   - Git repository

2. **Create and Configure App**
   ```bash
   # Login to Heroku
   heroku login
   
   # Create app
   heroku create your-pyra-credit-api
   
   # Add environment variables
   heroku config:set COINGECKO_API_KEY=your_api_key_here
   heroku config:set UPDATE_INTERVAL=300
   heroku config:set PORT=80
   ```

3. **Deploy**
   ```bash
   # Deploy from main branch
   git push heroku main
   
   # Check logs
   heroku logs --tail
   
   # Open app
   heroku open
   ```

4. **Custom Domain (Optional)**
   ```bash
   heroku domains:add pyra-credit.yourdomain.com
   # Then configure DNS to point to Heroku
   ```

### Railway Deployment

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   # or
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Deploy**
   ```bash
   railway login
   railway up
   ```

3. **Configure Environment**
   - Go to Railway dashboard
   - Add environment variables:
     - `COINGECKO_API_KEY`
     - `UPDATE_INTERVAL=300`

### Docker Deployment

1. **Build Image**
   ```bash
   docker build -t pyra-barter-credit .
   ```

2. **Run Locally**
   ```bash
   docker run -p 5000:5000 \
     -e COINGECKO_API_KEY=your_key_here \
     -e UPDATE_INTERVAL=300 \
     pyra-barter-credit
   ```

3. **Deploy to Cloud**
   ```bash
   # Tag for registry
   docker tag pyra-barter-credit your-registry/pyra-barter-credit:latest
   
   # Push to registry
   docker push your-registry/pyra-barter-credit:latest
   
   # Deploy on cloud platform (AWS ECS, Google Cloud Run, etc.)
   ```

### Digital Ocean App Platform

1. **Create App**
   - Go to Digital Ocean App Platform
   - Connect your GitHub repository
   - Choose "Python" as runtime

2. **Configure**
   - Set build command: `pip install -r requirements.txt`
   - Set run command: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - Add environment variables

### AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize and Deploy**
   ```bash
   eb init
   eb create pyra-credit-api
   eb deploy
   ```

3. **Configure Environment**
   ```bash
   eb setenv COINGECKO_API_KEY=your_key_here
   eb setenv UPDATE_INTERVAL=300
   ```

## Environment Variables

All deployment methods need these environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COINGECKO_API_KEY` | No | None | CoinGecko API key for higher rate limits |
| `UPDATE_INTERVAL` | No | 300 | Cache update interval in seconds |
| `PORT` | No | 5000 | Server port (set by platform usually) |
| `BASE_URL` | No | None | Base URL for embed scripts |

## Custom Domain Setup

### Heroku Custom Domain
```bash
heroku domains:add pyra-credit.yourdomain.com
heroku certs:auto:enable
```

### Railway Custom Domain
1. Go to Railway dashboard
2. Navigate to your project
3. Go to Settings > Domains
4. Add your custom domain

### GitHub Pages Custom Domain
1. Go to repository Settings > Pages
2. Add your custom domain
3. Create a `CNAME` file in your repository root with your domain

## SSL/HTTPS Setup

Most platforms (Heroku, Railway, Vercel) automatically provide HTTPS. For custom deployments:

### Let's Encrypt with Nginx
```nginx
server {
    listen 80;
    server_name pyra-credit.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name pyra-credit.yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring and Maintenance

### Health Checks
All deployments include a `/health` endpoint for monitoring:
```bash
curl https://your-domain.com/health
```

### Logging
- **Heroku**: `heroku logs --tail`
- **Railway**: View logs in dashboard
- **Docker**: `docker logs container_name`

### Automated Updates
The GitHub Actions workflow handles:
- Daily static file generation
- Automatic deployment on code changes
- URL updates in examples

## Performance Optimization

### Caching Headers
The API includes appropriate cache headers:
- `Cache-Control: public, max-age=300` (5 minutes)
- `ETag` headers for conditional requests

### Rate Limiting
Built-in rate limiting respects CoinGecko API limits:
- Free tier: 30 calls/minute
- With API key: Higher limits

### CDN Integration
For high traffic, consider adding a CDN:
- **Cloudflare**: Easy setup with free tier
- **AWS CloudFront**: If using AWS
- **Fastly**: For advanced caching

## Troubleshooting

### Common Issues

1. **API Key Rate Limiting**
   - Solution: Get CoinGecko API key
   - Set `COINGECKO_API_KEY` environment variable

2. **Deployment Fails**
   - Check Python version (3.8+ required)
   - Verify all dependencies in `requirements.txt`
   - Check platform-specific logs

3. **CORS Issues**
   - API includes CORS headers by default
   - For custom domains, update `CORS_ORIGINS` environment variable

4. **Static Files Not Updating**
   - Check GitHub Actions status
   - Verify secrets are set correctly
   - Manual trigger: Go to Actions tab, run workflow

### Getting Help

1. Check the logs first
2. Review environment variables
3. Test locally with `python app.py`
4. Open GitHub issue with:
   - Deployment platform
   - Error messages
   - Configuration details

## Security Considerations

### Environment Variables
- Never commit API keys to git
- Use platform-specific secret management
- Rotate API keys periodically

### CORS Configuration
```python
# In production, specify exact origins
CORS_ORIGINS = "https://yourdomain.com,https://www.yourdomain.com"
```

### Rate Limiting
- Built-in protection against abuse
- Consider additional firewall rules for production

## Cost Estimates

### Free Options
- **GitHub Pages**: Free
- **Railway**: 500 hours/month free
- **Heroku**: 1000 dyno hours/month free (with credit card)

### Paid Options
- **Heroku Hobby**: $7/month
- **Railway Pro**: $5/month
- **Digital Ocean**: $5/month
- **AWS/GCP**: Variable based on usage

## Backup and Recovery

### Data Backup
Since the API fetches live data, no database backups are needed. However:
- Keep your repository backed up
- Document your environment variables
- Save your CoinGecko API key securely

### Disaster Recovery
1. **Complete Outage**: Redeploy from git repository
2. **API Key Issues**: Generate new CoinGecko API key
3. **Domain Issues**: Update DNS settings

---

## Quick Reference Commands

```bash
# Local development
python setup.py                    # Initial setup
python app.py                     # Run locally
python generate_static.py         # Generate static files

# Heroku
heroku create app-name            # Create app
heroku config:set KEY=value       # Set environment variable
git push heroku main              # Deploy
heroku logs --tail                # View logs

# Docker
docker build -t pyra-credit .     # Build image
docker run -p 5000:5000 pyra-credit  # Run container

# Railway
railway up                        # Deploy
railway logs                      # View logs

# GitHub Actions
# Push to main branch triggers deployment
git push origin main
```

Choose the deployment method that best fits your needs and technical requirements!
