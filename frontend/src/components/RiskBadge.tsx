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
        return 'bg-red-50 text-red-700 border-red-200 shadow-sm';
      case 'MEDIUM_RISK':
        return 'bg-amber-50 text-amber-700 border-amber-200 shadow-sm';
      case 'LOW_RISK':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200 shadow-sm';
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
      <div className={`inline-flex items-center px-8 py-4 rounded-2xl border backdrop-blur-sm transition-all ${getBadgeStyles(level)}`}>
        <span className="text-3xl font-bold tracking-tight">{getLabel(level)}</span>
      </div>
      <p className="mt-5 text-sm font-medium text-[#005b52]/70">
        Risk Probability Prediction: <span className="font-mono text-[#04221f] font-bold text-base ml-1">{(probability * 100).toFixed(1)}%</span>
      </p>
    </div>
  );
};
