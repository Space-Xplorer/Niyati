# Niyati Frontend - Risk Intelligence Dashboard

![Frontend](https://img.shields.io/badge/Frontend-Next.js%2016-blue.svg)
![React](https://img.shields.io/badge/React-19.2.3-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-4.2-06B6D4.svg)

## 📖 Overview

The Niyati frontend is a modern, responsive web application built with **Next.js 16** and **React 19** that provides an intuitive interface for GST compliance management and risk analytics. Users can visualize entity relationships, monitor vendor risk scores, and interact with AI-powered insights through an interactive dashboard.

### Key Features

- **📊 Interactive Dashboards**: Real-time risk analytics for admin and business users
- **🔗 Graph Visualization**: Interactive entity relationship mapping (D3.js-based)
- **🎨 Modern UI/UX**: Tailwind CSS with responsive design
- **🔐 Secure Authentication**: JWT-based login with role-based access
- **📱 Mobile Responsive**: Optimized for desktop, tablet, and mobile
- **⚡ Performance Optimized**: Server-side rendering with Next.js
- **🧩 Reusable Components**: Well-structured component library
- **📈 Data Visualization**: Charts and graphs with Recharts

---

## 🏗️ Architecture

### Component Hierarchy

```
App (layout.tsx)
├── Authentication Layer (AuthContext)
│   ├── Login (login/page.tsx)
│   ├── Signup (signup/page.tsx)
│   └── Protected Routes
│
├── Dashboard Layer
│   ├── Admin Dashboard (AdminDashboard.tsx)
│   │   ├── Health Gauge
│   │   ├── Risk Distribution Chart
│   │   └── Vendor Risk Table
│   │
│   ├── Business Owner Dashboard (dashboard/page.tsx)
│   │   ├── Entity Overview
│   │   ├── Transaction Summary
│   │   └── Compliance Status
│   │
│   └── Analytics (analytics/page.tsx)
│       ├── Trend Charts
│       └── Export Reports
│
├── Graph Visualization (graph/page.tsx)
│   ├── Force Graph
│   ├── Entity Details Panel
│   └── Relationship Filters
│
├── Data Management
│   ├── Upload (upload/page.tsx)
│   │   └── CSV File Handler
│   │
│   └── Settings (settings/page.tsx)
│       └── User Preferences
│
└── Shared Components
    ├── Navigation
    ├── Layout Components
    ├── UI Primitives (Button, Input, etc.)
    └── Custom Hooks
```

### Data Flow Architecture

```
Browser Interface
        │
        ▼
    React Context (AuthContext)
    - JWT Token Management
    - User Profile & Permissions
        │
        ▼
    API Client (lib/api.ts)
    - Request Interceptors
    - Error Handling
    - Request/Response Logging
        │
        ▼
    Backend Flask API
    - Authentication
    - Business Logic
    - Database Queries
```

---

## 📁 Directory Structure

```
frontend/
├── src/
│   ├── app/                          # Next.js 13+ App Router
│   │   ├── layout.tsx                # Root layout wrapper
│   │   ├── page.tsx                  # Home page
│   │   ├── globals.css               # Global styles
│   │   ├── not-found.tsx             # 404 error page
│   │   │
│   │   ├── dashboard/                # Dashboard routes
│   │   │   └── page.tsx              # Business owner dashboard
│   │   │
│   │   ├── graph/                    # Graph visualization routes
│   │   │   ├── page.tsx              # Graph explorer view
│   │   │   └── error.tsx             # Graph error boundary
│   │   │
│   │   ├── login/                    # Authentication routes
│   │   │   └── page.tsx              # Login page
│   │   │
│   │   ├── signup/                   # User registration
│   │   │   └── page.tsx              # Signup page
│   │   │
│   │   └── upload/                   # Data management routes
│   │       └── page.tsx              # CSV upload interface
│   │
│   ├── components/                   # Reusable React Components
│   │   ├── AdminDashboard.tsx        # Admin analytics dashboard
│   │   ├── AgentCollaboration.tsx    # AI agent status & logs
│   │   ├── AgentLogViewer.tsx        # Real-time agent logs
│   │   ├── Button.tsx                # Custom button component
│   │   ├── HealthGauge.tsx           # System health indicator
│   │   ├── Input.tsx                 # Form input component
│   │   ├── NiyatiHero.tsx            # Landing page hero
│   │   ├── RiskBadge.tsx             # Risk level indicator
│   │   ├── ShapePlots.tsx            # SHAP value visualizations
│   │   ├── VendorRiskTable.tsx       # Vendor risk data table
│   │   │
│   │   └── ui/                       # UI Primitives
│   │       └── google-gemini-effect.tsx  # Animated effects
│   │
│   ├── context/                      # React Context & State
│   │   └── AuthContext.tsx           # Authentication context provider
│   │       - JWT token management
│   │       - User profile storage
│   │       - Auth state persistence
│   │
│   └── lib/                          # Utility Functions
│       └── api.ts                    # API client with interceptors
│           - HTTP request wrapper
│           - Response parsing
│           - Error handling
│           - Base URL configuration
│
├── public/                           # Static Assets
│   └── fonts/                        # Custom font files
│
├── next.config.ts                    # Next.js configuration
├── tsconfig.json                     # TypeScript configuration
├── tailwind.config.ts                # Tailwind CSS config
├── postcss.config.mjs                # PostCSS configuration
├── eslint.config.mjs                 # ESLint configuration
├── package.json                      # Dependencies & scripts
└── README.md                         # This file
```

---

## 🚀 Installation & Setup

### Prerequisites

```bash
# Node.js 18+ and npm/yarn
node --version  # v18.0.0+
npm --version   # v9.0.0+

# Backend running
# Expected at http://localhost:5000
```

### Installation Steps

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install
# or
yarn install

# 3. Create environment configuration
cat > .env.local << EOF
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
NEXT_PUBLIC_JWT_KEY=niyati-auth-token
EOF

# 4. Start development server
npm run dev
# or
yarn dev

# 5. Open browser
# Navigate to http://localhost:3000
```

### Environment variables

Create `.env.local` file:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
NEXT_PUBLIC_API_TIMEOUT=30000  # milliseconds

# Authentication
NEXT_PUBLIC_JWT_KEY=niyati-auth-token
NEXT_PUBLIC_JWT_EXPIRY=24h

# Feature Toggles
NEXT_PUBLIC_ENABLE_GRAPH_VIZ=true
NEXT_PUBLIC_ENABLE_AGENT_LOGS=true
NEXT_PUBLIC_ENABLE_EXPORT=true

# Analytics (Optional)
NEXT_PUBLIC_ANALYTICS_ID=
```

---

## 🎨 Component Library

### Core Components

#### Button Component
```tsx
import { Button } from '@/components/Button';

<Button 
  variant="primary"     // primary | secondary | danger
  size="md"             // sm | md | lg
  disabled={false}
  onClick={() => {}}
>
  Click Me
</Button>
```

#### Input Component
```tsx
import { Input } from '@/components/Input';

<Input
  type="text"
  label="Email"
  placeholder="user@example.com"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={emailError}
  required
/>
```

#### Risk Badge
```tsx
import { RiskBadge } from '@/components/RiskBadge';

<RiskBadge 
  level="HIGH_RISK"    // HIGH_RISK | MEDIUM_RISK | LOW_RISK
  probability={0.89}
/>
```

#### Health Gauge
```tsx
import { HealthGauge } from '@/components/HealthGauge';

<HealthGauge 
  score={78.5}
  size="large"         // small | medium | large
/>
```

### Dashboard Components

#### Admin Dashboard
```tsx
import AdminDashboard from '@/components/AdminDashboard';

<AdminDashboard 
  data={dashboardData}
  onVendorClick={(gstin) => navigateToEntity(gstin)}
  refreshInterval={30000}
/>
```

**Shows:**
- System health score
- Risk distribution pie chart
- High-risk vendors table
- Fraud pattern summary
- Agent activity logs

#### Vendor Risk Table
```tsx
import VendorRiskTable from '@/components/VendorRiskTable';

<VendorRiskTable
  vendors={vendorList}
  sortBy="risk_probability"
  onRowClick={(vendor) => viewDetails(vendor)}
/>
```

#### SHAP Plots
```tsx
import ShapePlots from '@/components/ShapePlots';

<ShapePlots
  modelExplanation={explanation}
  topFeatures={5}
/>
```

---

## 🔐 Authentication Flow

### Login Process
```
1. User enters credentials on /login
2. Frontend submits to POST /auth/login
3. Backend returns JWT token
4. Token stored in localStorage via AuthContext
5. Token attached to all API requests
6. Protected routes check auth state
```

### Implementation
```tsx
// context/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  userRole: string | null;
}

// Usage in components
const { user, logout, isAuthenticated } = useContext(AuthContext);

if (!isAuthenticated) {
  return <Navigate to="/login" />;
}
```

---

## 📡 API Integration

### API Client
```tsx
// lib/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('jwt_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Fetch Data Example
```tsx
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

export function useDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get('/dashboard')
      .then(res => setData(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading };
}
```

---

## 🎨 Styling & Theming

### Tailwind CSS Configuration
```tsx
// tailwind.config.ts
export default {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Niyati brand colors
        primary: 'rgb(59, 130, 246)',    // Blue
        success: 'rgb(34, 197, 94)',     // Green (LOW_RISK)
        warning: 'rgb(217, 119, 6)',     // Orange (MEDIUM_RISK)
        danger: 'rgb(239, 68, 68)',      // Red (HIGH_RISK)
      },
    },
  },
};
```

### Global Styles
```css
/* app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --color-primary: 3 102 214;
  --color-success: 34 197 94;
  --color-danger: 239 68 68;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}
```

---

## 📊 Data Visualization

### Chart Integration (Recharts)
```tsx
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts';

const RiskChart = ({ data }) => (
  <BarChart data={data} width={500} height={300}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="gstin" />
    <YAxis />
    <Tooltip />
    <Legend />
    <Bar dataKey="risk_probability" fill="#ef4444" />
  </BarChart>
);
```

### Graph Visualization (React Force Graph)
```tsx
import ForceGraph2D from 'react-force-graph-2d';

const EntityGraph = ({ nodes, links }) => (
  <ForceGraph2D
    graphData={{ nodes, links }}
    nodeAutoColorBy="category"
    nodeCanvasObject={(node, ctx) => {
      ctx.fillStyle = node.color || '#3b82f6';
      ctx.beginPath();
      ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI);
      ctx.fill();
    }}
    onNodeClick={(node) => console.log(node)}
  />
);
```

---

## 🧪 Testing

### Unit Tests
```bash
# Run tests
npm test

# Watch mode
npm test -- --watch

# Coverage report
npm test -- --coverage
```

### Test Example
```tsx
// __tests__/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '@/components/Button';

describe('Button Component', () => {
  it('renders button with text', () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });

  it('calls onClick handler', async () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>Click</Button>);
    
    await userEvent.click(screen.getByText('Click'));
    expect(onClick).toHaveBeenCalled();
  });
});
```

---

## 🚀 Building & Deployment

### Production Build
```bash
# Build optimized version
npm run build

# Start production server
npm start
```

### Static Export (Optional)
```bash
# next.config.ts
export const output = 'export';

# Build to 'out' directory
npm run build
```

### Docker Deployment
```bash
docker build -t niyati-frontend:latest .
docker run -p 3000:3000 niyati-frontend:latest
```

### Deployment Environments

#### Vercel (Recommended for Next.js)
```bash
# Connect GitHub repo to Vercel
# Environment variables: NEXT_PUBLIC_API_BASE_URL
# Auto-deploys on push
```

#### Railway / Render
See root [deploy.sh](../deploy.sh) for container configuration.

---

## 📱 Responsive Design

### Breakpoints
```tsx
// Tailwind breakpoints
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

### Mobile-first CSS
```tsx
// Mobile by default, then enhance
<div className="w-full md:w-1/2 lg:w-1/3">
  Responsive container
</div>
```

### Touch-friendly UI
```tsx
// Larger touch targets on mobile
<button className="p-4 md:p-2 h-12 md:h-10">
  Touch-friendly button
</button>
```

---

## 🎯 Accessibility

### ARIA Labels
```tsx
<button 
  aria-label="Delete vendor"
  aria-pressed={isPressed}
>
  🗑️
</button>
```

### Keyboard Navigation
```tsx
import { useEffect } from 'react';

useEffect(() => {
  const handleKeyPress = (e) => {
    if (e.key === 'Escape') {
      closeModal();
    }
  };
  window.addEventListener('keydown', handleKeyPress);
  return () => window.removeEventListener('keydown', handleKeyPress);
}, []);
```

### Color Contrast
- Use Tailwind utilities for WCAG AA compliance
- Avoid color-only indicators (use icons + color)

---

## 🔄 State Management

### Context API (Authentication)
```tsx
// AuthContext manages global auth state
// Re-renders only when auth changes
```

### Component State (React Hooks)
```tsx
const [vendors, setVendors] = useState([]);
const [filter, setFilter] = useState('');

const filteredVendors = vendors.filter(v => 
  v.name.toLowerCase().includes(filter.toLowerCase())
);
```

### Consider for Future:
- Redux for complex global state
- Zustand for lightweight store

---

## 🐛 Common Issues

### API Connection Failed
```
Check:
1. Backend running on http://localhost:5000
2. CORS enabled in backend
3. NEXT_PUBLIC_API_BASE_URL correct in .env.local
```

### Styles Not Loading
```bash
# Rebuild Tailwind
npm run build
rm -rf .next
npm run dev
```

### Authentication Lost on Refresh
```tsx
// Add token persistence to AuthContext
useEffect(() => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    setAuthState(token);
  }
}, []);
```

---

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Recharts](https://recharts.org)
- [React Force Graph](https://github.com/vasturiano/react-force-graph)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

## 🛠️ Development Workflow

### Creating a New Page
1. Create directory under `src/app/`
2. Add `page.tsx` component
3. Implement with TypeScript
4. Add authentication if needed
5. Test and document

```tsx
// src/app/new-feature/page.tsx
'use client';

import { useContext } from 'react';
import { AuthContext } from '@/context/AuthContext';

export default function NewFeaturePage() {
  const { user } = useContext(AuthContext);
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold">New Feature</h1>
      {/* Component content */}
    </div>
  );
}
```

### Creating a New Component
1. Create file in `src/components/`
2. Export as named export
3. Add TypeScript interfaces
4. Include JSDoc comments
5. Write unit tests

```tsx
// src/components/MyComponent.tsx
import { ReactNode } from 'react';

interface MyComponentProps {
  title: string;
  children: ReactNode;
  onClose?: () => void;
}

/**
 * MyComponent - Description of component
 * @param {MyComponentProps} props - Component properties
 */
export function MyComponent({ title, children, onClose }: MyComponentProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h2 className="text-xl font-semibold">{title}</h2>
      {children}
    </div>
  );
}
```

---

## 📊 Performance Optimization

### Code Splitting
```tsx
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <p>Loading chart...</p>,
});
```

### Image Optimization
```tsx
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="Niyati Logo"
  width={200}
  height={100}
  priority
/>
```

### Server Components
```tsx
// Fetch data securely on server
export default async function Page() {
  const data = await fetch('http://backend/api');
  return <Component data={data} />;
}
```

---

## 🎓 Hackathon Context

Niyati frontend was developed as part of the **GST Compliance & Risk Intelligence Hackathon**, showcasing:
- Modern web technologies (React 19, Next.js 16)
- Enterprise-grade UI/UX design
- Real-time data visualization
- Secure authentication flows
- Responsive, accessible design principles

---

## 📄 License

MIT License - See root [LICENSE](../LICENSE) file

---

<div align="center">

**Modern Frontend for Enterprise Risk Management**

Built with ❤️ for Niyati

[⬆ back to top](#niyati-frontend---risk-intelligence-dashboard)

</div>
