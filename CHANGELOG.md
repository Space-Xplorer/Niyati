# Changelog

All notable changes to Project Niyati are documented in this file.

## [Unreleased] - 2026-02-27

### Changed

#### Backend Consolidation
- **Consolidated `app.py` and `app_fastapi.py` into single `main.py` file**
  - Removed redundant Flask application (`app.py`)
  - Renamed `app_fastapi.py` to `main.py` as the single entry point
  - Standardized JWT environment variable from `JWT_SECRET_KEY` to `JWT_SECRET`
  - Updated all documentation to reference `main.py`
  - See `backend/CONSOLIDATION_NOTES.md` for details

#### Database Migration
- **Migrated from PostgreSQL to SQLite**
  - Changed `DATABASE_URL` to use SQLite file-based database
  - Removed PostgreSQL-specific imports from models
  - Updated docker-compose.yml to remove PostgreSQL service
  - Added SQLite database files to .gitignore
  - See `backend/MIGRATION_TO_SQLITE.md` for details

#### Security
- **Generated secure JWT secret key**
  - Created cryptographically secure 64-byte token
  - Updated `.env` file with new JWT_SECRET

#### Documentation
- **Created comprehensive README files**
  - Main `README.md` - Project overview, features, setup guide
  - `backend/README.md` - Complete API documentation with all endpoints
  - `frontend/README.md` - Frontend documentation with routing and components
  - All documentation updated to reflect SQLite and main.py changes

#### Cleanup
- **Removed test files and old documentation**
  - Deleted test files from backend root directory
  - Removed test result markdown files
  - Removed old documentation files (API_DOCUMENTATION.md, QUICKSTART.md, SETUP.md)
  - Cleaned up project structure

### Added

- `backend/main.py` - Unified FastAPI application
- `backend/CONSOLIDATION_NOTES.md` - Backend consolidation documentation
- `backend/MIGRATION_TO_SQLITE.md` - Database migration guide
- `CHANGELOG.md` - This file
- Comprehensive README files for project, backend, and frontend

### Removed

- `backend/app.py` - Redundant Flask application
- `backend/app_fastapi.py` - Renamed to main.py
- `backend/test_*.py` - Test files from root directory
- `backend/API_DOCUMENTATION.md` - Replaced by backend/README.md
- `backend/QUICKSTART.md` - Merged into README.md
- `SETUP.md` - Merged into README.md
- Test result markdown files

### Fixed

- Authentication context now excludes home page (`/`) from redirect
- Landing page is now fully public and accessible without authentication
- Signup page now sends correct role values (`Admin` or `Business_Owner`)

## Project Status

### Completed Features

✅ Five intelligent agents (Ingestion Wrangler, Graph Architect, Risk Detective, Predictive Analyst, Niyati Explainer)  
✅ LangGraph multi-agent orchestration  
✅ Neo4j knowledge graph integration  
✅ SQLite database for relational data  
✅ JWT authentication with RBAC  
✅ FastAPI REST API with all endpoints  
✅ Next.js frontend with public landing page  
✅ Real-time SSE log streaming  
✅ Comprehensive documentation  

### In Progress

🔄 CSV file upload workflow implementation  
🔄 Dashboard data visualization  
🔄 Graph visualization with React Force Graph  
🔄 EBM model training and inference  

### Planned

📋 Email notifications for HIGH_RISK detections  
📋 Vendor risk analysis  
📋 Production deployment configuration  
📋 CI/CD pipeline setup  

## Getting Started

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd niyati
```

2. **Set up backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python main.py
```

3. **Set up frontend**
```bash
cd frontend
npm install
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
