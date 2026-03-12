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
    if (score >= 70) return '#34d399'; // emerald-400
    if (score >= 40) return '#fbbf24'; // amber-400
    return '#f87171'; // red-400
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
          <span className="text-5xl font-bold tracking-tight text-[#04221f]">
            {Math.round(clampedScore)}
          </span>
          <span className="text-xs font-medium uppercase tracking-widest text-[#005b52]/60 mt-1">out of 100</span>
        </div>
      </div>
      <p className="mt-4 text-sm font-medium text-[#005b52]/80 text-center max-w-[200px] leading-relaxed">
        {clampedScore >= 70 && 'Excellent health — Low fraud risk'}
        {clampedScore >= 40 && clampedScore < 70 && 'Moderate health — Medium fraud risk'}
        {clampedScore < 40 && 'Poor health — High fraud risk'}
      </p>
    </div>
  );
};
