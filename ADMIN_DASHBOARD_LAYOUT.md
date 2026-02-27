# Admin Dashboard Layout

## Visual Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│  Project Niyati - Admin Dashboard                    [Home] [Graph] │
│  Government Officer - System-Wide View               [Upload] [Logout]│
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  System Health Overview                                             │
├──────────────┬──────────────┬──────────────┬──────────────────────┤
│ ❤️ Overall   │ 👥 Total     │ 📊 Records   │ ⚠️ Alerts           │
│ Health Score │ Taxpayers    │ Processed    │ Generated           │
│              │              │ Today        │ Today               │
│    75/100    │     156      │    847       │      12             │
└──────────────┴──────────────┴──────────────┴──────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Risk Distribution                                                  │
├───────────────────────┬───────────────────────┬────────────────────┤
│  High Risk            │  Medium Risk          │  Low Risk          │
│  🔴                   │  🟡                   │  🟢                │
│  12 (7.7%)            │  45 (28.8%)           │  99 (63.5%)        │
└───────────────────────┴───────────────────────┴────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Structural Fraud Patterns Detected                                 │
├───────────────────────┬───────────────────────┬────────────────────┤
│  🔄 Circular Trade    │  👻 Ghost Invoices    │  🕸️ Spider Webs   │
│  [8]                  │  [15]                 │  [3]               │
│  Entities involved in │  Suspicious invoices  │  Complex fraud     │
│  circular trading     │  without transactions │  networks          │
└───────────────────────┴───────────────────────┴────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Vendor Risk Analysis                              [Click for details]│
├──────────────┬─────────────────┬──────────┬────────────┬──────────┤
│ Vendor GSTIN │ Vendor Name     │ Risk     │ ITC at Risk│ Last Txn │
├──────────────┼─────────────────┼──────────┼────────────┼──────────┤
│ 29AABCT...   │ ABC Corp Ltd    │ 🔴 HIGH  │ ₹2,45,000  │ 15-Jan   │
│ 27AABCU...   │ XYZ Industries  │ 🟡 MED   │ ₹1,20,000  │ 20-Jan   │
│ 07AABCU...   │ PQR Traders     │ 🟢 LOW   │ ₹45,000    │ 22-Jan   │
└──────────────┴─────────────────┴──────────┴────────────┴──────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Agent Activity Log                    🟢 Connected  [Clear] [Expand]│
├─────────────────────────────────────────────────────────────────────┤
│  14:23:45  Agent 1: Starting ingestion pipeline...                  │
│  14:23:46  Agent 2: Processing purchase register...                 │
│  14:23:47  Agent 3: Analyzing circular trade patterns...            │
│  14:23:48  Agent 4: Computing risk scores...                        │
│  14:23:49  Agent 5: Generating narratives...                        │
│  14:23:50  Agent 1: Ingestion complete. 847 records processed.      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┬──────────────────────────────────────┐
│  🌐 Neo4j Network            │  📈 EBM SHAP Analysis                │
│  Visualization               │                                      │
│                              │  Explainable AI insights showing     │
│  Interactive graph showing   │  top risk drivers and feature        │
│  entity relationships and    │  contributions                       │
│  fraud patterns              │                                      │
│                              │                                      │
│  [View Full Graph]           │  [View Analysis]                     │
└──────────────────────────────┴──────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  🟢 System Operational                              [Refresh Data]  │
│  Last Ingestion: 28 Feb 2026, 14:23:50                             │
└─────────────────────────────────────────────────────────────────────┘
```

## Color Scheme

### Risk Levels
- 🔴 **Red**: High Risk (score < 40)
- 🟡 **Yellow**: Medium Risk (score 40-69)
- 🟢 **Green**: Low Risk (score ≥ 70)

### Agent Colors
- 🔵 **Blue**: Agent 1
- 🟣 **Purple**: Agent 2
- 🟢 **Green**: Agent 3
- 🟠 **Orange**: Agent 4
- 🩷 **Pink**: Agent 5
- 🔴 **Red**: Errors

### UI Elements
- **Primary**: Blue (#2563eb) - Actions, links
- **Success**: Green (#10b981) - Positive states
- **Warning**: Orange (#f97316) - Alerts
- **Danger**: Red (#ef4444) - High risk, errors
- **Info**: Purple (#9333ea) - Secondary actions
- **Neutral**: Gray (#6b7280) - Disabled, text

## Interactive Elements

### Clickable
1. **Vendor Table Rows**: Click to view detailed risk narrative
2. **Navigation Buttons**: Home, Graph, Upload, Logout
3. **Refresh Data**: Reload dashboard metrics
4. **Clear Logs**: Reset agent log history
5. **Expand Logs**: Toggle log viewer height
6. **View Full Graph**: Navigate to network visualization
7. **View Analysis**: Navigate to SHAP analysis

### Hover Effects
- All buttons show hover state (darker shade)
- Table rows highlight on hover
- Cards have subtle shadow increase
- Links underline on hover

## Responsive Breakpoints

### Desktop (≥1024px)
- 4 columns for system metrics
- 3 columns for risk distribution
- 3 columns for fraud patterns
- Full-width table
- 2 columns for placeholders

### Tablet (768px - 1023px)
- 2 columns for system metrics
- 3 columns for risk distribution
- 3 columns for fraud patterns
- Full-width table
- 2 columns for placeholders

### Mobile (<768px)
- 1 column for all sections
- Stacked cards
- Scrollable table
- Full-width placeholders

## Data Flow

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │
       │ GET /dashboard (with Bearer token)
       ▼
┌──────────────┐
│   Backend    │
│   Flask API  │
└──────┬───────┘
       │
       │ Query database
       ▼
┌──────────────┐
│   SQLite     │
│   Database   │
└──────┬───────┘
       │
       │ Return data
       ▼
┌──────────────┐
│ AdminDashboard│
│  Component   │
└──────┬───────┘
       │
       │ Transform & Display
       ▼
┌──────────────┐
│   UI Cards   │
│   & Tables   │
└──────────────┘

Parallel SSE Stream:
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │
       │ EventSource /logs/stream
       ▼
┌──────────────┐
│   Backend    │
│   SSE Stream │
└──────┬───────┘
       │
       │ Real-time logs
       ▼
┌──────────────┐
│ AgentLogViewer│
└──────────────┘
```

## Component Hierarchy

```
AdminDashboard
├── Header
│   ├── Title & Subtitle
│   └── Navigation Buttons
├── System Health Overview
│   ├── MetricCard (Health Score)
│   ├── MetricCard (Total Taxpayers)
│   ├── MetricCard (Records Processed)
│   └── MetricCard (Alerts Generated)
├── Risk Distribution
│   ├── RiskCard (High Risk)
│   ├── RiskCard (Medium Risk)
│   └── RiskCard (Low Risk)
├── Fraud Patterns
│   ├── FraudPatternCard (Circular Trade)
│   ├── FraudPatternCard (Ghost Invoices)
│   └── FraudPatternCard (Spider Webs)
├── VendorRiskTable
│   ├── Table Header
│   ├── Table Rows (clickable)
│   └── Modal (Risk Narrative)
├── AgentLogViewer
│   ├── Header (status, controls)
│   ├── Log Container (scrollable)
│   └── Footer (legend)
├── Placeholder Cards
│   ├── Neo4j Visualization
│   └── EBM SHAP Analysis
└── System Status Footer
    ├── Status Indicator
    ├── Last Ingestion Time
    └── Refresh Button
```

## State Management

```typescript
// Main state
const [metrics, setMetrics] = useState<SystemHealthMetrics | null>(null);
const [vendors, setVendors] = useState<VendorRisk[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

// VendorRiskTable state
const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);
const [narrative, setNarrative] = useState<string>('');
const [loadingNarrative, setLoadingNarrative] = useState(false);

// AgentLogViewer state
const [logs, setLogs] = useState<LogMessage[]>([]);
const [isConnected, setIsConnected] = useState(false);
const [isExpanded, setIsExpanded] = useState(false);
```

## Performance Optimizations

1. **Lazy Loading**: Components load on demand
2. **Memoization**: Expensive calculations cached
3. **Virtual Scrolling**: Large log lists optimized
4. **Debounced Refresh**: Prevent API spam
5. **SSE Cleanup**: Proper connection management
6. **Efficient Re-renders**: React.memo on cards

## Accessibility Features

1. **Semantic HTML**: Proper heading hierarchy
2. **ARIA Labels**: Screen reader support
3. **Keyboard Navigation**: Tab through elements
4. **Color Contrast**: WCAG AA compliant
5. **Focus Indicators**: Visible focus states
6. **Alt Text**: Descriptive labels

## Error Handling

1. **Network Errors**: Retry button shown
2. **Auth Errors**: Auto-redirect to login
3. **SSE Disconnect**: Status indicator updates
4. **Empty States**: Friendly messages
5. **Loading States**: Spinners with text
6. **Validation**: Input sanitization

## Security Considerations

1. **Token Auth**: Bearer token in headers
2. **HTTPS**: Production uses secure protocol
3. **XSS Prevention**: React auto-escapes
4. **CSRF Protection**: Token-based auth
5. **Role Validation**: Server-side checks
6. **Secure Storage**: localStorage for tokens
