'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/Button';
import { useAuth } from '@/context/AuthContext';

export default function Home() {
  const router = useRouter();
  const { token, user, logout } = useAuth();

  return (
    <main className="min-h-screen" style={{ backgroundColor: '#efefef' }}>
      {/* Navigation */}
      <nav className="border-b" style={{ borderColor: '#d0d0d0', backgroundColor: '#ffffff' }}>
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold" style={{ color: '#005b52' }}>
            Niyati
          </h1>
          <div className="flex gap-3">
            {token ? (
              <>
                <button
                  onClick={() => router.push('/dashboard')}
                  className="px-4 py-2 rounded-lg font-medium transition-all"
                  style={{
                    backgroundColor: 'transparent',
                    color: '#005b52',
                    border: '2px solid #005b52'
                  }}
                >
                  Dashboard
                </button>
                <button
                  onClick={logout}
                  className="px-4 py-2 rounded-lg font-medium transition-all"
                  style={{
                    backgroundColor: '#dbf226',
                    color: '#005b52',
                    border: '2px solid #dbf226'
                  }}
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => router.push('/login')}
                  className="px-4 py-2 rounded-lg font-medium transition-all"
                  style={{
                    backgroundColor: 'transparent',
                    color: '#005b52',
                    border: '2px solid #005b52'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#005b52';
                    e.currentTarget.style.color = '#ffffff';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = '#005b52';
                  }}
                >
                  Login
                </button>
                <Button onClick={() => router.push('/signup')}>
                  Get Started
                </Button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 text-center">
        <h2 className="text-5xl md:text-6xl font-extrabold mb-6" style={{ color: '#005b52' }}>
          Real-time GST Intelligence & Fraud Detection
        </h2>
        <p className="text-xl md:text-2xl mb-8" style={{ color: '#1a1a1a', opacity: 0.8 }}>
          A Shadow Mirror of India's GST Network powered by Knowledge Graphs and Explainable AI
        </p>
        <div className="flex gap-4 justify-center">
          <Button onClick={() => router.push('/signup')}>
            Start Free Trial
          </Button>
          <button
            onClick={() => router.push('/login')}
            className="px-6 py-3 rounded-lg font-medium transition-all"
            style={{
              backgroundColor: 'transparent',
              color: '#005b52',
              border: '2px solid #005b52'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#005b52';
              e.currentTarget.style.color = '#ffffff';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = '#005b52';
            }}
          >
            View Demo
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <h3 className="text-3xl font-bold text-center mb-12" style={{ color: '#005b52' }}>
          Powered by Five Intelligent Agents
        </h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Agent 1 */}
          <div className="p-6 rounded-xl" style={{ backgroundColor: '#ffffff', border: '1px solid #d0d0d0' }}>
            <div className="w-12 h-12 rounded-lg mb-4 flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
              <span className="text-2xl font-bold" style={{ color: '#005b52' }}>1</span>
            </div>
            <h4 className="text-xl font-bold mb-2" style={{ color: '#005b52' }}>Ingestion Wrangler</h4>
            <p style={{ color: '#1a1a1a', opacity: 0.7 }}>
              Validates and cleans GST transaction data from six CSV sources with automated feature engineering
            </p>
          </div>

          {/* Agent 2 */}
          <div className="p-6 rounded-xl" style={{ backgroundColor: '#ffffff', border: '1px solid #d0d0d0' }}>
            <div className="w-12 h-12 rounded-lg mb-4 flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
              <span className="text-2xl font-bold" style={{ color: '#005b52' }}>2</span>
            </div>
            <h4 className="text-xl font-bold mb-2" style={{ color: '#005b52' }}>Graph Architect</h4>
            <p style={{ color: '#1a1a1a', opacity: 0.7 }}>
              Builds a comprehensive Neo4j knowledge graph connecting taxpayers, invoices, and e-way bills
            </p>
          </div>

          {/* Agent 3 */}
          <div className="p-6 rounded-xl" style={{ backgroundColor: '#ffffff', border: '1px solid #d0d0d0' }}>
            <div className="w-12 h-12 rounded-lg mb-4 flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
              <span className="text-2xl font-bold" style={{ color: '#005b52' }}>3</span>
            </div>
            <h4 className="text-xl font-bold mb-2" style={{ color: '#005b52' }}>Risk Detective</h4>
            <p style={{ color: '#1a1a1a', opacity: 0.7 }}>
              Detects circular trading patterns, ghost invoices, and spider web networks through graph analysis
            </p>
          </div>

          {/* Agent 4 */}
          <div className="p-6 rounded-xl" style={{ backgroundColor: '#ffffff', border: '1px solid #d0d0d0' }}>
            <div className="w-12 h-12 rounded-lg mb-4 flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
              <span className="text-2xl font-bold" style={{ color: '#005b52' }}>4</span>
            </div>
            <h4 className="text-xl font-bold mb-2" style={{ color: '#005b52' }}>Predictive Analyst</h4>
            <p style={{ color: '#1a1a1a', opacity: 0.7 }}>
              Uses Explainable Boosting Machines to predict fraud risk with transparent feature contributions
            </p>
          </div>

          {/* Agent 5 */}
          <div className="p-6 rounded-xl" style={{ backgroundColor: '#ffffff', border: '1px solid #d0d0d0' }}>
            <div className="w-12 h-12 rounded-lg mb-4 flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
              <span className="text-2xl font-bold" style={{ color: '#005b52' }}>5</span>
            </div>
            <h4 className="text-xl font-bold mb-2" style={{ color: '#005b52' }}>Niyati Explainer</h4>
            <p style={{ color: '#1a1a1a', opacity: 0.7 }}>
              Generates plain-language audit narratives using LLMs for non-technical stakeholders
            </p>
          </div>

          {/* Orchestration */}
          <div className="p-6 rounded-xl" style={{ backgroundColor: '#005b52', border: '1px solid #005b52' }}>
            <div className="w-12 h-12 rounded-lg mb-4 flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
              <span className="text-2xl font-bold" style={{ color: '#005b52' }}>⚡</span>
            </div>
            <h4 className="text-xl font-bold mb-2" style={{ color: '#dbf226' }}>LangGraph Orchestration</h4>
            <p style={{ color: '#ffffff', opacity: 0.9 }}>
              Coordinates all agents in a seamless workflow with real-time observability and error recovery
            </p>
          </div>
        </div>
      </section>

      {/* Detection Capabilities */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <h3 className="text-3xl font-bold text-center mb-12" style={{ color: '#005b52' }}>
          What We Detect
        </h3>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
              <span className="text-3xl">🔄</span>
            </div>
            <h4 className="text-xl font-bold mb-2" style={{ color: '#005b52' }}>Circular Trading</h4>
            <p style={{ color: '#1a1a1a', opacity: 0.7 }}>
              Identifies transaction loops where A → B → C → A to detect ITC fraud schemes
            </p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
              <span className="text-3xl">👻</span>
            </div>
            <h4 className="text-xl font-bold mb-2" style={{ color: '#005b52' }}>Ghost Invoices</h4>
            <p style={{ color: '#1a1a1a', opacity: 0.7 }}>
              Flags high-value invoices without corresponding e-way bills indicating fake transactions
            </p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
              <span className="text-3xl">🕸️</span>
            </div>
            <h4 className="text-xl font-bold mb-2" style={{ color: '#005b52' }}>Spider Web Networks</h4>
            <p style={{ color: '#1a1a1a', opacity: 0.7 }}>
              Discovers clusters of entities sharing contact information to uncover shell companies
            </p>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <div className="rounded-2xl p-12" style={{ backgroundColor: '#005b52' }}>
          <h3 className="text-3xl font-bold text-center mb-8" style={{ color: '#dbf226' }}>
            Why Choose Niyati?
          </h3>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
                  <span style={{ color: '#005b52' }}>✓</span>
                </div>
              </div>
              <div>
                <h4 className="font-bold mb-2" style={{ color: '#ffffff' }}>Explainable AI</h4>
                <p style={{ color: '#ffffff', opacity: 0.8 }}>
                  Understand exactly why an entity is flagged with transparent feature contributions
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
                  <span style={{ color: '#005b52' }}>✓</span>
                </div>
              </div>
              <div>
                <h4 className="font-bold mb-2" style={{ color: '#ffffff' }}>Role-Based Access</h4>
                <p style={{ color: '#ffffff', opacity: 0.8 }}>
                  Admins see everything, business owners see only their data and vendor risks
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
                  <span style={{ color: '#005b52' }}>✓</span>
                </div>
              </div>
              <div>
                <h4 className="font-bold mb-2" style={{ color: '#ffffff' }}>Real-Time Monitoring</h4>
                <p style={{ color: '#ffffff', opacity: 0.8 }}>
                  Watch agent execution in real-time with Server-Sent Events streaming
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: '#dbf226' }}>
                  <span style={{ color: '#005b52' }}>✓</span>
                </div>
              </div>
              <div>
                <h4 className="font-bold mb-2" style={{ color: '#ffffff' }}>PII Protection</h4>
                <p style={{ color: '#ffffff', opacity: 0.8 }}>
                  All sensitive data is hashed before storage with SHA-256 encryption
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-4xl mx-auto px-6 py-20 text-center">
        <h3 className="text-4xl font-bold mb-6" style={{ color: '#005b52' }}>
          Ready to Detect GST Fraud?
        </h3>
        <p className="text-xl mb-8" style={{ color: '#1a1a1a', opacity: 0.8 }}>
          Join auditors and business owners using Niyati to protect their GST compliance
        </p>
        <Button onClick={() => router.push('/signup')}>
          Create Free Account
        </Button>
      </section>

      {/* Footer */}
      <footer className="border-t py-8" style={{ borderColor: '#d0d0d0', backgroundColor: '#ffffff' }}>
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p style={{ color: '#1a1a1a', opacity: 0.6 }}>
            © 2026 Project Niyati. Real-time GST Intelligence & Fraud Detection Platform.
          </p>
        </div>
      </footer>
    </main>
  );
}
