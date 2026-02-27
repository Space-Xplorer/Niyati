# Project Niyati API Documentation

## Overview

This document describes the FastAPI endpoints for the Project Niyati GST fraud detection platform.

## Running the Application

### Using FastAPI (Recommended)

```bash
cd backend
python app_fastapi.py
```

The API will be available at `http://localhost:8000`

### Using Uvicorn

```bash
cd backend
uvicorn app_fastapi:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication

#### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "role": "Admin",
  "gstin": "27AAPFU0939F1ZV"
}
```

**Response:**
```json
{
  "message": "User registered successfully"
}
```

#### POST /auth/login
Authenticate and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
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

### Real-Time Monitoring

#### GET /logs/stream
Server-Sent Events endpoint for real-time agent progress updates.

**Headers:**
```
Accept: text/event-stream
```

**Response:**
```
data: Workflow started
data: Agent 1: Validating e_invoices.csv - 1500 rows
data: Agent 2: Creating 500 nodes in batch 1/3
data: Agent 3: Analyzing 3-hop circular trading paths...
data: Agent 4: Computing risk scores for 150 entities
data: Agent 5: Generating audit narratives using groq
data: Workflow completed in 45.2s
```

### Data Ingestion

#### POST /sync
Upload 6 CSV files and trigger full workflow.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `e_invoices`: CSV file
- `eway_bills`: CSV file
- `entity_master`: CSV file
- `filing_history`: CSV file
- `purchase_register`: CSV file
- `returns_summary`: CSV file

**Response:**
```json
{
  "status": "success",
  "message": "Workflow completed successfully",
  "summary": {
    "entities_processed": 150,
    "circular_trade_patterns": 12,
    "ghost_invoice_entities": 45,
    "spider_web_clusters": 8,
    "high_risk_entities": 23
  },
  "execution_time_seconds": 45.2
}
```

### Risk Analysis

#### POST /pre-audit
Trigger on-demand fraud check for specific GSTIN.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "gstin": "27AAPFU0939F1ZV"
}
```

**Response:**
```json
{
  "gstin": "27AAPFU0939F1ZV",
  "risk_level": "HIGH_RISK",
  "risk_probability": 0.8923,
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
      "contribution": 0.19,
      "direction": "positive"
    }
  ],
  "circular_trade_count": 2,
  "ghost_invoice_count": 12,
  "spider_web_involvement": true,
  "narrative": "HIGH RISK — Entity 27AAPFU0939F1ZV shows 89.2% fraud probability..."
}
```

#### GET /risk/{gstin}
Get detailed risk data with EBM shape plots.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "gstin": "27AAPFU0939F1ZV",
  "risk_level": "HIGH_RISK",
  "risk_probability": 0.8923,
  "top_drivers": [...],
  "shape_plots": [
    {
      "feature_name": "ghost_invoice_pct",
      "contribution_weight": 0.34,
      "feature_value": 34.5,
      "baseline_value": 5.2,
      "x_values": [0, 10, 20, 30, 40, 50],
      "y_values": [0, 0.1, 0.2, 0.35, 0.4, 0.45]
    }
  ]
}
```

### Dashboard

#### GET /dashboard
Get dashboard data with RBAC filtering.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "health_score": 11.0,
  "risk_level": "HIGH_RISK",
  "risk_probability": 0.8923,
  "top_drivers": [...],
  "vendor_risks": [
    {
      "vendor_gstin": "29AABCU9603R1ZX",
      "vendor_name": "ABC Traders",
      "risk_level": "HIGH_RISK",
      "itc_at_risk": 450000.00,
      "last_transaction_date": "2024-01-15"
    }
  ],
  "patterns": {
    "circular_trade": 2,
    "ghost_invoices": 12,
    "spider_web_involvement": true
  }
}
```

### Graph Visualization

#### GET /graph
Get graph nodes and edges with RBAC filtering.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "27AAPFU0939F1ZV",
      "label": "Taxpayer",
      "name": "XYZ Corp",
      "risk_level": "HIGH_RISK"
    }
  ],
  "edges": [
    {
      "source": "27AAPFU0939F1ZV",
      "target": "29AABCU9603R1ZX",
      "type": "TRANSACTION"
    }
  ]
}
```

## Role-Based Access Control (RBAC)

### Admin Role
- Can access all data across all GSTINs
- No filtering applied to queries
- Full system visibility

### Business_Owner Role
- Can only access data for their associated GSTIN
- Automatic filtering applied to all queries
- Limited to their own transactions and related entities

## Error Responses

### 400 Bad Request
```json
{
  "message": "Invalid input: missing required field"
}
```

### 401 Unauthorized
```json
{
  "message": "Token is missing or invalid"
}
```

### 403 Forbidden
```json
{
  "message": "Access denied: Business_Owner can only access their own GSTIN"
}
```

### 404 Not Found
```json
{
  "message": "No risk data found for GSTIN 27AAPFU0939F1ZV"
}
```

### 500 Internal Server Error
```json
{
  "message": "Internal server error"
}
```

## Environment Variables

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/niyati
# or for SQLite: sqlite:///niyati.db

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# JWT
JWT_SECRET_KEY=your-secret-key-here

# LLM Provider
LLM_PROVIDER=groq  # or openai
LLM_API_KEY=your-api-key-here

# Circuit Breaker
CIRCUIT_BREAKER_THRESHOLD=3

# Batching
BATCH_SIZE=500
```

## Testing with cURL

### Register User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123","role":"Admin"}'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### Get Dashboard (with token)
```bash
curl -X GET http://localhost:8000/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Stream Logs (SSE)
```bash
curl -N http://localhost:8000/logs/stream
```

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to test all endpoints directly from your browser.
