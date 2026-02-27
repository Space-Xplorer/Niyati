# Backend Endpoints Comparison

## Flask Backend (Port 5000) - Basic Features

### Authentication Endpoints ✅
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - Alias for signup

### Dashboard Endpoints ✅
- `GET /dashboard` - Dashboard data with RBAC filtering
- `GET /api/health` - Health check

### Graph Endpoint ⚠️
- `GET /graph` - Returns empty graph (Neo4j not implemented in Flask)

### Admin Endpoints ✅
- `GET /api/admin/data` - Admin-only data (requires Admin role)

### Not Available in Flask ❌
- `POST /sync` - CSV upload and workflow (FastAPI only)
- `POST /pre-audit` - On-demand fraud check (FastAPI only)
- `GET /risk/{gstin}` - Detailed risk with SHAP plots (FastAPI only)
- `GET /logs/stream` - SSE real-time logs (FastAPI only)

---

## FastAPI Backend (Port 8000) - Full Features

### Authentication Endpoints ✅
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Dashboard Endpoints ✅
- `GET /dashboard` - Dashboard data with RBAC filtering
- `GET /health` - Health check

### Workflow Endpoints ✅
- `POST /sync` - Upload 6 CSV files and trigger full workflow
- `POST /pre-audit` - On-demand fraud check for specific GSTIN

### Graph Endpoints ✅
- `GET /graph` - Graph visualization data from Neo4j

### Risk Analysis Endpoints ✅
- `GET /risk/{gstin}` - Detailed risk data with SHAP plots

### Real-Time Endpoints ✅
- `GET /logs/stream` - Server-Sent Events for agent progress

---

## Recommendation

### Use Flask (Port 5000) if:
- You want quick testing of authentication and dashboard
- You don't need CSV upload workflow
- You don't need graph visualization
- You're just testing the UI

### Use FastAPI (Port 8000) if:
- You need full workflow with CSV upload
- You want graph visualization from Neo4j
- You need real-time agent logs via SSE
- You want detailed risk analysis with SHAP plots
- You're doing production deployment

---

## Switching Between Backends

### Frontend Configuration

Edit `frontend/.env.local`:

**For Flask:**
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
```

**For FastAPI:**
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Starting Backend

**Flask:**
```bash
cd backend
python start_backend.py flask
```

**FastAPI:**
```bash
cd backend
python start_backend.py fastapi
```

---

## Current Setup

✅ Flask is running on port 5000  
✅ Frontend is configured to use Flask  
✅ Dashboard works with test data  
✅ Graph endpoint returns empty data (expected for Flask)  

**To get full graph visualization:**
1. Stop Flask backend
2. Start FastAPI backend: `python start_backend.py fastapi`
3. Update `frontend/.env.local` to port 8000
4. Restart frontend: `npm run dev`
5. Upload CSV data or ensure Neo4j has data

---

## Endpoint Details

### Flask `/graph` Response
```json
{
  "nodes": [],
  "edges": [],
  "message": "Graph visualization requires Neo4j. Please use FastAPI backend or upload data first."
}
```

### FastAPI `/graph` Response
```json
{
  "nodes": [
    {
      "id": "29AABCT1332L1Z5",
      "label": "Taxpayer",
      "name": "Tech Solutions Pvt Ltd",
      "risk_level": "HIGH_RISK"
    }
  ],
  "edges": [
    {
      "source": "29AABCT1332L1Z5",
      "target": "27AABCU9603R1ZM",
      "type": "TRANSACTION"
    }
  ]
}
```

---

## Summary

- **Flask**: Lightweight, quick testing, basic features
- **FastAPI**: Full-featured, production-ready, all endpoints
- **Current**: Flask is running, graph page will show "No data available" (expected)
- **Solution**: Either accept empty graph or switch to FastAPI for full features
