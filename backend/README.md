# Backend API Documentation

## Overview

The Project Niyati backend is built with FastAPI and provides REST API endpoints for GST fraud detection. It orchestrates five intelligent agents using LangGraph, stores data in PostgreSQL and Neo4j, and provides real-time observability through Server-Sent Events.

## Architecture

### Multi-Agent System

The backend uses LangGraph to orchestrate five specialized agents:

1. **Ingestion Wrangler** (`agent_ingestion_wrangler.py`)
   - Validates CSV file schemas
   - Cleans and transforms data
   - Engineers 14 fraud-detection features
   - Persists to PostgreSQL staging tables

2. **Graph Architect** (`agent_graph_architect.py`)
   - Creates Taxpayer, Invoice, and EwayBill nodes in Neo4j
   - Establishes relationships (ISSUED, TO, BACKED_BY, SHARED_CONTACT)
   - Enforces uniqueness constraints
   - Uses UNWIND batching for performance

3. **Risk Detective** (`agent_risk_detective.py`)
   - Detects circular trading patterns (3-hop paths)
   - Identifies ghost invoices (high-value without e-way bills)
   - Discovers spider web networks (shared contacts)
   - Persists findings to PostgreSQL

4. **Predictive Analyst** (`agent_predictive_analyst.py`)
   - Loads trained EBM model
   - Computes risk probabilities (0-1)
   - Extracts top 3 feature contributions
   - Classifies as LOW/MEDIUM/HIGH risk

5. **Niyati Explainer** (`agent_niyati_explainer.py`)
   - Generates plain-language audit narratives
   - Uses Groq (Llama-3-8b) or OpenAI (GPT-4o)
   - Implements circuit breaker pattern
   - Falls back to template-based narratives

### Technology Stack

- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM for SQLite
- **Neo4j Python Driver** - Graph database client
- **LangGraph** - Multi-agent orchestration
- **InterpretML** - Explainable Boosting Machine
- **Flask-Bcrypt** - Password hashing
- **PyJWT** - JSON Web Token authentication
- **Pandas** - Data manipulation
- **Python-dotenv** - Environment configuration

## Installation

### Prerequisites

- Python 3.9 or higher
- Neo4j 5+ (or use Docker)
- pip or conda

### Setup

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the `backend/` directory:

```env
# SQLite Configuration (file-based database)
DATABASE_URL=sqlite:///niyati.db

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# LLM Configuration
LLM_PROVIDER=groq  # or "openai"
LLM_API_KEY=your_api_key_here

# JWT Configuration
JWT_SECRET=your-super-secret-key-change-in-production

# Optional: Email Configuration (for HIGH_RISK notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
AUDIT_TEAM_EMAIL=audit@example.com
```

4. **Initialize database**
```bash
python init_db.py
```

This creates all required PostgreSQL tables and Neo4j constraints.

## Running the Server

### Development Mode

```bash
python main.py
```

Server runs on http://localhost:8000

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Authentication

#### POST /auth/register

Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "role": "Admin",  // or "Business_Owner"
  "gstin": "29ABCDE1234F1Z5"  // Required for Business_Owner
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully"
}
```

**Errors:**
- `400` - Invalid role or missing fields
- `409` - User already exists

---

#### POST /auth/login

Authenticate and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "Admin",
    "gstin": null
  }
}
```

**Errors:**
- `400` - Missing email or password
- `401` - Invalid credentials

---

### Data Ingestion

#### POST /sync

Upload six CSV files and trigger full workflow.

**Authentication:** Required (Bearer token)

**Request:** `multipart/form-data`

**Form Fields:**
- `e_invoices` - File (CSV)
- `eway_bills` - File (CSV)
- `entity_master` - File (CSV)
- `filing_history` - File (CSV)
- `purchase_register` - File (CSV)
- `returns_summary` - File (CSV)

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Workflow completed successfully",
  "summary": {
    "invoices_processed": 1500,
    "taxpayers_created": 450,
    "circular_trade_patterns": 12,
    "ghost_invoices": 34,
    "spider_webs": 5,
    "high_risk_entities": 23
  },
  "execution_time_seconds": 45.2
}
```

**Errors:**
- `400` - Invalid file type or CSV parsing error
- `401` - Missing or invalid token
- `500` - Workflow execution failed

**CSV File Schemas:**

**e_invoices.csv:**
- `IRN` (string) - Invoice Reference Number
- `seller_gstin` (string) - Seller GSTIN
- `buyer_gstin` (string) - Buyer GSTIN
- `invoice_value` (float) - Invoice amount
- `invoice_date` (date) - Invoice date
- `DocNo` (string) - Document number

**eway_bills.csv:**
- `DocNo` (string) - Document number (matches invoice)
- `vehicle_no` (string) - Vehicle registration
- `distance` (float) - Distance in km
- `generated_date` (date) - E-way bill generation date

**entity_master.csv:**
- `gstin` (string) - GSTIN
- `business_name` (string) - Business name
- `phone` (string) - Contact phone
- `email` (string) - Contact email
- `address` (string) - Business address

**filing_history.csv:**
- `gstin` (string) - GSTIN
- `filing_period` (string) - Period (e.g., "2024-01")
- `days_delayed` (int) - Days delayed in filing
- `status` (string) - Filing status

**purchase_register.csv:**
- `buyer_gstin` (string) - Buyer GSTIN
- `seller_gstin` (string) - Seller GSTIN
- `invoice_value` (float) - Invoice amount
- `itc_claimed` (float) - ITC claimed

**returns_summary.csv:**
- `gstin` (string) - GSTIN
- `gstr1_sales` (float) - GSTR-1 sales
- `gstr3b_sales` (float) - GSTR-3B sales
- `period` (string) - Period

---

### Fraud Analysis

#### POST /pre-audit

Trigger on-demand fraud check for specific GSTIN.

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "gstin": "29ABCDE1234F1Z5"
}
```

**Response (200 OK):**
```json
{
  "gstin": "29ABCDE1234F1Z5",
  "risk_level": "HIGH_RISK",
  "risk_probability": 0.87,
  "top_drivers": [
    {
      "feature": "ghost_invoice_pct",
      "contribution": 0.34,
      "direction": "positive"
    },
    {
      "feature": "payment_gap_pct",
      "contribution": 0.28,
      "direction": "positive"
    },
    {
      "feature": "shared_contact_flag",
      "contribution": 0.15,
      "direction": "positive"
    }
  ],
  "circular_trade_count": 3,
  "ghost_invoice_count": 12,
  "spider_web_involvement": true,
  "narrative": "HIGH RISK — Entity 29ABCDE1234F1Z5 shows significant fraud indicators..."
}
```

**RBAC Rules:**
- Admin: Can audit any GSTIN
- Business_Owner: Can only audit their own GSTIN

**Errors:**
- `400` - Invalid GSTIN format
- `401` - Missing or invalid token
- `403` - Access denied (RBAC violation)
- `404` - No risk data found for GSTIN

---

### Dashboard

#### GET /dashboard

Retrieve dashboard data with health score and risk metrics.

**Authentication:** Required (Bearer token)

**Response (200 OK):**
```json
{
  "health_score": 78.5,
  "risk_level": "MEDIUM_RISK",
  "risk_probability": 0.215,
  "top_drivers": [
    {
      "feature": "filing_gap",
      "contribution": 0.12,
      "direction": "positive"
    },
    {
      "feature": "payment_gap_pct",
      "contribution": 0.08,
      "direction": "positive"
    },
    {
      "feature": "excess_itc_flag",
      "contribution": -0.05,
      "direction": "negative"
    }
  ],
  "vendor_risks": [
    {
      "vendor_gstin": "27XYZAB5678C1D2",
      "vendor_name": "ABC Traders",
      "risk_level": "HIGH_RISK",
      "itc_at_risk": 125000.0,
      "last_transaction_date": "2024-02-15"
    }
  ],
  "patterns": {
    "circular_trade": 2,
    "ghost_invoices": 5,
    "spider_web_involvement": false
  }
}
```

**RBAC Rules:**
- Admin: Sees aggregated data across all GSTINs
- Business_Owner: Sees only their GSTIN data

**Errors:**
- `401` - Missing or invalid token
- `404` - No dashboard data available

---

### Graph Visualization

#### GET /graph

Retrieve graph nodes and edges for visualization.

**Authentication:** Required (Bearer token)

**Response (200 OK):**
```json
{
  "nodes": [
    {
      "id": "29ABCDE1234F1Z5",
      "label": "Taxpayer",
      "name": "ABC Corporation",
      "risk_level": "HIGH_RISK"
    },
    {
      "id": "27XYZAB5678C1D2",
      "label": "Taxpayer",
      "name": "XYZ Traders",
      "risk_level": "LOW_RISK"
    }
  ],
  "edges": [
    {
      "source": "29ABCDE1234F1Z5",
      "target": "27XYZAB5678C1D2",
      "type": "TRANSACTION"
    }
  ]
}
```

**RBAC Rules:**
- Admin: Sees entire graph (up to 1000 nodes)
- Business_Owner: Sees only their network (1-hop neighbors)

**Errors:**
- `401` - Missing or invalid token
- `500` - Neo4j connection error

---

### Risk Details

#### GET /risk/{gstin}

Retrieve detailed risk data with EBM shape plots.

**Authentication:** Required (Bearer token)

**Path Parameters:**
- `gstin` (string) - GSTIN to query

**Response (200 OK):**
```json
{
  "gstin": "29ABCDE1234F1Z5",
  "risk_level": "HIGH_RISK",
  "risk_probability": 0.87,
  "top_drivers": [
    {
      "feature": "ghost_invoice_pct",
      "contribution": 0.34,
      "direction": "positive"
    }
  ],
  "shape_plots": [
    {
      "feature_name": "ghost_invoice_pct",
      "contribution_weight": 0.34,
      "feature_value": 45.2,
      "baseline_value": 5.0,
      "x_values": [0, 10, 20, 30, 40, 50],
      "y_values": [0, 0.05, 0.12, 0.22, 0.34, 0.45]
    }
  ]
}
```

**RBAC Rules:**
- Admin: Can query any GSTIN
- Business_Owner: Can only query their own GSTIN

**Errors:**
- `401` - Missing or invalid token
- `403` - Access denied (RBAC violation)
- `404` - No risk data found

---

### Real-Time Observability

#### GET /logs/stream

Server-Sent Events stream for real-time agent progress.

**Authentication:** Not required (public endpoint)

**Response:** `text/event-stream`

**Event Format:**
```
data: Agent 1: Validating e_invoices.csv - 1500 rows
data: Agent 1: Computing payment_gap feature...
data: Agent 2: Creating 450 Taxpayer nodes in batch 1/1
data: Agent 3: Analyzing 3-hop circular trading paths...
data: Agent 4: Computing risk scores for 450 entities
data: Agent 5: Generating audit narratives using groq
data: Workflow completed in 45.2s
```

**Usage Example (JavaScript):**
```javascript
const eventSource = new EventSource('http://localhost:8000/logs/stream');

eventSource.onmessage = (event) => {
  console.log('Agent update:', event.data);
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();
};
```

---

### Health Check

#### GET /health

Simple health check endpoint.

**Response (200 OK):**
```json
{
  "status": "ok",
  "message": "FastAPI backend is running"
}
```

---

## Database Models

### SQLite Tables

All tables are stored in a single `niyati.db` file in the backend directory.

**users**
- `id` (INTEGER, PK)
- `email` (VARCHAR, UNIQUE)
- `password_hash` (VARCHAR)
- `role` (VARCHAR) - "Admin" or "Business_Owner"
- `gstin` (VARCHAR, NULLABLE)
- `created_at` (TIMESTAMP)

**raw_invoices**
- `id` (INTEGER, PK)
- `irn` (VARCHAR, UNIQUE)
- `seller_gstin` (VARCHAR)
- `buyer_gstin` (VARCHAR)
- `invoice_value` (FLOAT)
- `invoice_date` (DATE)
- `DocNo` (VARCHAR)
- `uploaded_at` (TIMESTAMP)

**engineered_features**
- `id` (INTEGER, PK)
- `gstin` (VARCHAR)
- `payment_gap` (FLOAT)
- `payment_gap_pct` (FLOAT)
- `ghost_invoice_pct` (FLOAT)
- `shared_contact_flag` (BOOLEAN)
- `filing_gap` (FLOAT)
- `excess_itc_flag` (BOOLEAN)
- `feature_vector` (JSON)
- `computed_at` (TIMESTAMP)

**risk_predictions**
- `id` (INTEGER, PK)
- `gstin` (VARCHAR)
- `risk_probability` (FLOAT)
- `risk_level` (VARCHAR) - "LOW_RISK", "MEDIUM_RISK", "HIGH_RISK"
- `top_driver_1` (VARCHAR)
- `top_driver_1_contribution` (FLOAT)
- `top_driver_2` (VARCHAR)
- `top_driver_2_contribution` (FLOAT)
- `top_driver_3` (VARCHAR)
- `top_driver_3_contribution` (FLOAT)
- `model_version` (VARCHAR)
- `predicted_at` (TIMESTAMP)

**fraud_patterns**
- `id` (INTEGER, PK)
- `pattern_type` (VARCHAR) - "circular_trade", "ghost_invoice", "spider_web"
- `gstin_list` (JSON)
- `risk_score` (FLOAT)
- `detection_timestamp` (TIMESTAMP)

**audit_narratives**
- `id` (INTEGER, PK)
- `gstin` (VARCHAR)
- `narrative_text` (TEXT)
- `generated_at` (TIMESTAMP)

### Neo4j Graph Schema

**Nodes:**

**Taxpayer**
- `gstin` (STRING, UNIQUE)
- `business_name` (STRING)
- `phone` (STRING, HASHED)
- `email` (STRING, HASHED)
- `address` (STRING)
- `risk_level` (STRING)

**Invoice**
- `irn` (STRING, UNIQUE)
- `DocNo` (STRING)
- `invoice_value` (FLOAT)
- `invoice_date` (DATE)
- `seller_gstin` (STRING)
- `buyer_gstin` (STRING)

**EwayBill**
- `DocNo` (STRING, UNIQUE)
- `vehicle_no` (STRING)
- `distance` (FLOAT)
- `generated_date` (DATE)

**Relationships:**

- `(Taxpayer)-[:ISSUED]->(Invoice)` - Taxpayer issued an invoice
- `(Invoice)-[:TO]->(Taxpayer)` - Invoice sent to taxpayer
- `(Invoice)-[:BACKED_BY]->(EwayBill)` - Invoice has e-way bill
- `(Taxpayer)-[:SHARED_CONTACT]->(Taxpayer)` - Taxpayers share contact info

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created (registration successful) |
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (RBAC violation) |
| 404 | Not Found (resource doesn't exist) |
| 409 | Conflict (user already exists) |
| 500 | Internal Server Error |

---

## Testing

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test Suite

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Specific agent tests
pytest tests/unit/test_ingestion_wrangler_comprehensive.py
pytest tests/unit/test_graph_architect.py
pytest tests/unit/test_risk_detective.py
pytest tests/unit/test_predictive_analyst.py
pytest tests/unit/test_niyati_explainer.py
```

### Test Coverage

```bash
pytest --cov=. --cov-report=html
```

---

## Performance Optimization

### Neo4j Indexing

Ensure indexes are created for optimal query performance:

```cypher
CREATE CONSTRAINT taxpayer_gstin IF NOT EXISTS FOR (t:Taxpayer) REQUIRE t.gstin IS UNIQUE;
CREATE CONSTRAINT invoice_irn IF NOT EXISTS FOR (i:Invoice) REQUIRE i.irn IS UNIQUE;
CREATE INDEX taxpayer_risk IF NOT EXISTS FOR (t:Taxpayer) ON (t.risk_level);
```

### SQLite Indexing

SQLite automatically creates indexes for PRIMARY KEY and UNIQUE constraints. For additional performance:

```sql
CREATE INDEX IF NOT EXISTS idx_risk_predictions_gstin ON risk_predictions(gstin);
CREATE INDEX IF NOT EXISTS idx_fraud_patterns_type ON fraud_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_engineered_features_gstin ON engineered_features(gstin);
```

### Batch Processing

The Graph Architect uses UNWIND batching with batch size of 500 records for optimal Neo4j ingestion performance.

---

## Security Best Practices

1. **Change default JWT secret** in production
2. **Use strong passwords** for database connections
3. **Enable SSL/TLS** for PostgreSQL and Neo4j in production
4. **Rotate API keys** regularly
5. **Configure CORS** appropriately for production domains
6. **Use environment variables** for all secrets (never commit .env)
7. **Enable rate limiting** for public endpoints
8. **Monitor logs** for suspicious activity

---

## Troubleshooting

### Database Connection Errors

```bash
# Test Neo4j connection
cypher-shell -a bolt://localhost:7687 -u neo4j -p password

# Check SQLite database
sqlite3 niyati.db ".tables"
```

### LLM API Errors

If Groq/OpenAI API fails, the system automatically falls back to template-based narratives. Check:
- API key is valid
- API quota is not exceeded
- Network connectivity

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## Deployment

### Production Checklist

- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Configure production database URLs
- [ ] Enable SSL for database connections
- [ ] Set up proper CORS origins
- [ ] Configure email SMTP for notifications
- [ ] Set up monitoring and logging
- [ ] Enable rate limiting
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline
- [ ] Load test the application

### Docker Deployment

```bash
docker build -t niyati-backend .
docker run -p 8000:8000 --env-file .env niyati-backend
```

---

## Support

For issues or questions, please open an issue on GitHub or contact the development team.
