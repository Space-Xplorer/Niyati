# Project Niyati

**Real-time GST Intelligence & Fraud Detection Platform**

Project Niyati is a comprehensive fraud detection system designed as a "Shadow Mirror" of India's GST Network. It uses Knowledge Graph analysis, Explainable Boosting Machines (EBM), and multi-agent orchestration to detect circular trading patterns, ghost invoices, and Input Tax Credit (ITC) fraud.

## Features

### 🤖 Five Intelligent Agents

1. **Ingestion Wrangler** - Validates and cleans GST transaction data from six CSV sources with automated feature engineering
2. **Graph Architect** - Builds a comprehensive Neo4j knowledge graph connecting taxpayers, invoices, and e-way bills
3. **Risk Detective** - Detects circular trading patterns, ghost invoices, and spider web networks through graph analysis
4. **Predictive Analyst** - Uses Explainable Boosting Machines to predict fraud risk with transparent feature contributions
5. **Niyati Explainer** - Generates plain-language audit narratives using LLMs for non-technical stakeholders

### 🔍 Detection Capabilities

- **Circular Trading**: Identifies transaction loops (A → B → C → A) to detect ITC fraud schemes
- **Ghost Invoices**: Flags high-value invoices without corresponding e-way bills
- **Spider Web Networks**: Discovers clusters of entities sharing contact information to uncover shell companies

### 🛡️ Security & Compliance

- **Role-Based Access Control (RBAC)**: Admins see everything, business owners see only their data
- **PII Protection**: All sensitive data is hashed using SHA-256 before storage
- **JWT Authentication**: Secure token-based authentication with 24-hour expiry

### 📊 Explainable AI

- **Transparent Risk Scores**: Understand exactly why an entity is flagged
- **Feature Contributions**: Visual shape plots showing how each feature impacts risk
- **Plain-Language Narratives**: LLM-generated audit reports for non-technical stakeholders

### ⚡ Real-Time Observability

- **Server-Sent Events (SSE)**: Watch agent execution in real-time
- **LangGraph Orchestration**: Coordinated multi-agent workflow with error recovery
- **Circuit Breaker Pattern**: Graceful fallback when LLM APIs fail

## Tech Stack

### Backend
- **Python 3.9+** with Flask/FastAPI
- **SQLite** for relational data storage (file-based)
- **Neo4j** for knowledge graph
- **LangGraph** for multi-agent orchestration
- **Explainable Boosting Machine (EBM)** for ML predictions
- **Groq/OpenAI** for LLM-powered explanations

### Frontend
- **Next.js 15** with App Router
- **React 19** with TypeScript
- **TailwindCSS v4** for styling
- **React Force Graph** for network visualization

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Neo4j 5+ (or use Docker)
- Docker (optional, for Neo4j container)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd niyati
```

2. **Set up the backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DATABASE_URL` - SQLite database file path (default: sqlite:///niyati.db)
- `NEO4J_URI` - Neo4j bolt connection URI
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `LLM_PROVIDER` - Either "groq" or "openai"
- `LLM_API_KEY` - API key for your LLM provider
- `JWT_SECRET` - Secret key for JWT token generation

4. **Initialize the database**
```bash
python init_db.py
```

5. **Set up the frontend**
```bash
cd ../frontend
npm install
```

6. **Configure frontend environment**
```bash
cp .env.local.example .env.local
# Edit .env.local with your backend URL
```

Required frontend environment variables:
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://127.0.0.1:5000)

### Running the Application

#### Option 1: Manual Startup

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app_fastapi.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

#### Option 2: Docker Compose

```bash
docker-compose up
```

This will start:
- Neo4j on port 7687 (Bolt) and 7474 (Browser)
- Backend API on port 8000
- Frontend on port 3000

Note: SQLite database is file-based and doesn't require a container.

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474

## Project Structure

```
niyati/
├── backend/                      # Python backend
│   ├── orchestration/            # LangGraph multi-agent workflow
│   │   ├── agent_ingestion_wrangler.py
│   │   ├── agent_graph_architect.py
│   │   ├── agent_risk_detective.py
│   │   ├── agent_predictive_analyst.py
│   │   ├── agent_niyati_explainer.py
│   │   └── llm_agent.py          # LangGraph workflow orchestration
│   ├── model/                    # ML models
│   │   ├── daksha_ebm.pkl        # Trained EBM model
│   │   ├── ebm_training.py       # Model training script
│   │   └── feature_engineering.py
│   ├── utils/                    # Utility modules
│   │   ├── pii_hashing.py        # PII protection
│   │   ├── circuit_breaker.py    # Resilience patterns
│   │   └── neo4j_batching.py     # Graph optimization
│   ├── tests/                    # Test suites
│   ├── data/                     # Sample CSV files
│   ├── app.py                    # Flask application
│   ├── app_fastapi.py            # FastAPI application (main)
│   ├── auth.py                   # Authentication & JWT
│   ├── rbac.py                   # Role-based access control
│   ├── database.py               # SQLAlchemy setup
│   ├── models.py                 # Database models
│   └── requirements.txt          # Python dependencies
│
├── frontend/                     # Next.js frontend
│   ├── src/
│   │   ├── app/                  # Next.js App Router
│   │   │   ├── page.tsx          # Landing page (public)
│   │   │   ├── login/            # Login page
│   │   │   ├── signup/           # Signup page
│   │   │   ├── dashboard/        # Trust Dashboard (protected)
│   │   │   ├── graph/            # Graph visualization (protected)
│   │   │   └── upload/           # CSV upload (protected)
│   │   ├── components/           # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── HealthGauge.tsx
│   │   │   ├── VendorRiskTable.tsx
│   │   │   └── ShapePlots.tsx
│   │   └── context/              # React context providers
│   │       └── AuthContext.tsx   # Authentication state
│   ├── package.json
│   └── tsconfig.json
│
├── docker-compose.yml            # Docker services configuration
├── LICENSE
└── README.md                     # This file
```

## Usage

### 1. User Registration

Navigate to http://localhost:3000/signup and create an account:
- **Role**: Choose "Admin" or "Business Owner"
- **GSTIN**: Required for Business Owners (15-character GST ID).  The number must already be present in the `entity_master` table; signup will fail otherwise.

### 2. Upload CSV Files

After logging in, navigate to `/upload` and upload six CSV files:
1. `e_invoices.csv` - Electronic invoices
2. `eway_bills.csv` - E-way bill records
3. `entity_master.csv` - Taxpayer master data
4. `filing_history.csv` - GST filing history
5. `purchase_register.csv` - Purchase transactions
6. `returns_summary.csv` - GSTR-1 and GSTR-3B summaries

### 3. View Dashboard

Navigate to `/dashboard` to see:
- Health score (0-100)
- Risk level (LOW/MEDIUM/HIGH)
- Top 3 fraud drivers with contributions
- Vendor risk table
- Detected patterns summary

### 4. Explore Knowledge Graph

Navigate to `/graph` to visualize:
- Taxpayer nodes colored by risk level
- Transaction relationships
- Circular trading loops (pulsing red nodes)
- Spider web clusters

### 5. Pre-Audit Check

Use the API endpoint `POST /pre-audit` with a GSTIN to trigger on-demand fraud analysis for a specific entity.

## API Documentation

See [backend/README.md](backend/README.md) for complete API documentation including:
- All endpoints with request/response schemas
- Authentication requirements
- RBAC rules
- Error codes

## Frontend Documentation

See [frontend/README.md](frontend/README.md) for frontend documentation including:
- Routing structure
- Component library
- State management
- Styling guidelines

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

Test coverage includes:
- Unit tests for all 5 agents
- Integration tests for LangGraph workflow
- RBAC permission tests
- PII hashing tests

### Frontend Tests

```bash
cd frontend
npm test
```

## Performance

- **Graph Ingestion**: <30 seconds for 1,500 invoices
- **Full Workflow**: <60 seconds for datasets up to 1,500 records
- **Dashboard Load**: <3 seconds
- **Concurrent Requests**: Handles 10+ concurrent pre-audit requests

## Security

- All passwords are hashed using bcrypt
- PII data (phone, email) is hashed using SHA-256
- JWT tokens expire after 24 hours
- RBAC enforced at both API and database levels
- SQL injection protection via SQLAlchemy ORM
- CORS configured for production deployment

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

- Built with LangGraph for multi-agent orchestration
- Uses InterpretML's Explainable Boosting Machine
- Powered by Neo4j for knowledge graph analysis
- UI components inspired by Shadcn/UI
