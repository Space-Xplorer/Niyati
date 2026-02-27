"use client";

import { useScroll, useTransform } from "framer-motion";
import React from "react";
import { GoogleGeminiEffect } from "./ui/google-gemini-effect";

export function AgentCollaboration() {
  const ref = React.useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start 50%", "end start"], // Start pulling the lines exactly when the section reaches the middle of the screen
  });

  const pathLengthFirst = useTransform(scrollYProgress, [0, 0.8], [0.2, 1.2]);
  const pathLengthSecond = useTransform(scrollYProgress, [0, 0.8], [0.15, 1.2]);
  const pathLengthThird = useTransform(scrollYProgress, [0, 0.8], [0.1, 1.2]);
  const pathLengthFourth = useTransform(scrollYProgress, [0, 0.8], [0.05, 1.2]);
  const pathLengthFifth = useTransform(scrollYProgress, [0, 0.8], [0, 1.2]);

  return (
    <div
      className="h-[400vh] bg-[#f7faf9] w-full relative pt-40 overflow-clip"
      ref={ref}
    >
      <GoogleGeminiEffect
        pathLengths={[
          pathLengthFirst,
          pathLengthSecond,
          pathLengthThird,
          pathLengthFourth,
          pathLengthFifth,
        ]}
        title="The 6-Agent Force"
        description="Ingestion Wrangler, Risk Detective, Predictive Analyst, Niyati Explainer, Graph Architect, and Shadow Mirror work in harmony to secure your GST compliance."
      >
        {/* Agent Cards */}
        <div className="relative z-10 w-full px-8 max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-12 -mt-10 md:-mt-20">
          <AgentCard
            name="Ingestion Wrangler"
            description="Validates and normalizes CSV data, ensuring clean inputs for downstream analysis."
            icon="📥"
          />
          <AgentCard
            name="Risk Detective"
            description="Identifies circular trading patterns and suspicious transaction networks."
            icon="🔍"
          />
          <AgentCard
            name="Predictive Analyst"
            description="Uses ML models to forecast compliance risks and anomaly scores."
            icon="📊"
          />
          <AgentCard
            name="Niyati Explainer"
            description="Generates human-readable explanations using SHAP values and LLMs."
            icon="💡"
          />
          <AgentCard
            name="Graph Architect"
            description="Builds knowledge graphs to visualize entity relationships and dependencies."
            icon="🕸️"
          />
          <AgentCard
            name="Shadow Mirror"
            description="Monitors system health and orchestrates agent workflows in real-time."
            icon="🔮"
          />
        </div>
      </GoogleGeminiEffect>
    </div>
  );
}

function AgentCard({ name, description, icon }: { name: string; description: string; icon: string }) {
  return (
    <div className="bg-white border border-[#005b52]/10 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-bold text-[#005b52] mb-2">{name}</h3>
      <p className="text-sm text-[#005b52]/70 leading-relaxed">{description}</p>
    </div>
  );
}
