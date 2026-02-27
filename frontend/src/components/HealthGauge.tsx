'use client';

import React from 'react';

interface HealthGaugeProps {
  score: number;
}

export const HealthGauge: React.FC<HealthGaugeProps> = ({ score }) => {
  // Clamp score between 0 and 100
  const clampedScore = Math.max(0, Math.min(100, score));
  
  // Calculate color based on score
  const getColor = (score: number) => {
    if (score >= 70) return '#10b981'; // green
    if (score >= 40) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  const color = getColor(clampedScore);
  const circumference = 2 * Math.PI * 70; // radius = 70
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-48 h-48">
        <svg className="transform -rotate-90 w-48 h-48">
          {/* Background circle */}
          <circle
            cx="96"
            cy="96"
            r="70"
            stroke="#e5e7eb"
            strokeWidth="12"
            fill="none"
          />
          {/* Progress circle */}
          <circle
            cx="96"
            cy="96"
            r="70"
            stroke={color}
            strokeWidth="12"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold" style={{ color }}>
            {Math.round(clampedScore)}
          </span>
          <span className="text-sm text-gray-600">out of 100</span>
        </div>
      </div>
      <p className="mt-4 text-sm text-gray-600 text-center">
        {clampedScore >= 70 && 'Excellent health - Low fraud risk'}
        {clampedScore >= 40 && clampedScore < 70 && 'Moderate health - Medium fraud risk'}
        {clampedScore < 40 && 'Poor health - High fraud risk'}
      </p>
    </div>
  );
};
