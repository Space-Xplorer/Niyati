# Project Niyati - Setup Guide

This guide will help you set up and run the Project Niyati application with proper frontend-backend connection and session persistence.

## Prerequisites

- Python 3.8+
- Node.js 18+
- Neo4j (via Docker or AuraDB)

## Backend Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

The `.env` file is already configured. Key settings:

- `DATABASE_URL`: SQLite database (file-based)
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Neo4j connection
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `LLM_PROVIDER`, `LLM_API_KEY`: LLM configuration

**Important**: The environment variable is `JWT_SECRET_KEY` (not `JWT_SECRET`)

### 3. Initialize Database

```bash
cd backend
python init_db.py
```

### 4. Start Backend Server

You can run either Flask or FastAPI:

**Option A: Flask (Port 5000)**
```bash
cd backend
python start_backend.py flask
```

**Option B: FastAPI (Port 8000)**
```bash
cd backend
python start_backend.py fastapi
```

Or directly:
```bash
# Flask
python app.py

# FastAPI
uvicorn app_fastapi:app --reload --port 8000
```

## Frontend Setup

### 1. Install Node Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

A `.env.local` file has been created with the default configuration:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
```

**Important**: Change this to match your backend:
- Flask: `http://127.0.0.1:5000`
- FastAPI: `http://127.0.0.1:8000`

### 3. Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Neo4j Setup

### Option A: Docker (Local Development)

```bash
docker-compose up -d
```

This starts Neo4j on:
- HTTP: `http://localhost:7474`
- Bolt: `bolt://localhost:7687`
- Credentials: `neo4j` / `niyati_password`

### Option B: Neo4j AuraDB (Cloud)

Update `.env` with your AuraDB credentials:
```env
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

## Key Features Fixed

### 1. Session Persistence
- JWT tokens are validated on page load
- Expired tokens automatically log users out
- Token expiration is checked before API calls

### 2. Frontend-Backend Connection
- Centralized API configuration via `.env.local`
- Unified API client in `frontend/src/lib/api.ts`
- Proper error handling for 401 (unauthorized) responses

### 3. CORS Configuration
- Backend allows requests from `localhost:3000` (frontend)
- Credentials support enabled
- Proper headers configured

### 4. Environment Variables
- `JWT_SECRET_KEY` naming consistency across all files
- Frontend `.env.local` for API URL configuration
- Backend `.env` with all required variables

## Testing the Setup

### 1. Test Backend Health

**Flask:**
```bash
curl http://127.0.0.1:5000/api/health
```

**FastAPI:**
```bash
curl http://127.0.0.1:8000/health
```

### 2. Test User Registration

```bash
curl -X POST http://127.0.0.1:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","role":"Admin"}'
```

### 3. Test User Login

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 4. Test Frontend

1. Open `http://localhost:3000`
2. Click "Sign up" and create an account
3. Login with your credentials
4. You should be redirected to the dashboard

## Common Issues

### Issue: "Token is invalid" or "Token has expired"

**Solution**: The token expires after 24 hours. Simply log out and log back in.

### Issue: "CORS error" in browser console

**Solution**: 
1. Verify backend is running
2. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local` matches your backend
3. Ensure CORS is properly configured in backend

### Issue: "Connection refused" when accessing dashboard

**Solution**:
1. Verify backend is running on the correct port
2. Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
3. Test backend health endpoint directly

### Issue: Frontend shows "No data available"

**Solution**:
1. Initialize the database: `python backend/init_db.py`
2. Upload CSV data via the `/sync` endpoint or upload page
3. Ensure your user has proper RBAC permissions

## Architecture

### Backend Endpoints

**Flask (Port 5000):**
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User authentication
- `GET /dashboard` - Dashboard data (RBAC filtered)
- `GET /api/health` - Health check

**FastAPI (Port 8000):**
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /dashboard` - Dashboard data (RBAC filtered)
- `POST /sync` - Upload CSV files and trigger workflow
- `POST /pre-audit` - On-demand fraud check
- `GET /graph` - Graph visualization data
- `GET /risk/{gstin}` - Detailed risk analysis
- `GET /logs/stream` - SSE for real-time agent logs
- `GET /health` - Health check

### Frontend Routes

- `/` - Landing page
- `/login` - Login page
- `/signup` - Registration page
- `/dashboard` - Main dashboard (protected)
- `/graph` - Graph visualization (protected)
- `/upload` - CSV upload page (protected)

## Security Notes

1. **JWT Tokens**: Stored in localStorage (consider HttpOnly cookies for production)
2. **Token Expiration**: 24 hours (configurable in `auth.py`)
3. **CORS**: Restricted to localhost in development (configure for production)
4. **Secrets**: Change `JWT_SECRET_KEY` in production
5. **HTTPS**: Use HTTPS in production for secure token transmission

## Next Steps

1. Configure production environment variables
2. Set up proper database backups
3. Implement token refresh mechanism
4. Add rate limiting
5. Configure production CORS origins
6. Set up monitoring and logging
7. Implement email notifications for high-risk alerts

## Support

For issues or questions, refer to the documentation in the `docs/` folder.
