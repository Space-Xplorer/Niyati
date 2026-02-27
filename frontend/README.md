# Frontend Documentation

## Overview

The Project Niyati frontend is built with Next.js 15, React 19, and TailwindCSS v4. It provides a modern, responsive interface for GST fraud detection with real-time visualizations, role-based access control, and an intuitive user experience.

## Technology Stack

- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type-safe JavaScript
- **TailwindCSS v4** - Utility-first CSS framework
- **React Force Graph** - Network visualization
- **Recharts** - Chart library for shape plots
- **Server-Sent Events (SSE)** - Real-time agent updates

## Installation

### Prerequisites

- Node.js 18+ or 20+
- npm, yarn, pnpm, or bun

### Setup

1. **Install dependencies**
```bash
npm install
# or
yarn install
# or
pnpm install
```

2. **Configure environment variables**

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

3. **Run development server**
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── page.tsx              # Landing page (public)
│   │   ├── layout.tsx            # Root layout with AuthProvider
│   │   ├── globals.css           # Global styles and CSS variables
│   │   ├── not-found.tsx         # 404 page
│   │   ├── login/
│   │   │   └── page.tsx          # Login page
│   │   ├── signup/
│   │   │   └── page.tsx          # Signup page
│   │   ├── dashboard/
│   │   │   └── page.tsx          # Trust Dashboard (protected)
│   │   ├── graph/
│   │   │   └── page.tsx          # Graph visualization (protected)
│   │   └── upload/
│   │       └── page.tsx          # CSV upload (protected)
│   ├── components/               # Reusable UI components
│   │   ├── Button.tsx            # Styled button component
│   │   ├── Input.tsx             # Styled input component
│   │   ├── HealthGauge.tsx       # Health score gauge
│   │   ├── VendorRiskTable.tsx   # Vendor risk data table
│   │   ├── ShapePlots.tsx        # EBM shape plot visualization
│   │   ├── RiskBadge.tsx         # Risk level badge
│   │   └── AgentLogViewer.tsx    # SSE log viewer
│   ├── context/
│   │   └── AuthContext.tsx       # Authentication state management
│   └── proxy.ts                  # API proxy configuration
├── public/                       # Static assets
├── package.json                  # Dependencies and scripts
├── tsconfig.json                 # TypeScript configuration
├── next.config.ts                # Next.js configuration
├── postcss.config.mjs            # PostCSS configuration
└── eslint.config.mjs             # ESLint configuration
```

## Routing

### Public Routes

These routes are accessible without authentication:

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `app/page.tsx` | Landing page with product information |
| `/login` | `app/login/page.tsx` | User login form |
| `/signup` | `app/signup/page.tsx` | User registration form |

### Protected Routes

These routes require authentication (JWT token):

| Route | Component | Description | RBAC |
|-------|-----------|-------------|------|
| `/dashboard` | `app/dashboard/page.tsx` | Trust Dashboard with health score and risk metrics | Admin: All data<br>Business Owner: Own GSTIN only |
| `/graph` | `app/graph/page.tsx` | Force-directed graph visualization | Admin: Full graph<br>Business Owner: 1-hop network |
| `/upload` | `app/upload/page.tsx` | CSV file upload form | Admin: All uploads<br>Business Owner: Own data only |

## Components

### Button Component

**Location:** `src/components/Button.tsx`

Styled button with loading state and brand colors.

**Props:**
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;  // Shows spinner when true
}
```

**Usage:**
```tsx
import { Button } from '@/components/Button';

<Button onClick={handleClick} isLoading={isSubmitting}>
  Submit
</Button>
```

**Styling:**
- Background: `#dbf226` (lime yellow)
- Text: `#005b52` (dark teal)
- Hover: `#b8cc1f` (darker yellow)

---

### Input Component

**Location:** `src/components/Input.tsx`

Styled input field with focus states.

**Props:**
```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  // Standard HTML input props
}
```

**Usage:**
```tsx
import { Input } from '@/components/Input';

<Input
  type="email"
  placeholder="Enter your email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
/>
```

**Styling:**
- Background: `#ffffff` (white)
- Border: `#d0d0d0` (light gray)
- Focus: `#005b52` (dark teal)

---

### HealthGauge Component

**Location:** `src/components/HealthGauge.tsx`

Circular gauge displaying health score (0-100).

**Props:**
```typescript
interface HealthGaugeProps {
  score: number;        // 0-100
  riskLevel: string;    // "LOW_RISK", "MEDIUM_RISK", "HIGH_RISK"
}
```

**Usage:**
```tsx
import { HealthGauge } from '@/components/HealthGauge';

<HealthGauge score={78.5} riskLevel="MEDIUM_RISK" />
```

**Color Coding:**
- 0-40: Red (HIGH_RISK)
- 41-70: Yellow (MEDIUM_RISK)
- 71-100: Green (LOW_RISK)

---

### VendorRiskTable Component

**Location:** `src/components/VendorRiskTable.tsx`

Table displaying vendor risk data with sorting and filtering.

**Props:**
```typescript
interface VendorRiskTableProps {
  vendors: Array<{
    vendor_gstin: string;
    vendor_name: string;
    risk_level: string;
    itc_at_risk: number;
    last_transaction_date: string;
  }>;
}
```

**Usage:**
```tsx
import { VendorRiskTable } from '@/components/VendorRiskTable';

<VendorRiskTable vendors={vendorData} />
```

**Features:**
- Sortable columns
- Risk level badges
- Currency formatting for ITC
- Date formatting

---

### ShapePlots Component

**Location:** `src/components/ShapePlots.tsx`

Visualizes EBM feature contributions using line charts.

**Props:**
```typescript
interface ShapePlotsProps {
  shapePlots: Array<{
    feature_name: string;
    contribution_weight: number;
    feature_value: number;
    baseline_value: number;
    x_values: number[];
    y_values: number[];
  }>;
}
```

**Usage:**
```tsx
import { ShapePlots } from '@/components/ShapePlots';

<ShapePlots shapePlots={shapePlotData} />
```

**Features:**
- Line charts showing feature impact
- Color-coded by contribution (red=positive, green=negative)
- Tooltips with exact values
- Responsive design

---

### RiskBadge Component

**Location:** `src/components/RiskBadge.tsx`

Badge displaying risk level with appropriate styling.

**Props:**
```typescript
interface RiskBadgeProps {
  riskLevel: string;  // "LOW_RISK", "MEDIUM_RISK", "HIGH_RISK"
}
```

**Usage:**
```tsx
import { RiskBadge } from '@/components/RiskBadge';

<RiskBadge riskLevel="HIGH_RISK" />
```

**Styling:**
- LOW_RISK: Green background
- MEDIUM_RISK: Yellow background
- HIGH_RISK: Red background

---

### AgentLogViewer Component

**Location:** `src/components/AgentLogViewer.tsx`

Real-time log viewer using Server-Sent Events.

**Props:**
```typescript
interface AgentLogViewerProps {
  apiUrl: string;  // SSE endpoint URL
}
```

**Usage:**
```tsx
import { AgentLogViewer } from '@/components/AgentLogViewer';

<AgentLogViewer apiUrl="http://localhost:8000/logs/stream" />
```

**Features:**
- Auto-scrolling log display
- Color-coded by agent
- Error highlighting
- Connection status indicator

---

## State Management

### AuthContext

**Location:** `src/context/AuthContext.tsx`

Manages authentication state and JWT token storage.

**Context Value:**
```typescript
interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (token: string, user: User) => void;
  logout: () => void;
}

interface User {
  id: number;
  email: string;
  role: 'Admin' | 'Business_Owner';
  gstin?: string;
}
```

**Usage:**
```tsx
import { useAuth } from '@/context/AuthContext';

function MyComponent() {
  const { token, user, login, logout } = useAuth();
  
  // Check if user is authenticated
  if (!token) {
    return <div>Please log in</div>;
  }
  
  // Access user data
  return <div>Welcome, {user.email}</div>;
}
```

**Features:**
- Automatic token persistence in localStorage
- Automatic redirect to /login for unauthenticated users
- Excludes public routes (/, /login, /signup) from redirect

---

## Styling

### Color Scheme

The application uses a custom color scheme defined in `globals.css`:

```css
:root {
  --background: #efefef;      /* Light gray background */
  --foreground: #1a1a1a;      /* Dark text */
  --primary: #dbf226;         /* Lime yellow (buttons, accents) */
  --primary-dark: #b8cc1f;    /* Darker yellow (hover states) */
  --secondary: #005b52;       /* Dark teal (headings, labels) */
  --secondary-light: #007a6e; /* Lighter teal */
  --card-bg: #ffffff;         /* White cards */
  --border: #d0d0d0;          /* Light gray borders */
}
```

### TailwindCSS Configuration

TailwindCSS v4 is configured via PostCSS. Custom colors are available as utility classes:

```tsx
<div className="bg-background text-foreground">
  <button className="bg-primary text-secondary">Click me</button>
</div>
```

### Responsive Design

All components are responsive and use Tailwind's breakpoint system:

- `sm:` - 640px and up
- `md:` - 768px and up
- `lg:` - 1024px and up
- `xl:` - 1280px and up

Example:
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Responsive grid */}
</div>
```

---

## API Integration

### Making API Requests

All API requests should include the JWT token from AuthContext:

```tsx
import { useAuth } from '@/context/AuthContext';

function MyComponent() {
  const { token } = useAuth();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  const fetchData = async () => {
    const response = await fetch(`${apiUrl}/dashboard`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('API request failed');
    }
    
    const data = await response.json();
    return data;
  };
  
  // Use fetchData...
}
```

### Error Handling

```tsx
const [error, setError] = useState<string | null>(null);

try {
  const data = await fetchData();
  // Handle success
} catch (err: any) {
  setError(err.message || 'An error occurred');
}

// Display error
{error && (
  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
    {error}
  </div>
)}
```

### Loading States

```tsx
const [isLoading, setIsLoading] = useState(false);

const handleSubmit = async () => {
  setIsLoading(true);
  try {
    await fetchData();
  } finally {
    setIsLoading(false);
  }
};

<Button isLoading={isLoading} onClick={handleSubmit}>
  Submit
</Button>
```

---

## Page Details

### Landing Page (/)

**File:** `src/app/page.tsx`

**Features:**
- Hero section with tagline
- Five intelligent agents overview
- Detection capabilities showcase
- Benefits section
- Call-to-action buttons
- Public access (no authentication required)

**Sections:**
1. Navigation bar with Login/Sign Up buttons
2. Hero with main headline
3. Agent cards (5 agents + orchestration)
4. Detection capabilities (circular trading, ghost invoices, spider webs)
5. Benefits grid (explainable AI, RBAC, real-time monitoring, PII protection)
6. CTA section
7. Footer

---

### Login Page (/login)

**File:** `src/app/login/page.tsx`

**Input Fields:**
- Email (required)
- Password (required)

**Output:**
- Success: Redirects to /dashboard with JWT token stored
- Error: Displays error message (invalid credentials, server error)

**API Endpoint:** `POST /auth/login`

---

### Signup Page (/signup)

**File:** `src/app/signup/page.tsx`

**Input Fields:**
- Email (required)
- Password (required)
- Role (required) - Dropdown: "Admin" or "Business_Owner"
- GSTIN (required for Business_Owner) - 15-character string

**Output:**
- Success: Redirects to /login with success message
- Error: Displays error message (user exists, invalid role, server error)

**API Endpoint:** `POST /auth/register`

**Validation:**
- Email format validation
- Password minimum length (8 characters)
- GSTIN format validation (15 alphanumeric characters)

---

### Dashboard Page (/dashboard)

**File:** `src/app/dashboard/page.tsx`

**Authentication:** Required

**Input:** None (data fetched based on authenticated user)

**Output:**
- Health score gauge (0-100)
- Risk level badge
- Top 3 fraud drivers with contributions
- Vendor risk table
- Detected patterns summary
- Shape plots for top drivers

**API Endpoint:** `GET /dashboard`

**RBAC:**
- Admin: Sees aggregated data across all GSTINs
- Business_Owner: Sees only their GSTIN data

**Components Used:**
- HealthGauge
- RiskBadge
- VendorRiskTable
- ShapePlots

---

### Graph Page (/graph)

**File:** `src/app/graph/page.tsx`

**Authentication:** Required

**Input:** None (data fetched based on authenticated user)

**Output:**
- Force-directed graph visualization
- Nodes colored by risk level
- Interactive tooltips on hover
- Zoom and pan controls
- Legend for node colors

**API Endpoint:** `GET /graph`

**RBAC:**
- Admin: Sees entire graph (up to 1000 nodes)
- Business_Owner: Sees only their network (1-hop neighbors)

**Features:**
- Circular trade loops highlighted in red
- Node size based on transaction volume
- Edge thickness based on transaction value
- Click node to see details

---

### Upload Page (/upload)

**File:** `src/app/upload/page.tsx`

**Authentication:** Required

**Input:**
- 6 CSV file uploads:
  1. e_invoices.csv
  2. eway_bills.csv
  3. entity_master.csv
  4. filing_history.csv
  5. purchase_register.csv
  6. returns_summary.csv

**Output:**
- Upload progress indicator
- Real-time agent logs (via SSE)
- Success message with summary
- Error messages if validation fails

**API Endpoint:** `POST /sync`

**Features:**
- Drag-and-drop file upload
- File validation (CSV only)
- Progress bar during upload
- Real-time log viewer showing agent progress
- Summary of results (patterns detected, high-risk entities)

**Components Used:**
- AgentLogViewer
- Button (with loading state)

---

## Building for Production

### Build Command

```bash
npm run build
# or
yarn build
# or
pnpm build
```

This creates an optimized production build in the `.next/` directory.

### Start Production Server

```bash
npm start
# or
yarn start
# or
pnpm start
```

### Environment Variables

Ensure `NEXT_PUBLIC_API_URL` is set to your production API URL:

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Deployment Options

**Vercel (Recommended):**
```bash
vercel deploy
```

**Docker:**
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

**Static Export:**
```bash
npm run build
npm run export
```

---

## Testing

### Run Tests

```bash
npm test
# or
yarn test
```

### Run Tests in Watch Mode

```bash
npm test -- --watch
```

### Test Coverage

```bash
npm test -- --coverage
```

---

## Performance Optimization

### Image Optimization

Use Next.js Image component for automatic optimization:

```tsx
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority
/>
```

### Code Splitting

Next.js automatically code-splits by route. For additional splitting:

```tsx
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('@/components/HeavyComponent'), {
  loading: () => <div>Loading...</div>,
  ssr: false
});
```

### Caching

API responses can be cached using Next.js fetch cache:

```tsx
const data = await fetch(url, {
  next: { revalidate: 60 } // Cache for 60 seconds
});
```

---

## Troubleshooting

### "Module not found" errors

```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

### TypeScript errors

```bash
# Regenerate TypeScript types
npm run build
```

### API connection errors

Check that:
1. Backend is running on the correct port
2. `NEXT_PUBLIC_API_URL` is set correctly
3. CORS is enabled on the backend
4. JWT token is valid and not expired

---

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

---

## Accessibility

All components follow WCAG 2.1 Level AA guidelines:
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support
- Color contrast ratios meet standards
- Focus indicators visible

---

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

---

## Support

For issues or questions, please open an issue on GitHub.
