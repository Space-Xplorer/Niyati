# Admin Dashboard - Quick Start Guide

## Access the Admin Dashboard

1. **Login as Admin**
   ```
   URL: http://localhost:3000/login
   Email: admin@gstn.gov.in
   Password: admin123
   ```

2. **Navigate to Dashboard**
   - After login, click "Dashboard" or go to `/dashboard`
   - Admin users automatically see the AdminDashboard view
   - Regular users see the standard taxpayer dashboard

## Dashboard Sections

### 1. System Health Overview (Top Row)
Four metric cards showing:
- **Overall Health Score**: 0-100 scale, color-coded
- **Total Taxpayers**: Count of all entities in system
- **Records Processed Today**: Daily ingestion count
- **Alerts Generated Today**: High-risk alerts

### 2. Risk Distribution (Second Row)
Three cards showing taxpayer breakdown:
- **High Risk**: Red card with count and percentage
- **Medium Risk**: Yellow card with count and percentage
- **Low Risk**: Green card with count and percentage

### 3. Fraud Patterns (Third Row)
Three detection cards:
- **Circular Trade** 🔄: Circular trading patterns
- **Ghost Invoices** 👻: Suspicious invoices
- **Spider Web Networks** 🕸️: Complex fraud networks

### 4. Vendor Risk Table
- Full list of taxpayers with risk levels
- Click any row to see detailed risk narrative
- Sortable by risk level
- Shows ITC at risk and last transaction date

### 5. Agent Activity Log
- Real-time SSE stream of agent activity
- Color-coded by agent (5 agents)
- Expandable view for more logs
- Clear button to reset log history
- Connection status indicator

### 6. Future Features (Placeholders)
- **Neo4j Network Visualization**: Click to view graph
- **EBM SHAP Analysis**: Click for detailed analysis

## Key Features

### Real-Time Updates
- Agent logs stream live via SSE
- Connection status shows green dot when active
- Auto-scroll to latest log entries

### Interactive Elements
- Click vendor rows for risk narratives
- Expand/collapse agent log viewer
- Refresh data button in footer
- Navigation buttons in header

### Visual Indicators
- Color-coded metrics (red/yellow/green)
- Emoji icons for quick recognition
- Animated pulse on system status
- Hover effects on interactive elements

## Navigation

### Header Buttons
- **Home**: Return to landing page
- **Network Graph**: View Neo4j visualization
- **Upload Data**: Access data ingestion
- **Logout**: Sign out

### Quick Actions
- **Refresh Data**: Bottom right of page
- **Clear Logs**: In agent log viewer
- **Expand Logs**: In agent log viewer

## Data Refresh

### Automatic
- Agent logs: Real-time via SSE
- Dashboard metrics: On page load

### Manual
- Click "Refresh Data" button in footer
- Reload page (browser refresh)

## Troubleshooting

### No Data Showing
1. Check backend is running: `http://localhost:5000`
2. Verify admin login credentials
3. Check browser console for errors
4. Click "Refresh Data" button

### Agent Logs Not Streaming
1. Check SSE endpoint: `http://localhost:5000/logs/stream`
2. Look for connection status (green dot)
3. Check browser console for connection errors
4. Verify backend is running

### Vendor Table Empty
1. Ensure data has been uploaded via `/upload`
2. Check backend database has records
3. Verify API endpoint `/dashboard` returns data
4. Check authentication token is valid

## API Endpoints Used

- **GET /dashboard**: Main dashboard data
  - Requires: Bearer token
  - Returns: Health score, vendor risks, patterns

- **GET /logs/stream**: SSE log stream
  - Requires: No auth (public endpoint)
  - Returns: Server-sent events with log messages

- **GET /risk/{gstin}**: Vendor risk narrative
  - Requires: Bearer token
  - Returns: Detailed risk narrative for specific GSTIN

## Browser Requirements

- Modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Cookies enabled (for auth token)
- EventSource API support (for SSE)

## Performance Tips

1. **Clear logs periodically**: Use "Clear" button to free memory
2. **Collapse log viewer**: When not actively monitoring
3. **Refresh data sparingly**: Avoid excessive API calls
4. **Use network graph**: For detailed relationship analysis

## Security Notes

- Admin dashboard requires admin role
- All API calls use Bearer token authentication
- Tokens stored in localStorage
- Auto-logout on token expiration
- No sensitive data in URLs

## Mobile View

The dashboard is responsive:
- Single column on mobile
- Stacked cards for easy scrolling
- Touch-friendly buttons
- Readable text sizes
- Optimized for portrait orientation

## Keyboard Shortcuts

- **Tab**: Navigate between interactive elements
- **Enter**: Activate buttons/links
- **Escape**: Close modals (vendor narrative)
- **Space**: Scroll page

## Common Workflows

### Morning Check
1. Login as admin
2. Review system health score
3. Check alerts generated today
4. Scan fraud pattern counts
5. Review high-risk vendors

### Investigation
1. Identify high-risk vendor in table
2. Click row to view risk narrative
3. Navigate to network graph
4. Analyze entity relationships
5. Review SHAP analysis

### Monitoring
1. Expand agent log viewer
2. Watch real-time ingestion
3. Monitor for errors (red entries)
4. Check connection status
5. Clear logs when needed

## Support

For issues or questions:
1. Check browser console for errors
2. Verify backend logs
3. Review API endpoint responses
4. Check authentication status
5. Refer to main documentation

## Next Steps

After familiarizing with the dashboard:
1. Explore network graph visualization
2. Upload new data via `/upload`
3. Review individual taxpayer dashboards
4. Analyze SHAP plots for risk drivers
5. Configure alert thresholds (future feature)
