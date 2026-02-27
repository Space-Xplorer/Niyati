# Test Credentials for Project Niyati

The database has been seeded with test data! You can now test the application.

## ✅ Application Status

- **Frontend**: Running at http://localhost:3000
- **Backend**: Running at http://127.0.0.1:5000
- **Database**: Seeded with test data

## Test Accounts

### Option 1: Create Admin Account (Recommended for Testing)

1. Go to http://localhost:3000/signup
2. Fill in:
   - **Email**: `admin@niyati.com` (or any email)
   - **Password**: `admin123` (or any password)
   - **Check**: "Register as Admin"
3. Click "Sign Up"
4. Login with your credentials
5. You'll see ALL data (global view)

### Option 2: Create Business Owner Account

1. Go to http://localhost:3000/signup
2. Fill in:
   - **Email**: `business@niyati.com` (or any email)
   - **Password**: `business123` (or any password)
   - **GSTIN**: Use one of these:
     - `29AABCT1332L1Z5` (Tech Solutions - HIGH RISK)
     - `27AABCU9603R1ZM` (Global Traders - MEDIUM RISK)
     - `07AABCU9603R1ZX` (Retail Mart - LOW RISK)
   - **Uncheck**: "Register as Admin"
3. Click "Sign Up"
4. Login with your credentials
5. You'll see only YOUR GSTIN data (filtered view)

## Sample Data Available

### Entities (3 companies)
1. **Tech Solutions Pvt Ltd** - `29AABCT1332L1Z5`
   - Risk Level: HIGH_RISK (78.5%)
   - Issues: Payment gaps, ghost invoices, circular trading
   
2. **Global Traders Inc** - `27AABCU9603R1ZM`
   - Risk Level: MEDIUM_RISK (42%)
   - Issues: Filing delays, limited vendor diversity
   
3. **Retail Mart Ltd** - `07AABCU9603R1ZX`
   - Risk Level: LOW_RISK (15%)
   - Issues: Minor transaction anomalies

### Fraud Patterns (3 patterns detected)
- Circular Trade: 2 entities involved
- Ghost Invoices: 15 suspicious invoices
- Spider Web: 3 entities in network

## What You Can Test

### 1. Dashboard View
- Health score visualization
- Risk level badges
- Top risk drivers
- Fraud pattern summary
- Vendor risk table (empty for now)

### 2. RBAC (Role-Based Access Control)
- **Admin**: Sees all 3 entities' data
- **Business_Owner**: Sees only their GSTIN data

### 3. Session Persistence
- Login and refresh the page - you stay logged in
- Token expires after 24 hours - automatic logout
- Close browser and reopen - session persists

### 4. Authentication Flow
- Signup validation
- Login with credentials
- Protected routes (dashboard requires login)
- Logout functionality

## Quick Test Steps

1. **Sign up as Admin**:
   ```
   Email: admin@test.com
   Password: admin123
   Role: Admin (checked)
   ```

2. **Login**:
   - Use the credentials you just created
   - You'll be redirected to dashboard

3. **View Dashboard**:
   - See health scores for all 3 entities
   - View risk levels (HIGH, MEDIUM, LOW)
   - Check fraud patterns detected

4. **Test Logout**:
   - Click "Logout" button
   - You'll be redirected to login page
   - Session cleared from localStorage

5. **Test Session Persistence**:
   - Login again
   - Refresh the page
   - You should stay logged in

## Troubleshooting

### "No data available" on dashboard
**Solution**: The data has been seeded! Just refresh the page after logging in.

### "GSTIN not found" during signup
**Solution**: The GSTIN validation has been disabled for development. You can now use any GSTIN or sign up as Admin.

### Can't see data after login
**Solution**: 
1. Make sure you're logged in (check if you see "Logout" button)
2. Refresh the page
3. Check browser console for errors (F12)

### 401 Unauthorized errors
**Solution**: 
1. Logout and login again
2. Clear browser localStorage (F12 > Application > Local Storage > Clear)
3. Try signing up with a new account

## Next Steps

Once you've tested the basic functionality:

1. **Upload CSV Data** (if using FastAPI):
   - Switch to FastAPI backend: Change `.env.local` to port 8000
   - Go to `/upload` page
   - Upload the CSV files from `backend/data/` folder

2. **View Graph Visualization**:
   - Click "View Graph" button on dashboard
   - See transaction network (requires Neo4j data)

3. **Test Real-Time Logs** (FastAPI only):
   - Connect to SSE endpoint at `/logs/stream`
   - See agent progress in real-time

## CSV Files Available

If you want to test the full workflow with CSV upload (FastAPI only):

```
backend/data/
├── e_invoices.csv
├── eway_bills.csv
├── entity_master.csv
├── filing_history.csv
├── purchase_register.csv
├── returns_summary.csv
└── feature_vectors.csv
```

## Summary

✅ Backend running on port 5000  
✅ Frontend running on port 3000  
✅ Database seeded with test data  
✅ 3 sample entities with risk predictions  
✅ 3 fraud patterns detected  
✅ GSTIN validation disabled for easy testing  
✅ Session persistence working  
✅ RBAC filtering implemented  

**You're all set! Start testing at http://localhost:3000** 🚀
