'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { HealthGauge } from '@/components/HealthGauge';
import { RiskBadge } from '@/components/RiskBadge';
import { ShapePlots } from '@/components/ShapePlots';
import { VendorRiskTable } from '@/components/VendorRiskTable';
import { AgentLogViewer } from '@/components/AgentLogViewer';

interface DashboardData {
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
}

export default function DashboardPage() {
  const { token, user } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      if (!token) return;

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
        const response = await fetch(`${apiUrl}/dashboard`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

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
  }, [token]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
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
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Trust Dashboard</h1>
            <p className="text-gray-600 mt-2">
              {user?.role === 'admin' ? 'Global View' : `GSTIN: ${user?.email}`}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => window.location.href = '/'}
              className="text-sm bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded transition"
            >
              Home
            </button>
            <button
              onClick={() => window.location.href = '/graph'}
              className="text-sm bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded transition"
            >
              View Graph
            </button>
          </div>
        </div>

        {/* Health Score and Risk Level */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Health Score</h2>
            <HealthGauge score={data.health_score} />
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Level</h2>
            <RiskBadge level={data.risk_level} probability={data.risk_probability} />
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Circular Trade Patterns:</span>
                <span className="font-medium">{data.patterns.circular_trade}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Ghost Invoices:</span>
                <span className="font-medium">{data.patterns.ghost_invoices}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Spider Web Involvement:</span>
                <span className="font-medium">{data.patterns.spider_web_involvement ? 'Yes' : 'No'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Shape Plots */}
        <div className="mb-8">
          <ShapePlots gstin={user?.email || ''} token={token || ''} />
        </div>

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
