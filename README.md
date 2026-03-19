# Niyati - AI-Powered GST Compliance & Risk Intelligence Platform

![Niyati](https://img.shields.io/badge/Niyati-v1.0.0-blue.svg)
![Status](https://img.shields.io/badge/Status-Active%20Development-green.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

## 🎯 Overview

**Niyati** is an enterprise-grade AI-powered platform designed to transform GST (Goods and Services Tax) compliance and risk management. Leveraging advanced machine learning, knowledge graphs, and multi-agent AI orchestration, Niyati provides real-time risk detection, fraud pattern analysis, and actionable compliance insights for tax authorities and enterprises.

### Key Capabilities

- **🤖 Multi-Agent AI Orchestration**: LangGraph-based autonomous agents for data ingestion, risk analysis, fraud detection, and compliance explanations
- **📊 Advanced Risk Analytics**: Explainable ML models (EBM) for vendor risk scoring and ITC (Input Tax Credit) protection
- **🔗 Knowledge Graph Integration**: Neo4j-powered relationship mapping for comprehensive GST entity analysis
- **🔐 Enterprise Security**: Role-Based Access Control (RBAC), JWT authentication, and PII hashing
- **📱 Modern UI/UX**: Next.js React frontend with real-time dashboard and interactive data visualization
- **⚡ Scalable Architecture**: Cloud-ready deployment (Railway, Render, Docker support)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (Backend)
- **Node.js 18+** (Frontend)
- **Neo4j 5.0+** (Graph Database)
- **Docker & Docker Compose** (Optional - for containerized deployment)
- **.env configuration** (See [Configuration](#-configuration) section)

### Installation

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd Niyati
```

#### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Configure database URLs and secrets

# Initialize database
python init_db.py
python check_neo4j_schema.py

# Start the backend
python main.py
```

#### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

### Docker Deployment

```bash
docker-compose up -d
```

---

## 📋 Project Structure

```
Niyati/
├── backend/                      # Flask/FastAPI backend
│   ├── orchestration/           # LangGraph multi-agent workflows
│   ├── utils/                   # Shared utilities and helpers
│   ├── model/                   # ML model training and inference
│   ├── data/                    # Sample datasets (CSV)
│   ├── main.py                  # Application entry point
│   ├── models.py                # SQLAlchemy ORM models
│   ├── database.py              # Database configuration
│   └── requirements.txt          # Python dependencies
│
├── frontend/                     # Next.js React application
│   ├── src/
│   │   ├── app/                 # Next.js app routes
│   │   ├── components/          # Reusable React components
│   │   ├── context/             # React context for state management
│   │   └── lib/                 # Utility functions and API client
│   └── package.json             # Node.js dependencies
│
├── portal/                       # Additional admin portal
├── docker-compose.yml           # Container orchestration
├── LICENSE                      # MIT License
└── README.md                    # This file
```

---

## 🏗️ Architecture

### Multi-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer (Next.js)                 │
│              React Components + Tailwind CSS               │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              API Gateway & Authentication                    │
│         Flask/FastAPI + JWT + RBAC Middleware              │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
    ┌────▼────┐      ┌─────▼──────┐      ┌──▼────────┐
    │ SQLite  │      │    Neo4j    │      │  LangGraph│
    │ (Auth & │      │ (Knowledge  │      │ (Multi-  │
    │ Records)│      │  Graph)     │      │  Agent)  │
    └─────────┘      └─────────────┘      └──────────┘
         │                 │                  │
         └─────────────────┼──────────────────┘
                           │
         ┌─────────────────▼──────────────────┐
         │   ML Models & Feature Engineering   │
         │  (Explainable Boosting Machines)   │
         └────────────────────────────────────┘
```

### Key Components

**Backend Services**:
- **Auth Service**: JWT-based authentication with RBAC
- **Risk Detective Agent**: Analyzes vendor risk using ML models
- **Fraud Pattern Agent**: Detects suspicious transaction patterns
- **Graph Architect**: Manages entity relationships in Neo4j
- **Predictive Analyst**: Generates risk forecasts
- **Niyati Explainer**: Provides explainable AI insights

**Frontend Services**:
- **Dashboard**: Admin and business owner analytics
- **Graph Visualization**: Interactive entity relationship explorer
- **Authentication**: Login/signup with session management
- **Data Upload**: CSV import for entity and transaction data

---

## 🔐 Configuration

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///niyati.db
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# JWT & Security
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# LLM Configuration (for AI agents)
GROQ_API_KEY=your-groq-api-key
LANGCHAIN_API_KEY=your-langchain-api-key

# Application Settings
FLASK_ENV=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000

# Feature Flags
ORCHESTRATION_ENABLED=true
CIRCUIT_BREAKER_ENABLED=true
```

---

## 📚 API Documentation

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | User login with email and password |
| `/auth/register` | POST | New user registration |
| `/auth/logout` | POST | User logout |
| `/auth/refresh` | POST | Refresh JWT token |

### Dashboard Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/dashboard` | GET | Required | Gets RBAC-filtered summary data |
| `/dashboard/vendors` | GET | Required | Lists vendors with risk scores |
| `/dashboard/patterns` | GET | Admin | Shows detected fraud patterns |
| `/graph/entities` | GET | Required | Fetches entity relationships |

### Admin Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/admin/sync` | POST | Admin | Syncs data to Neo4j |
| `/admin/export` | GET | Admin | Exports compliance reports |

For detailed API documentation, see [backend/README.md](backend/README.md).

---

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest tests/ -v

# Run frontend tests
cd frontend
npm test

# Integration tests
pytest tests/integration/ -v
```

---

## 📦 Deployment

### Cloud Deployment Options

#### Railway
```bash
railway up
```

#### Render
See `render.yaml` for configuration.

#### Docker
```bash
docker build -t niyati:latest .
docker run -p 5000:5000 -p 3000:3000 niyati:latest
```

### Environment-Specific Configuration

**Development**:
```bash
FLASK_ENV=development
DEBUG=true
```

**Production**:
```bash
FLASK_ENV=production
DEBUG=false
WORKERS=4
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** changes: `git commit -m 'Add your feature'`
4. **Push** to branch: `git push origin feature/your-feature`
5. **Submit** a Pull Request with description

### Code Standards

- Backend: Follow PEP 8 style guide
- Frontend: ESLint configuration provided
- All code requires tests
- Documentation updates required for new features

---

## 📖 Documentation

- [Backend Documentation](backend/README.md) - API, database, agent architecture
- [Frontend Documentation](frontend/README.md) - Component library, state management
- [Architecture Decisions](docs/ARCHITECTURE.md)
- [API References](docs/API.md)

---

## 🐛 Known Issues & Limitations

- Neo4j relationship sync requires manual trigger via `/admin/sync`
- Real-time updates require polling (WebSocket support planned for v2.0)
- Maximum CSV upload size: 100MB

---

## 📊 Project Statistics

- **Backend**: Python 3.10+, FastAPI/Flask, 15+ agents
- **Frontend**: React 19, Next.js 16, TypeScript
- **Databases**: Neo4j 5, SQLite3
- **ML Framework**: scikit-learn, interpret-ml (EBM)
- **Deployment**: Docker, Railway, Render ready

---

## 📜 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

---

## ✨ Credits

**Niyati** was created as an innovative solution for the **GST Compliance Hackathon**, demonstrating advanced AI/ML capabilities for tax authority risk management and enterprise compliance.

**Development Team**: Patnala Maheshwar and Spoorthy Boga

**Technologies**: Python, React, Neo4j, LangGraph, Machine Learning

---

## 📞 Support & Contact

For issues, feature requests, or inquiries:
- **Issues**: Create a GitHub issue with detailed description
- **Email**: maheshwarpatn@gmail.com

---

## 🗺️ Roadmap

- **v1.1** (Q2 2026): WebSocket real-time updates, advanced reporting
- **v1.2** (Q3 2026): Mobile app, predictive compliance alerts
- **v2.0** (Q4 2026): Multi-jurisdiction support, blockchain integration

---

<div align="center">

**Made with ❤️ by the Niyati Team**

[⬆ back to top](#niyati---ai-powered-gst-compliance--risk-intelligence-platform)

</div>
