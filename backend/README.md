# Niyati Backend Service

![Backend](https://img.shields.io/badge/Backend-Flask%2FFastAPI-green.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Databases](https://img.shields.io/badge/Databases-Neo4j%20%7C%20SQLite-brightgreen.svg)

## 📖 Overview

The Niyati backend is a sophisticated multi-agent orchestration platform built with **Flask** and **LangGraph** that provides enterprise-grade GST (Goods and Services Tax) risk analysis, fraud detection, and compliance management. The backend leverages Neo4j knowledge graphs, machine learning models, and autonomous AI agents to deliver actionable insights.

### Core Features

- **🤖 LangGraph Multi-Agent System**: 6+ autonomous agents for specialized tasks
- **📊 Explainable ML Models**: InterpretML-based EBM for vendor risk scoring
- **🔗 Knowledge Graph Database**: Neo4j for entity relationship mapping
- **🔐 Enterprise Authentication**: JWT + RBAC with role-based data filtering
- **🛡️ Resilience Patterns**: Circuit breaker, retry logic, and graceful degradation
- **📡 REST API**: Clean, well-documented endpoints with async support
- **💾 Dual Database**: SQLite for transactions, Neo4j for relationships

---

## 🏗️ Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────┐
│        REST API Layer (Flask Blueprints)        │
│  /auth, /dashboard, /graph, /admin, /workflow   │
├─────────────────────────────────────────────────┤
│    RBAC & Authentication Middleware             │
│    JWT Token Validation, Permission Checks      │
├─────────────────────────────────────────────────┤
│    Business Logic Layer                         │
│  Dashboard Services, Graph Queries, Workflows   │
├─────────────────────────────────────────────────┤
│    Agent Orchestration (LangGraph)              │
│  Multi-Agent Workflows with State Management    │
├─────────────────────────────────────────────────┤
│    Data Processing Layer                        │
│  Feature Engineering, CSV Validation, Batching  │
├─────────────────────────────────────────────────┤
│    Database Adapters                            │
│  ┌──────────────┐  ┌──────────────────────┐    │
│  │  SQLAlchemy  │  │  Neo4j Python Driver │    │
│  │   (SQLite)   │  │   (Knowledge Graph)  │    │
│  └──────────────┘  └──────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### Agent Ecosystem

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **Ingestion Wrangler** | Data validation & transformation | CSV files | Cleaned datasets |
| **Graph Architect** | Entity relationship mapping | Cleaned data | Neo4j relationships |
| **Risk Detective** | Vendor risk analysis | Entity data | Risk scores & profiles |
| **Fraud Pattern Detector** | Anomaly detection | Transaction logs | Suspicious patterns |
| **Predictive Analyst** | Forecasting & trends | Historical data | Predictions & alerts |
| **Niyati Explainer** | Model interpretability | Risk scores | Explanation reports |

---

## 📁 Directory Structure

```
backend/
├── main.py                          # Flask application entry point
├── models.py                        # SQLAlchemy ORM models
├── database.py                      # Database configuration
├── auth.py                          # Authentication & RBAC logic
├── rbac.py                          # Role-based access control utilities
│
├── orchestration/                   # LangGraph Agent Workflows
│   ├── llm_agent.py                # Base agent configuration
│   ├── state.py                    # Workflow state definitions
│   ├── agent_ingestion_wrangler.py # Data ingestion agent
│   ├── agent_graph_architect.py    # Relationship mapping agent
│   ├── agent_risk_detective.py     # Risk analysis agent
│   ├── agent_fraud_detector.py     # Anomaly detection agent
│   ├── agent_predictive_analyst.py # Forecasting agent
│   └── agent_niyati_explainer.py   # Explainability agent
│
├── model/                           # Machine Learning
│   ├── feature_engineering.py      # Feature extraction pipeline
│   └── ebm_training.py             # Explainable Boosting Machine training
│
├── utils/                           # Shared Utilities
│   ├── db_connection.py            # Database connection helpers
│   ├── neo4j_batching.py           # Optimized Neo4j bulk operations
│   ├── csv_validation.py           # CSV schema validation
│   ├── feature_engineering_wrapper.py  # ML pipeline wrapper
│   ├── pii_hashing.py              # Sensitive data encryption
│   ├── change_detection.py         # Delta detection for updates
│   ├── circuit_breaker.py          # Fault tolerance
│   └── workflow_persistence.py     # State serialization
│
├── data/                            # Sample Datasets
│   ├── e_invoices.csv              # Electronic invoices
│   ├── eway_bills.csv              # E-way bill records
│   ├── entity_master.csv           # Entity reference data
│   ├── filing_history.csv          # GST filing history
│   ├── purchase_register.csv       # Purchase transactions
│   ├── returns_summary.csv         # Return summaries
│   └── feature_vectors.csv         # Pre-computed features
│
├── tests/                           # Test Suite
│   ├── test_auth.py
│   ├── test_neo4j_connection.py
│   ├── test_fraud_patterns.py
│   └── integration/
│
├── instance/                        # Instance-specific data (gitignored)
├── requirements.txt                 # Python dependencies
└── Dockerfile                       # Container configuration
```

---

## 🚀 Installation & Setup

### Prerequisites

```bash
# Python 3.10+
python --version

# Neo4j running (local or cloud)
# Default: bolt://localhost:7687

# Virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

### Installation Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cat > .env << EOF
DATABASE_URL=sqlite:///niyati.db
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
SECRET_KEY=your-secret-key-min-32-chars
FLASK_ENV=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000
GROQ_API_KEY=your_groq_api_key
EOF

# 3. Initialize databases
python init_db.py
python check_neo4j_schema.py

# 4. (Optional) Load sample data
python get_sample_gstins.py
python sync_risk_to_neo4j.py

# 5. Start the server
python main.py
# or for production
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Docker Setup

```bash
cd backend
docker build -t niyati-backend:latest .
docker run -p 5000:5000 \
  -e DATABASE_URL=sqlite:///niyati.db \
  -e NEO4J_URI=bolt://host.docker.internal:7687 \
  niyati-backend:latest
```

---

## 🔐 Authentication & Authorization

### JWT Authentication

All protected endpoints require a valid JWT token in the `Authorization` header:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:5000/dashboard
```

### RBAC Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | Full system access, user management | Tax authority officers |
| **Business_Owner** | View own entity data, upload GST docs | Enterprise users |
| **Auditor** | Read-only access to all entities | External auditors |
| **Guest** | Limited public data | Unauthenticated access |

### Access Control Example

```python
@app.route('/admin/sync', methods=['POST'])
@token_required
@admin_required
def sync_data(current_user):
    """Only Admin role can execute this endpoint"""
    # Implementation
    pass
```

---

## 📡 API Endpoints

### Authentication

```
POST /auth/register
  Description: Register new user
  Body: { "email": "user@example.com", "password": "secure_pass", "role": "Business_Owner" }
  Response: { "user_id": 123, "email": "...", "token": "jwt_token" }

POST /auth/login
  Description: Login and get JWT token
  Body: { "email": "user@example.com", "password": "password" }
  Response: { "token": "jwt_token", "user": {...} }

POST /auth/logout
  Description: Invalidate current session
  Headers: { "Authorization": "Bearer token" }
  Response: { "message": "Logged out successfully" }

POST /auth/refresh
  Description: Refresh JWT token
  Headers: { "Authorization": "Bearer token" }
  Response: { "token": "new_jwt_token" }
```

### Dashboard

```
GET /dashboard
  Description: Get RBAC-filtered dashboard data
  Auth: Required
  Params: ?include=vendors,patterns,health_score
  Response:
  {
    "health_score": 78.5,
    "high_risk_count": 12,
    "vendor_risks": [...],
    "fraud_patterns": [...]
  }

GET /dashboard/vendors?risk_level=HIGH_RISK&limit=50
  Description: List vendors with filtering
  Auth: Required
  Response: { "vendors": [...], "total": 150, "page": 1 }

GET /dashboard/patterns?start_date=2026-01-01&end_date=2026-03-20
  Description: Get detected fraud patterns
  Auth: Admin required
  Response: { "patterns": [...], "severity": "HIGH", "count": 8 }
```

### Graph Operations

```
GET /graph/entities?gstin=18AABCY1234H1Z0
  Description: Get entity details and relationships
  Auth: Required
  Response:
  {
    "entity": {...},
    "relationships": {
      "suppliers": [...],
      "customers": [...]
    }
  }

POST /graph/sync
  Description: Sync SQLite data to Neo4j
  Auth: Admin required
  Body: { "entity_type": "all", "force": false }
  Response: { "synced": 1500, "errors": 0, "duration_ms": 3500 }

GET /graph/patterns?type=circular_trade
  Description: Detect specific patterns in graph
  Auth: Admin required
  Response: { "patterns": [...], "severity_distribution": {...} }
```

### Admin Operations

```
POST /admin/export
  Description: Export compliance report
  Auth: Admin required
  Params: ?format=pdf&period=2026-01-01:2026-03-20
  Response: Binary PDF file

POST /admin/health
  Description: System health check
  Auth: Admin required
  Response: { "status": "healthy", "db": "ok", "neo4j": "ok", "agents": "ok" }
```

---

## 🤖 Agent Orchestration

### Workflow Execution

Agents are orchestrated using **LangGraph** state machines:

```python
from orchestration.llm_agent import execute_workflow_sync

# Execute a workflow
result = execute_workflow_sync(
    workflow_name="risk_analysis",
    input_data={
        "entity_gstin": "18AABCY1234H1Z0",
        "transaction_data": transactions
    }
)

print(result["risk_score"])
print(result["explanation"])
```

### Creating a Custom Agent

```python
# orchestration/agent_custom.py
from langgraph.graph import StateGraph
from .state import WorkflowState

def custom_agent_logic(state: WorkflowState):
    # Process state
    state["custom_output"] = "result"
    return state

# Register in graph
graph = StateGraph(WorkflowState)
graph.add_node("custom_agent", custom_agent_logic)
```

---

## 💾 Database Schemas

### SQLite Models

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Admin, Business_Owner
    gstin = db.Column(db.String(15))  # Association for Business_Owner

class RiskPrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gstin = db.Column(db.String(15), nullable=False)
    risk_level = db.Column(db.String(20))  # HIGH_RISK, MEDIUM_RISK, LOW_RISK
    risk_probability = db.Column(db.Float)
    top_driver_1 = db.Column(db.String(255))
    top_driver_1_contribution = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FraudPattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pattern_type = db.Column(db.String(100))  # circular_trade, ghost_invoice
    severity = db.Column(db.String(20))  # HIGH, MEDIUM, LOW
    entities_involved = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Neo4j Graph Schema

```cypher
// Node types
CREATE INDEX entity_gstin FOR (e:Entity) ON (e.gstin);
CREATE INDEX transaction_date FOR (t:Transaction) ON (t.date);

// Relationship types
:SUPPLIER_OF (Entity -> Entity)
:CUSTOMER_OF (Entity -> Entity)
:CONTAINS (Entity -> Transaction)
:FLAGGED_BY (Transaction -> FraudPattern)
:EXHIBITS_RISK (Entity -> RiskProfile)
```

---

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Integration Tests

```bash
# Test Neo4j connection
python test_neo4j_connection.py

# Test fraud patterns
python test_fraud_patterns.py

# Full integration suite
pytest tests/integration/ -v
```

### Test Example

```python
# tests/test_auth.py
import pytest
from main import app
from database import db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_login_success(client):
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in response.json
```

---

## 🛡️ Security Best Practices

### Environment Variables
```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use strong SECRET_KEY (min 32 chars)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### PII Protection
```python
from utils.pii_hashing import hash_sensitive_data

# Hash PAN, Aadhaar, etc.
hashed_pan = hash_sensitive_data(pan_number)
```

### SQL Injection Prevention
```python
# Use parameterized queries (ORM handles this)
users = User.query.filter_by(email=email).first()

# NOT: User.query.filter(f"email = '{email}'").first()
```

### Rate Limiting (Recommended)
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    pass
```

---

## 🚀 Performance Optimization

### Database Indexing
```python
# Already configured in models.py
db.Index('idx_user_email', User.email)
db.Index('idx_risk_gstin', RiskPrediction.gstin)
```

### Neo4j Batching
```python
from utils.neo4j_batching import batch_create_relationships

# Create 10,000 relationships efficiently
relationships = [...]
batch_create_relationships(relationships, batch_size=1000)
```

### Caching Strategy
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_entity_risk(gstin: str):
    # Expensive Neo4j query
    return risk_profile
```

---

## 📊 Monitoring & Logging

### Application Logging

```python
import logging

logger = logging.getLogger(__name__)

@app.route('/dashboard')
def dashboard():
    logger.info(f"Dashboard accessed by user: {user_id}")
    try:
        data = fetch_dashboard_data()
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        raise
```

### Health Check Endpoint

```bash
curl http://localhost:5000/admin/health
Response:
{
  "status": "healthy",
  "timestamp": "2026-03-20T10:30:00Z",
  "components": {
    "sqlite": "connected",
    "neo4j": "connected",
    "backend": "running"
  }
}
```

---

## 🔄 Deployment Checklist

- [ ] Set production environment variables
- [ ] Configure CORS origins correctly
- [ ] Enable HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure Neo4j authentication
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts
- [ ] Review security rules
- [ ] Perform load testing
- [ ] Document API with Swagger/OpenAPI

### Production Deployment

```bash
# Use gunicorn with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  main:app

# Or with systemd service
sudo systemctl start niyati-backend
sudo systemctl status niyati-backend
```

---

## 🤝 Development Workflow

### Adding a New Endpoint

1. Create handler in appropriate blueprint
2. Add authentication decorators
3. Document in docstring (API spec)
4. Write unit tests
5. Update API documentation
6. Commit with descriptive message

```python
@app.route('/api/new-endpoint', methods=['GET'])
@token_required
def new_endpoint(current_user):
    """
    Description of endpoint.
    
    Args:
        current_user: Authenticated user object
        
    Returns:
        dict: Response with data and status
    """
    try:
        result = process_request(current_user)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Neo4j Python Driver](https://neo4j.com/docs/api/python-driver/current/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/)
- [JWT Authentication](https://tools.ietf.org/html/rfc7519)

---

## 🐛 Troubleshooting

### Neo4j Connection Failed

```bash
# Check Neo4j is running
neo4j status

# Verify credentials
python -c "from neo4j import GraphDatabase; GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))"
```

### Memory Issues with Large CSV Files

```python
# Use chunked processing
df = pd.read_csv('large_file.csv', chunksize=10000)
for chunk in df:
    process_chunk(chunk)
```

### SQLite Database Locked

```bash
# Remove lock file
rm niyati.db-journal

# Use connection pooling for concurrent access
```

---

## 📄 License

MIT License - See root [LICENSE](../LICENSE) file

---

## 🎓 Hackathon Context

Niyati was developed as an innovative solution for the **GST Compliance & Risk Intelligence Hackathon**, showcasing advanced applications of:
- Multi-agent AI orchestration with LangGraph
- Explainable machine learning for regulatory compliance
- Knowledge graphs for relationship discovery
- Enterprise-grade authentication and access control
- Real-time risk analytics and fraud detection

---

<div align="center">

**For detailed component documentation, see individual files with docstrings**

[⬆ back to the backend](#niyati-backend-service)

</div>
