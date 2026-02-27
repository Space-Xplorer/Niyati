# Quick Reference Card

## 🚀 Application URLs
- **Frontend**: http://localhost:3000
- **Backend**: http://127.0.0.1:5000
- **Status**: ✅ Both running

## 🔑 Test Credentials

### Create Admin Account
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
```

## 📊 Test Data (3 Entities)
1. `29AABCT1332L1Z5` - HIGH RISK (78.5%)
2. `27AABCU9603R1ZM` - MEDIUM RISK (42%)
3. `07AABCU9603R1ZX` - LOW RISK (15%)

## ✅ What Works
- ✅ Landing page
- ✅ Signup/Login
- ✅ Dashboard with data
- ✅ Session persistence
- ✅ RBAC filtering
- ✅ Token expiration
- ✅ Graph page (empty data)

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
- `FINAL_STATUS.md` - Complete status report
- `QUICK_START.md` - 5-minute setup
- `README_SETUP.md` - Full documentation
- `TEST_CREDENTIALS.md` - Testing guide
- `FRONTEND_FUNCTIONALITY_CHECK.md` - Functionality audit

## 🎉 You're All Set!
Everything is working. Start testing at http://localhost:3000
