# Admin Dashboard Implementation

## Overview

Created a comprehensive AdminDashboard component for Project Niyati, designed specifically for Government Officers with admin role access. The dashboard provides system-wide visibility into tax fraud detection metrics and real-time monitoring capabilities.

## Component Location

- **Main Component**: `frontend/src/components/AdminDashboard.tsx`
- **Integration**: `frontend/src/app/dashboard/page.tsx` (automatically shows AdminDashboard for admin users)

## Features Implemented

### 1. System Health Overview
Four key metric cards displaying:
- **Overall Health Score**: System-wide health metric (0-100 scale)
- **Total Taxpayers**: Count of all taxpayers in the system
- **Records Processed Today**: Daily ingestion statistics
- **Alerts Generated Today**: High-risk alerts count

Each card features:
- Color-coded indicators (red/yellow/green based on severity)
- Emoji icons for visual clarity
- Real-time data from `/dashboard` API endpoint

### 2. Risk Distribution
Three-card breakdown showing:
- **High Risk**: Count and percentage of high-risk taxpayers
- **Medium Risk**: Count and percentage of medium-risk taxpayers
- **Low Risk**: Count and percentage of low-risk taxpayers

Visual design:
- Color-coded cards (red, yellow, green)
- Large numbers for quick scanning
- Percentage calculations for context

### 3. Structural Fraud Patterns
Three fraud pattern detection cards:
- **Circular Trade**: Entities involved in circular trading patterns (🔄)
- **Ghost Invoices**: Suspicious invoices without transactions (👻)
- **Spider Web Networks**: Complex interconnected fraud networks (🕸️)

Features:
- Badge counters showing detection counts
- Descriptive text explaining each pattern
- Color-coded by severity

### 4. Vendor Risk Table
Reuses existing `VendorRiskTable` component:
- Displays all taxpayers sorted by risk tier
- Click-to-view detailed risk narratives
- Fetches data from `/dashboard` API endpoint
- Shows GSTIN, name, risk level, ITC at risk, last transaction date

### 5. Agent Log Viewer
Reuses existing `AgentLogViewer` component:
- Real-time SSE stream from `/logs/stream`
- Shows ingestion pipeline activity
- Color-coded by agent (5 agents supported)
- Expandable/collapsible view
- Auto-scroll to latest logs
- Connection status indicator

### 6. Placeholder Sections
Two placeholder cards for future features:
- **Neo4j Network Visualization**: Links to `/graph` page
- **EBM SHAP Analysis**: Links to detailed analysis view

### 7. System Status Footer
- Real-time system operational status
- Last ingestion timestamp
- Refresh data button

## Technical Implementation

### State Management
```typescript
const [metrics, setMetrics] = useState<SystemHealthMetrics | null>(null);
const [vendors, setVendors] = useState<VendorRisk[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

### Data Fetching
- Uses `fetch` API with Bearer token authentication
- Endpoint: `${apiUrl}/dashboard`
- Transforms response data for admin-specific metrics
- Error handling with retry capability

### Component Architecture
```
AdminDashboard (Main Container)
├── MetricCard (System metrics)
├── RiskCard (Risk distribution)
├── FraudPatternCard (Fraud patterns)
├── VendorRiskTable (Reused component)
├── AgentLogViewer (Reused component)
└── PlaceholderCard (Future features)
```

### Styling
- Tailwind CSS for all styling
- Responsive grid layouts (1/2/3/4 columns based on screen size)
- Color-coded components for quick visual scanning
- Consistent spacing and shadows
- Hover effects and transitions

## Integration

### Dashboard Page Logic
```typescript
export default function DashboardPage() {
  const { token, user, logout } = useAuth();
  
  // If user is admin, show AdminDashboard
  if (user?.role === 'admin') {
    return <AdminDashboard token={token || ''} onLogout={logout} />;
  }
  
  // Otherwise show regular taxpayer dashboard
  // ... existing code
}
```

### Authentication
- Uses `AuthContext` for user role detection
- Automatically routes admin users to AdminDashboard
- Regular users see standard taxpayer dashboard
- Token-based API authentication

## API Requirements

The AdminDashboard expects the `/dashboard` endpoint to return:

```typescript
{
  health_score: number;
  vendor_risks: Array<{
    vendor_gstin: string;
    vendor_name: string;
    risk_level: 'HIGH_RISK' | 'MEDIUM_RISK' | 'LOW_RISK';
    itc_at_risk: number;
    last_transaction_date: string;
  }>;
  patterns: {
    circular_trade: number;
    ghost_invoices: number;
    spider_web_involvement: boolean;
  };
}
```

The component transforms this data to calculate:
- Total taxpayer count
- Risk tier distributions
- Daily activity metrics

## SSE Stream

The AgentLogViewer connects to:
- Endpoint: `${apiUrl}/logs/stream`
- Protocol: Server-Sent Events (SSE)
- Expected format: Plain text log messages
- Auto-reconnect on connection loss

## Navigation

Header includes buttons for:
- **Home**: Navigate to landing page
- **Network Graph**: View Neo4j visualization (`/graph`)
- **Upload Data**: Access data ingestion (`/upload`)
- **Logout**: Sign out and clear session

## Loading States

- Initial load: Full-screen spinner with message
- Error state: Error message with retry button
- Empty state: "No data available" message

## Responsive Design

- Mobile (< 768px): Single column layout
- Tablet (768px - 1024px): 2-column layout
- Desktop (> 1024px): 3-4 column layout
- All components stack gracefully on smaller screens

## Color Scheme

### Health/Risk Colors
- **Green** (#10b981): Low risk, good health (≥70)
- **Yellow** (#f59e0b): Medium risk, moderate health (40-69)
- **Red** (#ef4444): High risk, poor health (<40)

### Accent Colors
- **Blue** (#2563eb): Primary actions, info
- **Purple** (#9333ea): Secondary actions
- **Orange** (#f97316): Warnings, alerts
- **Gray** (#6b7280): Neutral, disabled

## Future Enhancements

1. **Real-time Updates**: WebSocket for live metric updates
2. **Date Range Filters**: Filter data by time period
3. **Export Functionality**: Download reports as PDF/CSV
4. **Drill-down Views**: Click metrics to see detailed breakdowns
5. **Comparison Views**: Compare metrics across time periods
6. **Alert Configuration**: Set custom thresholds for alerts
7. **User Management**: Admin panel for user access control

## Testing

To test the AdminDashboard:

1. Login with admin credentials:
   ```
   Email: admin@gstn.gov.in
   Password: admin123
   ```

2. Navigate to `/dashboard`

3. Verify:
   - System metrics display correctly
   - Risk distribution shows proper counts
   - Fraud patterns are visible
   - Vendor table loads and is interactive
   - Agent logs stream in real-time
   - All navigation buttons work

## Dependencies

- React 19.2.3
- Next.js 16.1.6
- Tailwind CSS 4.2.1
- Recharts 3.7.0 (for ShapePlots)
- react-force-graph-2d 1.29.1 (for network graph)

## Performance Considerations

- Dynamic imports for heavy components
- Memoized calculations for derived metrics
- Efficient re-rendering with proper key props
- SSE connection cleanup on unmount
- Debounced refresh to prevent API spam

## Accessibility

- Semantic HTML structure
- ARIA labels on interactive elements
- Keyboard navigation support
- Color contrast meets WCAG AA standards
- Screen reader friendly text

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Conclusion

The AdminDashboard provides a comprehensive, real-time view of the Project Niyati tax fraud detection system. It combines macro-level metrics, detailed risk analysis, and live monitoring capabilities in a clean, intuitive interface designed for government officers.
