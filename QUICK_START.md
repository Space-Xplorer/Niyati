# Quick Start Guide - Project Niyati

Get up and running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Node.js 18+ installed
- Neo4j running (Docker or AuraDB)

## Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start Flask backend (port 5000)
python start_backend.py flask

# OR start FastAPI backend (port 8000)
# python start_backend.py fastapi
```

Backend will be running at:
- Flask: `http://127.0.0.1:5000`
- FastAPI: `http://127.0.0.1:8000`

## Step 2: Frontend Setup (2 minutes)

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be running at: `http://localhost:3000`

## Step 3: Test the Application (1 minute)

1. Open browser to `http://localhost:3000`
2. Click "Sign up" to create an account
3. Fill in:
   - Email: `test@example.com`
   - Password: `password123`
   - Check "Register as Admin" for testing
4. Click "Sign Up"
5. Login with your credentials
6. You'll be redirected to the dashboard!

## Configuration

### Backend Environment Variables

The `.env` file is already configured. Key settings:

```env
DATABASE_URL=sqlite:///niyati.db
JWT_SECRET_KEY=<your-secret-key>
NEO4J_URI=<your-neo4j-uri>
LLM_PROVIDER=groq
LLM_API_KEY=<your-api-key>
```

### Frontend Environment Variables

The `.env.local` file is already configured:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
```

**Important**: If using FastAPI, change to:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Troubleshooting

### "Connection refused" error

**Solution**: Make sure backend is running on the correct port. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local` matches your backend.

### "Token is invalid" error

**Solution**: Logout and login again. Tokens expire after 24 hours.

### "No data available" on dashboard

**Solution**: You need to upload CSV data first. The database is empty on first run.

### CORS errors in browser console

**Solution**: 
1. Verify backend is running
2. Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
3. Restart both frontend and backend

## What's Fixed

✅ JWT secret key consistency  
✅ Frontend-backend connection  
✅ Session persistence  
✅ Token expiration validation  
✅ Automatic logout on expired tokens  
✅ CORS configuration  
✅ Centralized API client  
✅ Environment variable management  

## Next Steps

1. Upload CSV data via the Upload page (if using FastAPI)
2. Explore the dashboard to see risk analysis
3. View the transaction graph
4. Check out the agent logs for real-time updates

## Need Help?

- Full setup guide: See `README_SETUP.md`
- All fixes applied: See `FIXES_APPLIED.md`
- Original README: See `README.md`

## Quick Commands Reference

```bash
# Backend
python backend/start_backend.py flask     # Start Flask
python backend/start_backend.py fastapi   # Start FastAPI
python backend/init_db.py                 # Initialize database

# Frontend
npm run dev                               # Start dev server
npm run build                             # Build for production
npm run lint                              # Run linter

# Docker (Neo4j)
docker-compose up -d                      # Start Neo4j
docker-compose down                       # Stop Neo4j
```

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │  Next.js on port 3000
│   (React)       │  
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│   Backend       │  Flask (5000) or FastAPI (8000)
│   (Python)      │  
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│SQLite│  │ Neo4j │  Databases
└──────┘  └───────┘
```

## Default Credentials

After signup, use your own credentials. For testing:

- Email: `test@example.com`
- Password: `password123`
- Role: Admin (for full access)

---

**Ready to build!** 🚀

For detailed documentation, see `README_SETUP.md`
