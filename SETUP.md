# Project Niyati - Setup Guide

## Overview

Project Niyati is a Real-time GST Intelligence & Fraud Detection Platform. This guide will help you set up the development environment.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git

## Quick Start

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd project-niyati
```

### 2. Start Database Services

```bash
# Start PostgreSQL and Neo4j using Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps
```

Expected output:
```
NAME                IMAGE                    STATUS
niyati-neo4j        neo4j:5.15-community     Up (healthy)
niyati-postgres     postgres:15-alpine       Up (healthy)
```

### 3. Configure Environment Variables

Edit `backend/.env` and set your API keys:

```bash
cd backend
cp .env.example .env
# Edit .env and set:
# - LLM_API_KEY (get from https://console.groq.com or OpenAI)
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string (already configured)
- `NEO4J_URI`: Neo4j connection URI (already configured)
- `NEO4J_USER`: Neo4j username (already configured)
- `NEO4J_PASSWORD`: Neo4j password (already configured)
- `LLM_PROVIDER`: "groq" or "openai"
- `LLM_API_KEY`: Your LLM API key ⚠️ **REQUIRED**
- `JWT_SECRET`: Secret for JWT tokens (already configured)
- `CIRCUIT_BREAKER_THRESHOLD`: Circuit breaker threshold (already configured)
- `BATCH_SIZE`: Neo4j batch size (already configured)

### 4. Install Backend Dependencies

```bash
# From backend directory
pip install -r requirements.txt
```

Required packages:
- `langgraph`: Multi-agent orchestration
- `neo4j`: Neo4j graph database driver
- `interpret`: Explainable Boosting Machine (EBM)
- `fastapi`: REST API framework
- `pydantic`: Data validation
- `langchain-groq`: LLM integration
- `circuitbreaker`: Resilience patterns
- `sse-starlette`: Server-Sent Events
- `uvicorn`: ASGI server

### 5. Verify Setup

```bash
# From backend directory
python verify_setup.py
```

This will check:
- ✅ Environment variables
- ✅ Python dependencies
- ✅ Data files (CSV files in `backend/data/`)
- ✅ Model files (trained EBM model in `backend/model/`)
- ✅ PostgreSQL connection
- ✅ Neo4j connection

### 6. Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

### 7. Start Development Servers

**Backend (Terminal 1):**
```bash
cd backend
uvicorn app:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

## Project Structure

```
project-niyati/
├── backend/
│   ├── data/                    # CSV data files (already present)
│   │   ├── e_invoices.csv
│   │   ├── eway_bills.csv
│   │   ├── entity_master.csv
│   │   ├── filing_history.csv
│   │   ├── purchase_register.csv
│   │   ├── returns_summary.csv
│   │   └── feature_vectors.csv
│   ├── model/                   # ML models (already present)
│   │   ├── daksha_ebm.pkl       # Trained EBM model
│   │   ├── feature_engineering.py
│   │   └── ebm_training.py
│   ├── orchestration/           # LangGraph agents (to be implemented)
│   ├── .env                     # Environment configuration
│   ├── .env.example             # Environment template
│   ├── requirements.txt         # Python dependencies
│   ├── verify_setup.py          # Setup verification script
│   └── app.py                   # FastAPI application (to be updated)
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # React components
│   │   └── context/             # React context
│   ├── package.json             # Node dependencies
│   └── tsconfig.json            # TypeScript config
├── docker-compose.yml           # Database services
└── SETUP.md                     # This file
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Orchestration**: LangGraph for multi-agent workflow
- **Databases**: 
  - PostgreSQL (via Supabase) for relational data
  - Neo4j for knowledge graph
- **ML**: Microsoft interpret library (EBM)
- **LLM**: Groq (Llama-3-8b) or OpenAI (GPT-4o)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: TailwindCSS v4.2
- **UI Components**: Shadcn/UI (to be configured)
- **Visualization**: react-force-graph (to be installed)
- **Language**: TypeScript

## Database Access

### PostgreSQL
```bash
# Connect using psql
docker exec -it niyati-postgres psql -U niyati_user -d niyati_db

# Or use any PostgreSQL client with:
# Host: localhost
# Port: 5432
# User: niyati_user
# Password: niyati_password
# Database: niyati_db
```

### Neo4j
```bash
# Access Neo4j Browser
open http://localhost:7474

# Credentials:
# Username: neo4j
# Password: niyati_password
```

## Verification Checklist

Run `python backend/verify_setup.py` to check:

- [x] **Data Files**: All 7 CSV files present (1,770 KB - 479 KB)
- [x] **Model Files**: Trained EBM model (1,993 KB) and scripts
- [ ] **Environment Variables**: LLM_API_KEY needs to be set
- [ ] **Python Dependencies**: Install missing packages (neo4j, circuitbreaker)
- [ ] **PostgreSQL**: Database connection (requires docker-compose up)
- [ ] **Neo4j**: Graph database connection (requires docker-compose up)

## Current Status (Task 1)

### ✅ Completed
1. Project structure verified (backend/frontend directories exist)
2. Data files verified (all 7 CSV files present in `backend/data/`)
3. Trained EBM model verified (`backend/model/daksha_ebm.pkl`)
4. Feature engineering scripts verified
5. Frontend TypeScript configuration verified
6. Frontend TailwindCSS v4.2 configuration verified
7. Created `docker-compose.yml` for PostgreSQL and Neo4j
8. Updated `backend/.env` with all required environment variables
9. Updated `backend/.env.example` with template
10. Updated `backend/requirements.txt` with all required dependencies
11. Created `verify_setup.py` script for automated verification

### ⚠️ Pending User Action
1. **Set LLM_API_KEY**: Edit `backend/.env` and add your Groq or OpenAI API key
2. **Start Docker services**: Run `docker-compose up -d`
3. **Install Python dependencies**: Run `pip install -r backend/requirements.txt`
4. **Install Shadcn/UI**: Run `npx shadcn-ui@latest init` in frontend directory

### 📝 Notes
- The existing `backend/app.py` uses Flask, but the spec requires FastAPI
- This will be updated in subsequent tasks (Task 2-10)
- Data, mock data, feature engineering, and trained EBM model are already complete
- Focus is on building the 5 LangGraph agents that orchestrate existing functionality

## Next Steps

After completing the setup:
1. Proceed to **Task 2**: Create Agent 1 (Ingestion Wrangler)
2. Implement the 5 LangGraph agents
3. Build FastAPI endpoints
4. Implement frontend components

## Troubleshooting

### Docker services won't start
```bash
# Check if ports are already in use
netstat -an | findstr "5432 7474 7687"

# Stop and remove containers
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Python package installation fails
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

### Database connection fails
```bash
# Check service health
docker-compose ps

# View logs
docker-compose logs postgres
docker-compose logs neo4j

# Restart services
docker-compose restart
```

## Support

For issues or questions:
1. Check the verification script output: `python backend/verify_setup.py`
2. Review the logs: `docker-compose logs`
3. Refer to the design document: `.kiro/specs/project-niyati/design.md`
