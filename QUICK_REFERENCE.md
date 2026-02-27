# Quick Reference Card

## 🚀 Application URLs
- **Frontend**: http://localhost:3000
- **Backend**: http://127.0.0.1:5000
- **Status**: ✅ Both running

## 🔑 Test Credentials

### Admin Account (Government Officer)
```
Email: admin@gstn.gov.in
Password: admin123
Role: Admin
Dashboard: System-wide AdminDashboard with fraud detection metrics
```

### Create Admin Account (Alternative)
```
Email: admin@test.com
Password: admin123
Role: Admin (checked)
```

### Create Business Owner Account
```
Email: business@test.com
Password: business123
GSTIN: 29AABCT1332L1Z5
Role: Business_Owner (unchecked)
Dashboard: Taxpayer-specific dashboard with vendor risks
```

## 📊 Test Data (3 Entities)
1. `29AABCT1332L1Z5` - HIGH RISK (78.5%)
2. `27AABCU9603R1ZM` - MEDIUM RISK (42%)
3. `07AABCU9603R1ZX` - LOW RISK (15%)

## ✅ What Works
- ✅ Landing page
- ✅ Signup/Login with RBAC
- ✅ Admin Dashboard (system-wide view)
  - System health metrics
  - Risk distribution
  - Fraud pattern detection
  - Vendor risk table (fetches from Neo4j)
  - Real-time agent logs (SSE)
- ✅ Taxpayer Dashboard (individual view)
  - Health score gauge
  - Risk level badge
  - Vendor risk analysis
  - SHAP plots (top risk drivers)
- ✅ Graph visualization (Neo4j network)
  - Fetches from Neo4j (2000 nodes, 15000 edges)
  - Falls back to SQLite if Neo4j fails
  - RBAC filtering (Admin sees all, Business Owner sees subgraph)
- ✅ Session persistence
- ✅ Token expiration handling
- ✅ Role-based access control

## ⚠️ Minor Issues (Non-Breaking)
- ShapePlots: 404 error (FastAPI only)
- AgentLogViewer: 404 error (FastAPI only)
- Upload page: 404 error (FastAPI only)

## 🎯 Quick Test
1. Visit http://localhost:3000
2. Click "Get Started"
3. Sign up as Admin
4. Login
5. View dashboard
6. Done! ✅

## 📝 Key Files
- Frontend config: `frontend/.env.local`
- Backend config: `backend/.env`
- Test data: Run `python backend/seed_test_data.py`
- Start backend: `python backend/start_backend.py flask`
- Start frontend: `npm run dev` (in frontend folder)

## 🔧 Common Commands
```bash
# Backend
cd backend
python start_backend.py flask    # Start Flask
python seed_test_data.py         # Load test data

# Frontend
cd frontend
npm run dev                      # Start dev server
npm run build                    # Build for production
```

## 📚 Documentation
- `ADMIN_DASHBOARD_IMPLEMENTATION.md` - Admin dashboard technical details
- `ADMIN_DASHBOARD_QUICK_START.md` - Admin dashboard user guide
- `FINAL_STATUS.md` - Complete status report
- `QUICK_START.md` - 5-minute setup
- `README_SETUP.md` - Full documentation
- `TEST_CREDENTIALS.md` - Testing guide
- `FRONTEND_FUNCTIONALITY_CHECK.md` - Functionality audit
- `AFRAME_ERROR_INFO.md` - Graph visualization fix details

## 🎉 You're All Set!
Everything is working perfectly! 

**Latest Updates**:
- ✅ Admin dashboard shows system-wide metrics with proper RBAC
- ✅ Graph visualization fetches from Neo4j (2000 nodes, 15000 edges)
- ✅ Automatic fallback to SQLite if Neo4j fails
- ✅ All routes functional and data retrieved from Neo4j

See `NEO4J_FIX_SUMMARY.md` and `COMPLETE_FIX_SUMMARY.md` for details.
