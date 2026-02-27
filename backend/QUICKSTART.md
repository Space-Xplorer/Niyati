# Quick Start Guide - Project Niyati FastAPI Backend

## Prerequisites

- Python 3.11+
- PostgreSQL or SQLite
- Neo4j database
- Groq or OpenAI API key

## Installation

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set up environment variables:**

Create a `.env` file in the `backend` directory:

```bash
# Database
DATABASE_URL=sqlite:///niyati.db
# For PostgreSQL: postgresql://user:password@localhost:5432/niyati

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this

# LLM Provider
LLM_PROVIDER=groq
LLM_API_KEY=your_groq_api_key

# Optional Configuration
CIRCUIT_BREAKER_THRESHOLD=3
BATCH_SIZE=500
```

3. **Initialize the database:**
```bash
python init_db.py
```

4. **Start the FastAPI server:**
```bash
python app_fastapi.py
```

Or using uvicorn:
```bash
uvicorn app_fastapi:app --reload --host 0.0.0.0 --port 8000
```

## Testing the API

### 1. Register a user

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@niyati.com",
    "password": "admin123",
    "role": "Admin"
  }'
```

### 2. Login and get token

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@niyati.com",
    "password": "admin123"
  }'
```

Save the token from the response.

### 3. Access protected endpoints

```bash
# Get dashboard
curl -X GET http://localhost:8000/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get graph data
curl -X GET http://localhost:8000/graph \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Stream real-time logs
curl -N http://localhost:8000/logs/stream
```

### 4. Upload CSV files

```bash
curl -X POST http://localhost:8000/sync \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "e_invoices=@data/e_invoices.csv" \
  -F "eway_bills=@data/eway_bills.csv" \
  -F "entity_master=@data/entity_master.csv" \
  -F "filing_history=@data/filing_history.csv" \
  -F "purchase_register=@data/purchase_register.csv" \
  -F "returns_summary=@data/returns_summary.csv"
```

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive documentation where you can test all endpoints directly from your browser.

## Architecture Overview

```
FastAPI Application (app_fastapi.py)
├── Authentication Endpoints (/auth/register, /auth/login)
├── SSE Streaming (/logs/stream)
├── Data Ingestion (/sync)
├── Risk Analysis (/pre-audit, /risk/{gstin})
├── Dashboard (/dashboard)
└── Graph Visualization (/graph)

LangGraph Workflow (orchestration/)
├── Agent 1: Ingestion Wrangler
├── Agent 2: Graph Architect
├── Agent 3: Risk Detective (concurrent)
├── Agent 4: Predictive Analyst (concurrent)
└── Agent 5: Niyati Explainer

Databases
├── PostgreSQL/SQLite (relational data, users, predictions)
└── Neo4j (knowledge graph, structural patterns)
```

## Key Features Implemented

✅ **Task 12.1**: SSE streaming endpoint for real-time agent logs  
✅ **Task 12.2**: POST /sync endpoint for CSV upload and workflow trigger  
✅ **Task 12.3**: POST /pre-audit endpoint for on-demand GSTIN checks  
✅ **Task 12.5**: GET /dashboard endpoint with RBAC filtering  
✅ **Task 12.7**: GET /graph endpoint with Neo4j integration  
✅ **Task 12.8**: GET /risk/{gstin} endpoint with shape plot data  
✅ **Task 12.9**: Error handling middleware for consistent responses  

## RBAC (Role-Based Access Control)

### Admin Role
- Full access to all data
- Can view all GSTINs
- No filtering applied

### Business_Owner Role
- Access only to their own GSTIN
- Automatic filtering on all queries
- Can view related vendors/buyers

## Troubleshooting

### Database Connection Issues

If you see database connection errors:
1. Check your `DATABASE_URL` in `.env`
2. Ensure PostgreSQL/SQLite is running
3. Run `python init_db.py` to create tables

### Neo4j Connection Issues

If graph endpoints fail:
1. Verify Neo4j is running: `neo4j status`
2. Check `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` in `.env`
3. Test connection: `cypher-shell -u neo4j -p password`

### LLM API Issues

If narrative generation fails:
1. Verify `LLM_API_KEY` is set correctly
2. Check `LLM_PROVIDER` is either "groq" or "openai"
3. The system will fall back to template-based narratives

## Next Steps

1. **Frontend Integration**: Connect Next.js frontend to these endpoints
2. **Testing**: Run property-based tests and integration tests
3. **Deployment**: Deploy to production with proper security configurations
4. **Monitoring**: Set up logging and monitoring for production

## Support

For issues or questions, refer to:
- API Documentation: `API_DOCUMENTATION.md`
- Design Document: `.kiro/specs/project-niyati/design.md`
- Requirements: `.kiro/specs/project-niyati/requirements.md`
