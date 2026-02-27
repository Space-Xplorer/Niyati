'use client';

import React from 'react';

interface RiskBadgeProps {
  level: 'HIGH_RISK' | 'MEDIUM_RISK' | 'LOW_RISK';
  probability: number;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, probability }) => {
  const getBadgeStyles = (level: string) => {
    switch (level) {
      case 'HIGH_RISK':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'MEDIUM_RISK':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'LOW_RISK':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getLabel = (level: string) => {
    switch (level) {
      case 'HIGH_RISK':
        return 'High Risk';
      case 'MEDIUM_RISK':
        return 'Medium Risk';
      case 'LOW_RISK':
        return 'Low Risk';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="flex flex-col items-center">
      <div className={`inline-flex items-center px-6 py-3 rounded-full border-2 ${getBadgeStyles(level)}`}>
        <span className="text-2xl font-bold">{getLabel(level)}</span>
      </div>
      <p className="mt-4 text-sm text-gray-600">
        Risk Probability: <span className="font-semibold">{(probability * 100).toFixed(1)}%</span>
      </p>
    </div>
  );
};
