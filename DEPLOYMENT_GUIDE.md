# Niyati - Production Deployment Guide

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                    Next.js 16 (Vercel)                       │
│              https://niyati.yourdomain.com                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS/REST API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                       BACKEND                                │
│              FastAPI + LangGraph (Railway/Render)            │
│              https://api.niyati.yourdomain.com               │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌────────────┐
│   Neo4j      │ │ SQLite/  │ │   LLM API  │
│   (Aura)     │ │PostgreSQL│ │   (Groq)   │
│   Graph DB   │ │  (Neon)  │ │            │
└──────────────┘ └──────────┘ └────────────┘
```

## Deployment Options

### Option 1: Full Cloud (Recommended for Production)

**Cost: ~$50-100/month**

#### Frontend: Vercel
- **Why**: Zero-config Next.js deployment, global CDN, automatic HTTPS
- **Cost**: Free tier (Hobby) or $20/month (Pro)
- **Setup Time**: 5 minutes

#### Backend: Railway
- **Why**: Easy Python deployment, built-in PostgreSQL, good for FastAPI
- **Cost**: $5-20/month (usage-based)
- **Setup Time**: 10 minutes

#### Database (Neo4j): Neo4j Aura
- **Why**: Managed graph database, automatic backups
- **Cost**: Free tier (50k nodes) or $65/month (Professional)
- **Setup Time**: 5 minutes

#### Database (SQL): Neon PostgreSQL
- **Why**: Serverless PostgreSQL, auto-scaling, free tier available
- **Cost**: Free tier or $19/month (Pro)
- **Setup Time**: 5 minutes

#### LLM: Groq API
- **Why**: Fast inference, generous free tier
- **Cost**: Free tier (14,400 requests/day) or pay-as-you-go
- **Setup Time**: 2 minutes

---

### Option 2: Budget-Friendly (~$20/month)

#### Frontend: Vercel (Free)
#### Backend: Render (Free tier or $7/month)
#### Neo4j: Neo4j Aura Free Tier
#### SQL: SQLite (file-based, included)
#### LLM: Groq Free Tier

---

### Option 3: Self-Hosted (VPS)

**Cost: $10-40/month**

#### Single VPS: DigitalOcean/Hetzner/Linode
- 4GB RAM, 2 vCPUs minimum
- Run everything on one server using Docker Compose

---

## Step-by-Step Deployment

### Phase 1: Database Setup (15 minutes)

#### 1.1 Neo4j Aura Setup
```bash
# 1. Go to https://neo4j.com/cloud/aura/
# 2. Create free account
# 3. Create new instance (AuraDB Free)
# 4. Save credentials:
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

#### 1.2 PostgreSQL Setup (Neon)
```bash
# 1. Go to https://neon.tech/
# 2. Create free account
# 3. Create new project
# 4. Get connection string:
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb
```

**OR use SQLite (simpler, no setup needed)**
```bash
# Just use file-based database
DATABASE_URL=sqlite:///./instance/niyati.db
```

---

### Phase 2: Backend Deployment (20 minutes)

#### Option A: Railway (Recommended)

1. **Prepare Backend**
```bash
cd backend

# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Ensure requirements.txt is up to date
pip freeze > requirements.txt
```

2. **Deploy to Railway**
```bash
# 1. Go to https://railway.app/
# 2. Sign up with GitHub
# 3. Click "New Project" → "Deploy from GitHub repo"
# 4. Select your Niyati repository
# 5. Set root directory to "backend"
```

3. **Configure Environment Variables**
```bash
# In Railway dashboard, add these variables:
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
DATABASE_URL=postgresql://... (or sqlite:///./instance/niyati.db)
JWT_SECRET_KEY=your-super-secret-key-change-this
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=optional
ANTHROPIC_API_KEY=optional
FRONTEND_URL=https://niyati.vercel.app
```

4. **Deploy**
- Railway auto-deploys on git push
- Get your backend URL: `https://your-app.railway.app`

#### Option B: Render

1. **Create render.yaml**
```yaml
services:
  - type: web
    name: niyati-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: NEO4J_URI
        sync: false
      - key: NEO4J_USER
        sync: false
      - key: NEO4J_PASSWORD
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: LLM_PROVIDER
        value: groq
      - key: GROQ_API_KEY
        sync: false
```

2. **Deploy**
```bash
# 1. Go to https://render.com/
# 2. Connect GitHub repository
# 3. Create new Web Service
# 4. Point to backend directory
# 5. Add environment variables
```

---

### Phase 3: Frontend Deployment (10 minutes)

#### Vercel Deployment

1. **Update API URL**
```bash
cd frontend

# Edit .env.local
echo "NEXT_PUBLIC_API_URL=https://your-backend.railway.app" > .env.local
```

2. **Deploy to Vercel**
```bash
# Option 1: Vercel CLI
npm install -g vercel
vercel login
vercel --prod

# Option 2: Vercel Dashboard
# 1. Go to https://vercel.com/
# 2. Import Git Repository
# 3. Select your Niyati repo
# 4. Set root directory to "frontend"
# 5. Add environment variable:
#    NEXT_PUBLIC_API_URL=https://your-backend.railway.app
# 6. Deploy
```

3. **Configure Custom Domain (Optional)**
```bash
# In Vercel dashboard:
# Settings → Domains → Add Domain
# Add: niyati.yourdomain.com
# Update DNS records as instructed
```

---

### Phase 4: Initialize Database (5 minutes)

```bash
# Run database initialization
curl -X POST https://your-backend.railway.app/init-db \
  -H "Content-Type: application/json"

# Create admin user
curl -X POST https://your-backend.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@yourdomain.com",
    "password": "SecurePassword123!",
    "role": "Admin"
  }'
```

---

## Environment Variables Reference

### Backend (.env)
```bash
# Neo4j Configuration
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# Database Configuration
DATABASE_URL=postgresql://user:pass@host/db
# OR for SQLite:
# DATABASE_URL=sqlite:///./instance/niyati.db

# Security
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Configuration
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxxxx
OPENAI_API_KEY=sk-xxxxx (optional)
ANTHROPIC_API_KEY=sk-ant-xxxxx (optional)

# CORS
FRONTEND_URL=https://niyati.vercel.app

# Optional: Email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Docker Deployment (Self-Hosted)

### Create docker-compose.yml
```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/your-password
    volumes:
      - neo4j_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: your-password
      DATABASE_URL: sqlite:///./instance/niyati.db
      JWT_SECRET_KEY: your-secret-key
      LLM_PROVIDER: groq
      GROQ_API_KEY: ${GROQ_API_KEY}
    depends_on:
      - neo4j
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  neo4j_data:
```

### Deploy
```bash
# Create .env file with secrets
echo "GROQ_API_KEY=your-key" > .env

# Start services
docker-compose up -d

# Initialize database
docker-compose exec backend python init_db.py
```

---

## Post-Deployment Checklist

### Security
- [ ] Change all default passwords
- [ ] Generate strong JWT_SECRET_KEY (min 32 characters)
- [ ] Enable HTTPS (automatic on Vercel/Railway)
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable Neo4j authentication
- [ ] Review and restrict API access

### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure uptime monitoring (UptimeRobot)
- [ ] Enable application logs
- [ ] Set up alerts for high-risk detections

### Backups
- [ ] Enable Neo4j Aura automatic backups
- [ ] Set up PostgreSQL/SQLite backups
- [ ] Export configuration regularly

### Performance
- [ ] Enable CDN for static assets (automatic on Vercel)
- [ ] Configure database connection pooling
- [ ] Set up caching for API responses
- [ ] Monitor API response times

---

## Cost Breakdown

### Minimal Setup (Free Tier)
- Frontend: Vercel Free - $0
- Backend: Render Free - $0
- Neo4j: Aura Free - $0
- PostgreSQL: Neon Free - $0
- LLM: Groq Free - $0
**Total: $0/month** (with limitations)

### Recommended Production
- Frontend: Vercel Pro - $20/month
- Backend: Railway Pro - $20/month
- Neo4j: Aura Professional - $65/month
- PostgreSQL: Neon Pro - $19/month
- LLM: Groq Pay-as-you-go - ~$10/month
**Total: ~$134/month**

### Budget Production
- Frontend: Vercel Free - $0
- Backend: Railway Hobby - $5/month
- Neo4j: Aura Free - $0
- PostgreSQL: SQLite - $0
- LLM: Groq Free - $0
**Total: $5/month** (good for small teams)

---

## Scaling Considerations

### When to Scale
- More than 100 concurrent users
- More than 10,000 entities in Neo4j
- API response times > 2 seconds
- Database queries taking > 1 second

### Scaling Strategy
1. **Horizontal Scaling**: Add more backend instances (Railway auto-scales)
2. **Database Optimization**: Add indexes, optimize queries
3. **Caching**: Implement Redis for frequently accessed data
4. **CDN**: Use Cloudflare for global distribution
5. **Load Balancing**: Use Railway's built-in load balancer

---

## Troubleshooting

### Backend won't start
```bash
# Check logs
railway logs

# Common issues:
# 1. Missing environment variables
# 2. Database connection failed
# 3. Port already in use
```

### Frontend can't connect to backend
```bash
# Check CORS settings in backend
# Verify NEXT_PUBLIC_API_URL is correct
# Check browser console for errors
```

### Neo4j connection timeout
```bash
# Verify NEO4J_URI format: neo4j+s://host
# Check firewall rules
# Verify credentials
```

---

## Support & Maintenance

### Regular Tasks
- Weekly: Review error logs
- Monthly: Update dependencies
- Quarterly: Security audit
- Yearly: Review and optimize costs

### Updates
```bash
# Backend updates
cd backend
pip install --upgrade -r requirements.txt

# Frontend updates
cd frontend
npm update

# Redeploy
git push origin main  # Auto-deploys on Vercel/Railway
```

---

## Quick Start Commands

```bash
# 1. Get API keys
# - Neo4j Aura: https://neo4j.com/cloud/aura/
# - Groq: https://console.groq.com/

# 2. Deploy backend to Railway
railway login
railway init
railway up

# 3. Deploy frontend to Vercel
vercel login
vercel --prod

# 4. Initialize database
curl -X POST https://your-backend.railway.app/init-db

# 5. Create admin user
curl -X POST https://your-backend.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"SecurePass123!","role":"Admin"}'

# 6. Access your app
# https://niyati.vercel.app
```

---

## Next Steps

1. **Set up monitoring**: Integrate Sentry for error tracking
2. **Configure alerts**: Set up email notifications for HIGH_RISK detections
3. **Add analytics**: Integrate PostHog or Google Analytics
4. **Custom domain**: Configure your own domain
5. **SSL certificates**: Automatic on Vercel/Railway
6. **Backup strategy**: Set up automated backups
7. **Documentation**: Create user guides and API docs

---

## Recommended: Railway + Vercel Setup (Fastest)

### Total Time: 30 minutes
### Total Cost: $5-25/month

1. **Backend on Railway** (10 min)
   - Connect GitHub repo
   - Set environment variables
   - Deploy automatically

2. **Frontend on Vercel** (5 min)
   - Import GitHub repo
   - Set API URL
   - Deploy automatically

3. **Neo4j Aura Free** (5 min)
   - Create account
   - Create database
   - Copy credentials

4. **Initialize** (5 min)
   - Run init-db endpoint
   - Create admin user
   - Upload sample data

5. **Test** (5 min)
   - Login to frontend
   - Upload CSV files
   - View dashboard

**Done! Your system is live.**
