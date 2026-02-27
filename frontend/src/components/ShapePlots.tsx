'use client';

import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface ShapePlotData {
  feature_name: string;
  contribution_weight: number;
  feature_value: number;
  baseline_value: number;
  direction: 'positive' | 'negative';
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
        setShapePlots(result.top_drivers || []);
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
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Risk Drivers</h2>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Risk Drivers</h2>
        <p className="text-red-600 text-sm">{error}</p>
      </div>
    );
  }

  if (shapePlots.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Risk Drivers</h2>
        <p className="text-gray-600 text-sm">No risk driver data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">Top Risk Drivers</h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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
  const isPositive = data.direction === 'positive';
  const color = isPositive ? '#ef4444' : '#10b981'; // red for positive, green for negative
  const arrow = isPositive ? '↑' : '↓';

  // Format feature name for display
  const formatFeatureName = (name: string) => {
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
      fill: '#9ca3af',
    },
    {
      name: 'Current',
      value: data.feature_value,
      fill: color,
    },
  ];

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      {/* Rank badge */}
      <div className="flex items-center justify-between mb-3">
        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-800 text-xs font-semibold">
          {rank}
        </span>
        <span
          className="text-2xl font-bold"
          style={{ color }}
        >
          {arrow} {Math.abs(data.contribution_weight * 100).toFixed(1)}%
        </span>
      </div>

      {/* Feature name */}
      <h3 className="text-sm font-semibold text-gray-900 mb-2">
        {formatFeatureName(data.feature_name)}
      </h3>

      {/* Values comparison */}
      <div className="mb-4 space-y-1">
        <div className="flex justify-between text-xs">
          <span className="text-gray-600">Current Value:</span>
          <span className="font-medium">{data.feature_value.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-gray-600">Baseline:</span>
          <span className="font-medium">{data.baseline_value.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-gray-600">Impact:</span>
          <span className="font-medium" style={{ color }}>
            {isPositive ? 'Increases' : 'Decreases'} Risk
          </span>
        </div>
      </div>

      {/* Bar chart */}
      <ResponsiveContainer width="100%" height={120}>
        <BarChart data={chartData}>
          <XAxis dataKey="name" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '0.375rem',
              fontSize: '12px',
            }}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
