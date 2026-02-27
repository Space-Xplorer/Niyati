'use client';

import React, { useEffect, useState } from 'react';
import { VendorRiskTable } from './VendorRiskTable';
import { AgentLogViewer } from './AgentLogViewer';

interface SystemHealthMetrics {
  overall_health_score: number;
  total_taxpayers: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  fraud_patterns: {
    circular_trade: number;
    ghost_invoices: number;
    spider_web_involvement: boolean;
    circular_entities?: Array<{ gstin: string; partner_gstin: string; pattern: string }>;
    ghost_entities?: Array<{ gstin: string; ghost_invoice_count: number; pattern: string }>;
    spider_entities?: Array<{ gstin: string; shared_contact_count: number; pattern: string }>;
  };
  recent_activity: {
    last_ingestion: string;
    records_processed_today: number;
    alerts_generated_today: number;
  };
  data_source?: string;
}

interface VendorRisk {
  vendor_gstin: string;
  vendor_name: string;
  risk_level: string;
  itc_at_risk: number;
  last_transaction_date: string;
}

interface AdminDashboardProps {
  token: string;
  onLogout: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ token, onLogout }) => {
  const [metrics, setMetrics] = useState<SystemHealthMetrics | null>(null);
  const [vendors, setVendors] = useState<VendorRisk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFraudTab, setSelectedFraudTab] = useState<'circular' | 'ghost' | 'spider'>('circular');

  useEffect(() => {
    fetchDashboardData();
  }, [token]);

  const fetchDashboardData = async () => {
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

      console.log('Admin dashboard data received:', result);

      setMetrics({
        overall_health_score: result.health_score || 75,
        total_taxpayers: result.total_taxpayers || 0,
        high_risk_count: result.high_risk_count || 0,
        medium_risk_count: result.medium_risk_count || 0,
        low_risk_count: result.low_risk_count || 0,
        fraud_patterns: {
          circular_trade: result.patterns?.circular_trade || 0,
          ghost_invoices: result.patterns?.ghost_invoices || 0,
          spider_web_involvement: result.patterns?.spider_web_involvement || false,
          circular_entities: result.patterns?.circular_entities || [],
          ghost_entities: result.patterns?.ghost_entities || [],
          spider_entities: result.patterns?.spider_entities || []
        },
        recent_activity: {
          last_ingestion: new Date().toISOString(),
          records_processed_today: result.total_taxpayers || 0,
          alerts_generated_today: result.high_risk_count || 0,
        },
        data_source: result.data_source || 'unknown',
      });

      setVendors(result.vendor_risks || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

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

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error: {error}</p>
          <button
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f7faf9]">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-[#04221f]">Project Niyati - Admin Dashboard</h1>
            <p className="text-[#005b52]/70 mt-2">Government Officer - System-Wide View</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => window.location.href = '/'}
              className="text-sm bg-white border border-[#005b52]/20 hover:bg-[#005b52]/5 text-[#04221f] px-4 py-2 rounded-lg font-medium transition"
            >
              Home
            </button>
            <button
              onClick={() => window.location.href = '/graph'}
              className="text-sm bg-[#dbf226] hover:bg-[#c4da1e] border border-[#04221f]/10 text-[#04221f] px-4 py-2 rounded-lg font-medium shadow-md shadow-black/5 transition"
            >
              Network Graph
            </button>
            <button
              onClick={onLogout}
              className="text-sm bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium shadow-md transition"
            >
              Logout
            </button>
          </div>
        </div>

        {/* System Health Overview */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-[#04221f] mb-4">System Health Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Overall Health Score"
              value={metrics.overall_health_score}
              suffix="/100"
              color={getHealthColor(metrics.overall_health_score)}
            />
            <MetricCard
              title="Total Taxpayers"
              value={metrics.total_taxpayers}
              color="blue"
            />
            <MetricCard
              title="Records Processed Today"
              value={metrics.recent_activity.records_processed_today}
              color="green"
            />
            <MetricCard
              title="Alerts Generated Today"
              value={metrics.recent_activity.alerts_generated_today}
              color="orange"
            />
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-[#04221f] mb-4">Risk Distribution</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <RiskCard
              title="High Risk"
              count={metrics.high_risk_count}
              percentage={(metrics.high_risk_count / metrics.total_taxpayers * 100).toFixed(1)}
              color="red"
            />
            <RiskCard
              title="Medium Risk"
              count={metrics.medium_risk_count}
              percentage={(metrics.medium_risk_count / metrics.total_taxpayers * 100).toFixed(1)}
              color="yellow"
            />
            <RiskCard
              title="Low Risk"
              count={metrics.low_risk_count}
              percentage={(metrics.low_risk_count / metrics.total_taxpayers * 100).toFixed(1)}
              color="green"
            />
          </div>
        </div>

        {/* Fraud Pattern Detection */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-[#04221f] mb-4">Structural Fraud Patterns Detected</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <FraudPatternCard
              title="Circular Trade"
              count={metrics.fraud_patterns.circular_trade}
              description="Entities involved in circular trading patterns"
              color="red"
              onClick={() => setSelectedFraudTab('circular')}
              isActive={selectedFraudTab === 'circular'}
            />
            <FraudPatternCard
              title="Ghost Invoices"
              count={metrics.fraud_patterns.ghost_invoices}
              description="Invoices without corresponding e-way bills"
              color="purple"
              onClick={() => setSelectedFraudTab('ghost')}
              isActive={selectedFraudTab === 'ghost'}
            />
            <FraudPatternCard
              title="Spider Web Networks"
              count={metrics.fraud_patterns.spider_entities?.length || 0}
              description="Complex interconnected fraud networks"
              color="orange"
              onClick={() => setSelectedFraudTab('spider')}
              isActive={selectedFraudTab === 'spider'}
            />
          </div>

          {/* Fraud Details Table */}
          <FraudDetailsTable
            selectedTab={selectedFraudTab}
            circularEntities={metrics.fraud_patterns.circular_entities || []}
            ghostEntities={metrics.fraud_patterns.ghost_entities || []}
            spiderEntities={metrics.fraud_patterns.spider_entities || []}
          />
        </div>

        {/* Vendor Risk Table */}
        <div className="mb-8">
          <VendorRiskTable vendors={vendors} />
        </div>

        {/* Agent Activity Log */}
        <div className="mb-8">
          <AgentLogViewer />
        </div>

        {/* Placeholder Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <PlaceholderCard
            title="Neo4j Network Visualization"
            description="Interactive graph visualization showing entity relationships and fraud patterns"
            actionText="View Full Graph"
            actionLink="/graph"
          />
          <PlaceholderCard
            title="EBM SHAP Analysis"
            description="Explainable AI insights showing top risk drivers and feature contributions"
            actionText="View Analysis"
            actionLink="/dashboard"
          />
        </div>

        {/* System Status Footer */}
        <div className="bg-white rounded-2xl shadow-xl shadow-black/5 border border-[#005b52]/10 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-sm text-gray-600">System Operational</span>
              </div>
              <div className="text-sm text-gray-600">
                Last Ingestion: {new Date(metrics.recent_activity.last_ingestion).toLocaleString()}
              </div>
              {metrics.data_source && (
                <div className="text-sm text-gray-600">
                  Data Source: <span className="font-semibold text-blue-600">
                    {metrics.data_source === 'neo4j_computed' ? 'NEO4J (Computed On-The-Fly)' :
                      metrics.data_source === 'hybrid' ? 'SQLITE (Risk) + NEO4J (Graph)' :
                        metrics.data_source === 'sqlite' ? 'SQLITE (Risk Predictions)' :
                          metrics.data_source.toUpperCase()}
                  </span>
                </div>
              )}
            </div>
            <button
              onClick={fetchDashboardData}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Refresh Data
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper Components

interface MetricCardProps {
  title: string;
  value: number;
  suffix?: string;
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, suffix = '', color }) => {
  const colorClasses = {
    red: 'bg-red-50 border-red-200 text-red-700',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    orange: 'bg-orange-50 border-orange-200 text-orange-700',
  };

  return (
    <div className={`rounded-lg border-2 p-6 ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="text-3xl font-bold mb-1">
        {value}{suffix}
      </div>
      <div className="text-sm opacity-80">{title}</div>
    </div>
  );
};

interface RiskCardProps {
  title: string;
  count: number;
  percentage: string;
  color: 'red' | 'yellow' | 'green';
}

const RiskCard: React.FC<RiskCardProps> = ({ title, count, percentage, color }) => {
  const colorClasses = {
    red: 'bg-red-50 border-red-300',
    yellow: 'bg-yellow-50 border-yellow-300',
    green: 'bg-green-50 border-green-300',
  };

  const textColorClasses = {
    red: 'text-red-700',
    yellow: 'text-yellow-700',
    green: 'text-green-700',
  };

  return (
    <div className={`rounded-lg border-2 p-6 ${colorClasses[color]}`}>
      <h3 className={`text-lg font-semibold mb-3 ${textColorClasses[color]}`}>{title}</h3>
      <div className="flex items-baseline space-x-2">
        <span className={`text-4xl font-bold ${textColorClasses[color]}`}>{count}</span>
        <span className={`text-xl ${textColorClasses[color]} opacity-70`}>({percentage}%)</span>
      </div>
    </div>
  );
};

interface FraudPatternCardProps {
  title: string;
  count: number;
  description: string;
  color: string;
  onClick: () => void;
  isActive: boolean;
}

const FraudPatternCard: React.FC<FraudPatternCardProps> = ({ title, count, description, color, onClick, isActive }) => {
  const colorClasses = {
    red: 'border-red-300 bg-red-50',
    purple: 'border-purple-300 bg-purple-50',
    orange: 'border-orange-300 bg-orange-50',
  };

  const badgeColorClasses = {
    red: 'bg-red-600',
    purple: 'bg-purple-600',
    orange: 'bg-orange-600',
  };

  return (
    <button
      onClick={onClick}
      className={`rounded-lg border-2 p-6 text-left transition-all ${colorClasses[color as keyof typeof colorClasses]} ${isActive ? 'ring-2 ring-blue-500 shadow-lg' : 'hover:shadow-md'
        }`}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <span className={`inline-flex items-center justify-center min-w-[2.5rem] h-10 px-3 rounded-full ${badgeColorClasses[color as keyof typeof badgeColorClasses]} text-white text-lg font-bold`}>
          {count}
        </span>
      </div>
      <p className="text-sm text-gray-600">{description}</p>
    </button>
  );
};

interface FraudDetailsTableProps {
  selectedTab: 'circular' | 'ghost' | 'spider';
  circularEntities: Array<{ gstin: string; partner_gstin: string; pattern: string }>;
  ghostEntities: Array<{ gstin: string; ghost_invoice_count: number; pattern: string }>;
  spiderEntities: Array<{ gstin: string; shared_contact_count: number; pattern: string }>;
}

const FraudDetailsTable: React.FC<FraudDetailsTableProps> = ({
  selectedTab,
  circularEntities,
  ghostEntities,
  spiderEntities
}) => {
  return (
    <div className="bg-white rounded-2xl shadow-xl shadow-black/5 border border-[#005b52]/10 overflow-hidden">
      <div className="px-6 py-4 border-b border-[#005b52]/5">
        <h3 className="text-lg font-semibold text-gray-900">
          {selectedTab === 'circular' && 'Circular Trade Entities'}
          {selectedTab === 'ghost' && 'Ghost Invoice Entities'}
          {selectedTab === 'spider' && 'Spider Web Network Entities'}
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                GSTIN
              </th>
              {selectedTab === 'circular' && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Partner GSTIN
                </th>
              )}
              {selectedTab === 'ghost' && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ghost Invoice Count
                </th>
              )}
              {selectedTab === 'spider' && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Shared Contacts
                </th>
              )}
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Pattern Type
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {selectedTab === 'circular' && circularEntities.map((entity, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {entity.gstin}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {entity.partner_gstin}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                    {entity.pattern}
                  </span>
                </td>
              </tr>
            ))}
            {selectedTab === 'ghost' && ghostEntities.map((entity, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {entity.gstin}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {entity.ghost_invoice_count}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                    {entity.pattern}
                  </span>
                </td>
              </tr>
            ))}
            {selectedTab === 'spider' && spiderEntities.map((entity, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {entity.gstin}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {entity.shared_contact_count}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-orange-100 text-orange-800">
                    {entity.pattern}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

interface PlaceholderCardProps {
  title: string;
  description: string;
  actionText: string;
  actionLink: string;
}

const PlaceholderCard: React.FC<PlaceholderCardProps> = ({ title, description, actionText, actionLink }) => {
  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-200 p-6">
      <div className="flex items-start space-x-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
          <p className="text-sm text-gray-600 mb-4">{description}</p>
          <button
            onClick={() => window.location.href = actionLink}
            className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition"
          >
            {actionText}
          </button>
        </div>
      </div>
    </div>
  );
};

const getHealthColor = (score: number): string => {
  if (score >= 70) return 'green';
  if (score >= 40) return 'yellow';
  return 'red';
};
