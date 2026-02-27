"use client";
import { motion, MotionValue } from "framer-motion";
import React from "react";

export const GoogleGeminiEffect = ({
  pathLengths,
  title,
  description,
  className,
  children,
}: {
  pathLengths: MotionValue[];
  title?: string;
  description?: string;
  className?: string;
  children?: React.ReactNode;
}) => {
  return (
    <div className={`flex flex-col items-center justify-start min-h-screen sticky top-0 pt-[15vh] ${className}`}>
      <p className="text-lg md:text-5xl lg:text-7xl font-bold text-[#005b52] text-center max-w-4xl mx-auto px-4">
        {title || "Multi-Agent Intelligence"}
      </p>
      <p className="text-xs md:text-lg lg:text-xl text-[#005b52]/70 text-center max-w-2xl mx-auto mt-4 md:mt-8 px-4">
        {description || "Six specialized agents collaborate in real-time to detect anomalies, predict risks, and explain compliance gaps across your GST network."}
      </p>
      <div className="w-full max-w-7xl h-[50vh] md:h-[65vh] flex items-center justify-center mt-6 md:mt-12">
        <svg
          width="1440"
          height="890"
          viewBox="0 0 1440 890"
          xmlns="http://www.w3.org/2000/svg"
          className="absolute w-full"
        >
          {/* 5 Continuous Lines: Left to Right with Smooth Bezier Curves */}
          {/* Top Line */}
          <motion.path
            d="M0 245 L 360 245 C 540 245, 540 445, 720 445 C 900 445, 900 245, 1080 245 L 1440 245"
            fill="none"
            stroke="url(#gradient1)"
            strokeWidth="2"
            strokeLinecap="round"
            style={{ pathLength: pathLengths[0] }}
          />

          {/* Upper Middle Line */}
          <motion.path
            d="M0 345 L 360 345 C 540 345, 540 445, 720 445 C 900 445, 900 345, 1080 345 L 1440 345"
            fill="none"
            stroke="url(#gradient2)"
            strokeWidth="2"
            strokeLinecap="round"
            style={{ pathLength: pathLengths[1] }}
          />

          {/* Center Line (Straight through) */}
          <motion.path
            d="M0 445 L 1440 445"
            fill="none"
            stroke="url(#gradient3)"
            strokeWidth="2"
            strokeLinecap="round"
            style={{ pathLength: pathLengths[2] }}
          />

          {/* Lower Middle Line */}
          <motion.path
            d="M0 545 L 360 545 C 540 545, 540 445, 720 445 C 900 445, 900 545, 1080 545 L 1440 545"
            fill="none"
            stroke="url(#gradient4)"
            strokeWidth="2"
            strokeLinecap="round"
            style={{ pathLength: pathLengths[3] }}
          />

          {/* Bottom Line */}
          <motion.path
            d="M0 645 L 360 645 C 540 645, 540 445, 720 445 C 900 445, 900 645, 1080 645 L 1440 645"
            fill="none"
            stroke="url(#gradient5)"
            strokeWidth="2"
            strokeLinecap="round"
            style={{ pathLength: pathLengths[4] }}
          />

          <defs>
            <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#005b52" stopOpacity="0" />
              <stop offset="50%" stopColor="#dbf226" stopOpacity="1" />
              <stop offset="100%" stopColor="#005b52" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#005b52" stopOpacity="0" />
              <stop offset="50%" stopColor="#dbf226" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#005b52" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#005b52" stopOpacity="0" />
              <stop offset="50%" stopColor="#dbf226" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#005b52" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="gradient4" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#005b52" stopOpacity="0" />
              <stop offset="50%" stopColor="#dbf226" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#005b52" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="gradient5" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#005b52" stopOpacity="0" />
              <stop offset="50%" stopColor="#dbf226" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#005b52" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      {children}
    </div>
  );
};
