'use client';

import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface ShapePlotData {
  feature_name?: string;
  contribution_weight?: number;
  feature_value?: number;
  baseline_value?: number;
  direction?: 'positive' | 'negative';
}

interface ShapePlotsProps {
  gstin: string;
  token: string;
}

export const ShapePlots: React.FC<ShapePlotsProps> = ({ gstin, token }) => {
  const [shapePlots, setShapePlots] = useState<ShapePlotData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchShapePlots = async () => {
      if (!token || !gstin) return;

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
        const response = await fetch(`${apiUrl}/risk/${gstin}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch shape plot data');
        }

        const result = await response.json();
        // Backend returns shape_plots (with feature_name/feature_value/baseline_value/contribution_weight)
        // top_drivers uses different keys (feature/contribution) — not compatible with ShapePlotData
        setShapePlots(result.shape_plots || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchShapePlots();
  }, [gstin, token]);

  if (loading) {
    return (
      <div className="bg-[#f7faf9] border border-[#005b52]/10 rounded-3xl shadow-xl p-8">
        <h2 className="text-xl font-bold text-[#04221f] tracking-wide mb-6">Top Risk Drivers</h2>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[#005b52]"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-[#f7faf9] border border-[#005b52]/10 rounded-3xl shadow-xl p-8">
        <h2 className="text-xl font-bold text-[#04221f] tracking-wide mb-6">Top Risk Drivers</h2>
        <p className="text-red-500 text-sm font-medium">{error}</p>
      </div>
    );
  }

  if (shapePlots.length === 0) {
    return (
      <div className="bg-[#f7faf9] border border-[#005b52]/10 rounded-3xl shadow-xl p-8">
        <h2 className="text-xl font-bold text-[#04221f] tracking-wide mb-6">Top Risk Drivers</h2>
        <p className="text-gray-500 text-sm font-medium">No risk driver data available</p>
      </div>
    );
  }

  return (
    <div className="bg-[#f7faf9] border border-[#005b52]/10 rounded-3xl shadow-xl p-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center text-xl shadow-sm border border-[#005b52]/5">📊</div>
        <h2 className="text-xl font-bold text-[#04221f] tracking-wide">Top Risk Drivers</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {shapePlots.slice(0, 3).map((plot, index) => (
          <ShapePlotCard key={index} data={plot} rank={index + 1} />
        ))}
      </div>
    </div>
  );
};

interface ShapePlotCardProps {
  data: ShapePlotData;
  rank: number;
}

const ShapePlotCard: React.FC<ShapePlotCardProps> = ({ data, rank }) => {
  // Infer direction from contribution_weight sign if direction field is missing
  const inferredDirection: 'positive' | 'negative' =
    data.direction ?? ((data.contribution_weight ?? 0) >= 0 ? 'positive' : 'negative');
  const isPositive = inferredDirection === 'positive';
  const color = isPositive ? '#f87171' : '#34d399'; // red-400 for positive, emerald-400 for negative
  const arrow = isPositive ? '↑' : '↓';

  // Format feature name for display — guard against undefined/null
  const formatFeatureName = (name: string | undefined | null): string => {
    if (!name) return 'Unknown Feature';
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Create chart data comparing feature value to baseline
  const chartData = [
    {
      name: 'Baseline',
      value: data.baseline_value,
      fill: 'rgba(0,91,82,0.1)', // transluscent teal for baseline
    },
    {
      name: 'Current',
      value: data.feature_value,
      fill: color,
    },
  ];

  return (
    <div className="bg-white border border-[#005b52]/10 rounded-2xl p-5 hover:shadow-md transition-shadow relative overflow-hidden group">
      {/* Subtle glow on hover */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-[#005b52]/5 rounded-full blur-[50px] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>

      {/* Rank badge */}
      <div className="flex items-center justify-between mb-4 relative z-10">
        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#f7faf9] text-[#005b52] border border-[#005b52]/10 text-sm font-bold shadow-sm">
          #{rank}
        </span>
        <span
          className="text-2xl font-bold tracking-tight drop-shadow-sm"
          style={{ color }}
        >
          {arrow} {Math.abs((data.contribution_weight ?? 0) * 100).toFixed(1)}%
        </span>
      </div>

      {/* Feature name */}
      <h3 className="text-base font-bold text-[#04221f] mb-4 relative z-10 truncate" title={formatFeatureName(data.feature_name)}>
        {formatFeatureName(data.feature_name)}
      </h3>

      {/* Values comparison */}
      <div className="mb-6 space-y-2 relative z-10">
        <div className="flex justify-between items-center text-sm">
          <span className="text-[#005b52]/60">Current Value</span>
          <span className="font-mono text-[#04221f] font-bold bg-[#f7faf9] px-2 py-0.5 rounded">{(data.feature_value ?? 0).toFixed(2)}</span>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span className="text-[#005b52]/60">Baseline</span>
          <span className="font-mono text-[#04221f] font-bold bg-[#f7faf9] px-2 py-0.5 rounded">{(data.baseline_value ?? 0).toFixed(2)}</span>
        </div>
        <div className="flex justify-between items-center text-sm pt-2 border-t border-[#005b52]/10">
          <span className="text-[#005b52]/60">Impact Indicator</span>
          <span className="font-medium px-2 py-0.5 rounded text-xs uppercase tracking-wider font-bold" style={{ backgroundColor: `${color}20`, color, borderColor: `${color}40`, borderWidth: '1px' }}>
            {isPositive ? 'Risk ↑' : 'Risk ↓'}
          </span>
        </div>
      </div>

      {/* Bar chart */}
      <div className="relative z-10">
        <ResponsiveContainer width="100%" height={100}>
          <BarChart data={chartData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={{ stroke: '#e5e7eb' }} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={{ stroke: '#e5e7eb' }} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: '0.75rem',
                fontSize: '12px',
                color: '#1f2937',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
              }}
              itemStyle={{ color: '#1f2937' }}
              cursor={{ fill: 'rgba(0,0,0,0.05)' }}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
