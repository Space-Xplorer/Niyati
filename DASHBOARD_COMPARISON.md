# Dashboard Comparison: Admin vs Taxpayer

## Overview

Project Niyati has two distinct dashboard views based on user role:

1. **AdminDashboard**: System-wide view for Government Officers
2. **TaxpayerDashboard**: Individual entity view for Business Owners

## Side-by-Side Comparison

### Admin Dashboard (Government Officer)
```
┌─────────────────────────────────────────────────┐
│ Project Niyati - Admin Dashboard                │
│ Government Officer - System-Wide View           │
└─────────────────────────────────────────────────┘

System Health Overview
├─ Overall Health Score: 75/100
├─ Total Taxpayers: 156
├─ Records Processed Today: 847
└─ Alerts Generated Today: 12

Risk Distribution
├─ High Risk: 12 (7.7%)
├─ Medium Risk: 45 (28.8%)
└─ Low Risk: 99 (63.5%)

Fraud Patterns
├─ Circular Trade: 8 entities
├─ Ghost Invoices: 15 detected
└─ Spider Webs: 3 networks

Vendor Risk Table (All Taxpayers)
├─ 29AABCT1332L1Z5 - HIGH RISK
├─ 27AABCU9603R1ZM - MEDIUM RISK
├─ 07AABCU9603R1ZX - LOW RISK
└─ ... (156 total)

Agent Activity Log (Real-time SSE)
├─ Agent 1: Processing...
├─ Agent 2: Analyzing...
└─ Agent 3: Computing...
```

### Taxpayer Dashboard (Business Owner)
```
┌─────────────────────────────────────────────────┐
│ Trust Dashboard                                  │
│ GSTIN: 29AABCT1332L1Z5                          │
└─────────────────────────────────────────────────┘

Health Score
└─ Your Score: 45/100 (Medium Risk)

Risk Level
├─ Risk Probability: 78.5%
├─ Circular Trade Patterns: 2
├─ Ghost Invoices: 5
└─ Spider Web Involvement: Yes

Top Risk Drivers (SHAP)
├─ Feature 1: High transaction velocity
├─ Feature 2: Unusual supplier patterns
└─ Feature 3: Geographic anomalies

Vendor Risk Analysis (Your Vendors)
├─ Vendor A - HIGH RISK
├─ Vendor B - MEDIUM RISK
└─ Vendor C - LOW RISK

Agent Activity Log (Real-time SSE)
└─ Same as admin view
```

## Key Differences

### Scope
| Feature | Admin Dashboard | Taxpayer Dashboard |
|---------|----------------|-------------------|
| **View** | System-wide | Individual entity |
| **Data** | All taxpayers | Single GSTIN |
| **Metrics** | Aggregate | Personal |
| **Access** | All entities | Own data only |

### Features

#### Admin Dashboard Only
- ✅ System health overview
- ✅ Total taxpayer count
- ✅ Risk distribution across all entities
- ✅ Fraud pattern detection counts
- ✅ All taxpayers in vendor table
- ✅ Records processed today
- ✅ Alerts generated today

#### Taxpayer Dashboard Only
- ✅ Personal health score gauge
- ✅ Individual risk probability
- ✅ SHAP plots (top risk drivers)
- ✅ Personal fraud pattern involvement
- ✅ Own vendor risk analysis only

#### Shared Features
- ✅ Agent activity log (SSE stream)
- ✅ Navigation to graph view
- ✅ Logout functionality
- ✅ Responsive design
- ✅ Real-time updates

## Access Control

### Admin Dashboard
```typescript
// Requires admin role
if (user?.role === 'admin') {
  return <AdminDashboard token={token} onLogout={logout} />;
}
```

**Credentials**:
- Email: `admin@gstn.gov.in`
- Password: `admin123`
- Role: `admin`

### Taxpayer Dashboard
```typescript
// Default for business_owner role
return <TaxpayerDashboard />;
```

**Credentials**:
- Email: Any GSTIN (e.g., `29AABCT1332L1Z5`)
- Password: User-defined
- Role: `business_owner`

## Use Cases

### Admin Dashboard Use Cases

1. **System Monitoring**
   - Check overall system health
   - Monitor daily processing volume
   - Track alert generation

2. **Risk Assessment**
   - Identify high-risk entities
   - Analyze risk distribution
   - Detect fraud patterns

3. **Investigation**
   - Review all taxpayer risks
   - Click for detailed narratives
   - Navigate to network graph

4. **Compliance**
   - Monitor circular trade
   - Track ghost invoices
   - Identify spider web networks

### Taxpayer Dashboard Use Cases

1. **Self-Assessment**
   - Check personal health score
   - Review risk level
   - Understand risk drivers

2. **Vendor Management**
   - Assess vendor risks
   - Review ITC at risk
   - Monitor transaction dates

3. **Compliance**
   - Understand fraud involvement
   - Review SHAP explanations
   - Take corrective actions

4. **Transparency**
   - See what government sees
   - Understand risk calculation
   - Access detailed narratives

## Data Sources

### Admin Dashboard
```
GET /dashboard (admin token)
Returns:
{
  health_score: 75,
  vendor_risks: [
    { vendor_gstin: "29AABCT...", risk_level: "HIGH_RISK", ... },
    { vendor_gstin: "27AABCU...", risk_level: "MEDIUM_RISK", ... },
    // ... all taxpayers
  ],
  patterns: {
    circular_trade: 8,
    ghost_invoices: 15,
    spider_web_involvement: true
  }
}
```

### Taxpayer Dashboard
```
GET /dashboard (taxpayer token)
Returns:
{
  gstin: "29AABCT1332L1Z5",
  health_score: 45,
  risk_level: "MEDIUM_RISK",
  risk_probability: 0.785,
  vendor_risks: [
    // Only this taxpayer's vendors
  ],
  patterns: {
    circular_trade: 2,
    ghost_invoices: 5,
    spider_web_involvement: true
  }
}
```

## Visual Design

### Admin Dashboard
- **Color Scheme**: Professional blue/gray
- **Layout**: Dense, information-rich
- **Cards**: Metric-focused, compact
- **Emphasis**: System-wide statistics

### Taxpayer Dashboard
- **Color Scheme**: Warm, personal
- **Layout**: Spacious, easy to read
- **Cards**: Explanation-focused
- **Emphasis**: Individual insights

## Navigation

### Admin Dashboard
```
[Home] [Network Graph] [Upload Data] [Logout]
```

### Taxpayer Dashboard
```
[Home] [Network Graph] [Logout]
```

Note: Taxpayers don't have access to Upload Data

## Performance

### Admin Dashboard
- **Initial Load**: ~500ms (more data)
- **Data Size**: ~50KB (all taxpayers)
- **Updates**: Manual refresh
- **SSE**: Real-time logs

### Taxpayer Dashboard
- **Initial Load**: ~200ms (less data)
- **Data Size**: ~10KB (single entity)
- **Updates**: Manual refresh
- **SSE**: Real-time logs

## Security

### Admin Dashboard
- ✅ Requires admin role
- ✅ Server-side role validation
- ✅ Access to all data
- ✅ Audit logging (future)

### Taxpayer Dashboard
- ✅ Requires business_owner role
- ✅ Server-side GSTIN filtering
- ✅ Access to own data only
- ✅ No cross-entity access

## Mobile Experience

### Admin Dashboard
- **Optimized for**: Tablet/Desktop
- **Mobile**: Functional but dense
- **Recommendation**: Use desktop for best experience

### Taxpayer Dashboard
- **Optimized for**: All devices
- **Mobile**: Fully responsive
- **Recommendation**: Works great on mobile

## Future Enhancements

### Admin Dashboard
- [ ] Date range filters
- [ ] Export reports (PDF/CSV)
- [ ] Custom alert thresholds
- [ ] User management panel
- [ ] Audit log viewer
- [ ] Comparison views

### Taxpayer Dashboard
- [ ] Historical trends
- [ ] Peer comparison
- [ ] Recommendations
- [ ] Document upload
- [ ] Dispute resolution
- [ ] Compliance checklist

## Summary

| Aspect | Admin Dashboard | Taxpayer Dashboard |
|--------|----------------|-------------------|
| **Purpose** | System monitoring | Self-assessment |
| **Scope** | All entities | Single entity |
| **Data** | Aggregate | Personal |
| **Users** | Government officers | Business owners |
| **Access** | admin role | business_owner role |
| **Features** | System metrics | Personal insights |
| **Design** | Dense, professional | Spacious, friendly |
| **Mobile** | Desktop-first | Mobile-friendly |

Both dashboards provide valuable insights tailored to their respective user roles, ensuring appropriate access control while maintaining transparency and usability.
