'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { HealthGauge } from '@/components/HealthGauge';
import { RiskBadge } from '@/components/RiskBadge';
import { ShapePlots } from '@/components/ShapePlots';
import { VendorRiskTable } from '@/components/VendorRiskTable';
import { AgentLogViewer } from '@/components/AgentLogViewer';
import { AdminDashboard } from '@/components/AdminDashboard';

interface DashboardData {
  gstin?: string;
  health_score: number;
  risk_level: 'HIGH_RISK' | 'MEDIUM_RISK' | 'LOW_RISK';
  risk_probability: number;
  top_drivers: Array<{
    feature: string;
    contribution: number;
    direction: string;
  }>;
  vendor_risks: Array<{
    vendor_gstin: string;
    vendor_name: string;
    risk_level: string;
    itc_at_risk: number;
    last_transaction_date: string;
  }>;
  patterns: {
    circular_trade: number;
    ghost_invoices: number;
    spider_web_involvement: boolean;
  };
  explanation?: string;
  fraud_details?: {
    circular_trade_partners?: string[];
    ghost_invoice_count?: number;
    shared_contact_count?: number;
  };
}

export default function DashboardPage() {
  const { token, user, logout } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is admin (case-insensitive)
  const isAdmin = user?.role?.toLowerCase() === 'admin';

  useEffect(() => {
    // Skip fetching if admin (AdminDashboard handles its own data)
    if (isAdmin) {
      setLoading(false);
      return;
    }

    const fetchDashboard = async () => {
      if (!token) return;

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
        const response = await fetch(`${apiUrl}/dashboard`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.status === 401) {
          // Token expired or invalid, logout user
          logout();
          return;
        }

        if (!response.ok) {
          throw new Error('Failed to fetch dashboard data');
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [token, logout, isAdmin]);

  // Render AdminDashboard for admin users (after hooks, but check loading first)
  if (isAdmin && user && token) {
    if (loading) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading admin dashboard...</p>
          </div>
        </div>
      );
    }
    return <AdminDashboard token={token} onLogout={logout} />;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#04221f] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#dbf226] mx-auto"></div>
          <p className="mt-4 text-[#dbf226]/70">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Error: {error}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white font-sans selection:bg-[#005b52] selection:text-white">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-serif font-bold text-[#04221f]">Trust Dashboard</h1>
            <p className="text-[#005b52]/70 mt-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#005b52] animate-pulse"></span>
              GSTIN: <span className="font-mono text-[#04221f]">{user?.gstin || user?.email}</span>
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => window.location.href = '/'}
              className="text-sm bg-[#f7faf9] border border-[#005b52]/10 hover:bg-[#005b52]/5 text-[#04221f] px-5 py-2.5 rounded-full font-semibold transition-all"
            >
              Home
            </button>
            <button
              onClick={() => window.location.href = '/graph'}
              className="text-sm bg-[#005b52] hover:bg-[#04221f] text-[#dbf226] px-5 py-2.5 rounded-full font-bold transition-all shadow-[0_4_14px_0_rgba(0,0,0,0.1)] hover:-translate-y-0.5"
            >
              View Graph
            </button>
            <button
              onClick={() => window.location.href = '/upload'}
              className="text-sm bg-[#f7faf9] hover:bg-[#005b52]/5 border border-[#005b52]/10 text-[#04221f] px-5 py-2.5 rounded-full font-semibold transition-all"
            >
              Upload Data
            </button>
            <button
              onClick={logout}
              className="text-sm bg-red-50 text-red-600 border border-red-100 hover:bg-red-100 px-5 py-2.5 rounded-full font-semibold transition-all"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Health Score and Risk Level */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-[#f7faf9] rounded-3xl border border-[#005b52]/10 shadow-xl p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center text-xl shadow-sm">⚕️</div>
              <h2 className="text-xl font-bold text-[#04221f] tracking-wide">Health Score</h2>
            </div>
            <HealthGauge score={data.health_score} />
          </div>
          <div className="bg-[#f7faf9] rounded-3xl border border-[#005b52]/10 shadow-xl p-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center text-xl shadow-sm">🎯</div>
              <h2 className="text-xl font-bold text-[#04221f] tracking-wide">Risk Assessment</h2>
            </div>
            <RiskBadge level={data.risk_level} probability={data.risk_probability} />
            <div className="mt-8 space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-[#005b52]/5 group">
                <span className="text-[#005b52]/70 group-hover:text-[#005b52] transition-colors">Circular Trade Patterns</span>
                <span className="font-mono text-lg font-bold text-[#04221f]">{data.patterns?.circular_trade ?? 0}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-[#005b52]/5 group">
                <span className="text-[#005b52]/70 group-hover:text-[#005b52] transition-colors">Ghost Invoices</span>
                <span className="font-mono text-lg font-bold text-[#04221f]">{data.patterns?.ghost_invoices ?? 0}</span>
              </div>
              <div className="flex justify-between items-center py-3 group">
                <span className="text-[#005b52]/70 group-hover:text-[#005b52] transition-colors">Spider Web Involvement</span>
                {data.patterns?.spider_web_involvement ? (
                  <span className="bg-red-50 text-red-600 border border-red-200 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">Detected</span>
                ) : (
                  <span className="bg-green-50 text-green-600 border border-green-200 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">Clear</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Shape Plots */}
        <div className="mb-8">
          <ShapePlots gstin={data.gstin || user?.gstin || ''} token={token || ''} />
        </div>

        {/* Detailed Explanation */}
        {data.explanation && (
          <div className="mb-8 opacity-0 animate-[slideDown_0.5s_ease-out_forwards] animation-delay-200">
            <div className="bg-[#f7faf9] rounded-3xl border border-[#005b52]/10 shadow-xl p-8 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-50 rounded-full blur-[80px] group-hover:bg-emerald-100 transition-colors duration-500 pointer-events-none"></div>
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center text-xl shadow-sm border border-emerald-200">🤖</div>
                  <h2 className="text-xl font-bold text-[#04221f] tracking-wide">AI Narrative Assessment</h2>
                </div>
                <pre className="whitespace-pre-wrap text-[15px] leading-relaxed text-[#005b52]/80 font-mono bg-white p-6 rounded-2xl border border-[#005b52]/10 shadow-sm">
                  {data.explanation}
                </pre>
              </div>
            </div>
          </div>
        )}

        {/* Fraud Details */}
        {data.fraud_details && (data.fraud_details.circular_trade_partners?.length || 0) > 0 && (
          <div className="mb-8 opacity-0 animate-[slideDown_0.5s_ease-out_forwards] animation-delay-300">
            <div className="bg-red-50 border border-red-200 rounded-3xl p-8 shadow-xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-linear-to-r from-red-500 via-red-400 to-transparent"></div>

              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center text-red-600 border border-red-200 animate-pulse">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                </div>
                <h2 className="text-2xl font-bold text-red-700 tracking-tight">Fraud Alert: Circular Trade Detected</h2>
              </div>

              <p className="text-red-900/80 text-lg mb-6 leading-relaxed">
                Graph analysis has identified your business participating in a closed-loop transaction cycle with the following entities:
              </p>

              <div className="bg-white rounded-2xl p-6 border border-red-100 mb-6 shadow-sm">
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {data.fraud_details.circular_trade_partners?.map((partner, idx) => (
                    <div key={idx} className="flex items-center gap-3 bg-red-50/50 border border-red-100 px-4 py-3 rounded-xl">
                      <div className="w-2 h-2 rounded-full bg-red-500"></div>
                      <span className="font-mono text-red-900 font-medium">{partner}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-red-100 border-l-4 border-red-500 p-4 rounded-r-xl">
                <p className="text-red-800">
                  <strong className="text-red-700">Action Required:</strong> Circular trade is a primary indicator of ITC fraud. Immediate review of the aforementioned transaction chain is advised.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Vendor Risk Table */}
        <div className="mb-8">
          <VendorRiskTable vendors={data.vendor_risks} />
        </div>

        {/* Agent Log Viewer */}
        <div>
          <AgentLogViewer />
        </div>
      </div>
    </div>
  );
}
