'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/Button';
import NiyatiLanding from '@/components/NiyatiHero';

export default function Home() {
  const router = useRouter();

  return (
    <>
      {/* Hero Section with Floating Navbar */}
      <NiyatiLanding />

      {/* Features Section */}
      <section id="features" className="px-6 py-24 bg-[#04221f] text-white">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 px-4 py-1.5 rounded-full border border-white/10 text-sm font-semibold tracking-wide bg-white/5 inline-flex items-center gap-3">
            <span className="bg-[#dbf226] text-[#04221f] px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider">
              Architecture
            </span>
            Powered by Five Intelligent Agents
          </div>
          <h3 className="text-4xl md:text-5xl font-serif font-bold mb-16 text-[#dbf226]">
            LangGraph Orchestration
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Agent 1 */}
            <div className="p-8 rounded-3xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
              <div className="w-12 h-12 rounded-xl mb-6 flex items-center justify-center bg-[#005b52] text-[#dbf226]">
                <span className="text-2xl font-bold">1</span>
              </div>
              <h4 className="text-xl font-bold mb-3 text-white">Ingestion Wrangler</h4>
              <p className="text-white/70 leading-relaxed">
                Validates and cleans GST transaction data from six CSV sources with automated feature engineering.
              </p>
            </div>

            {/* Agent 2 */}
            <div className="p-8 rounded-3xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
              <div className="w-12 h-12 rounded-xl mb-6 flex items-center justify-center bg-[#005b52] text-[#dbf226]">
                <span className="text-2xl font-bold">2</span>
              </div>
              <h4 className="text-xl font-bold mb-3 text-white">Graph Architect</h4>
              <p className="text-white/70 leading-relaxed">
                Builds a comprehensive Neo4j knowledge graph connecting taxpayers, invoices, and e-way bills.
              </p>
            </div>

            {/* Agent 3 */}
            <div className="p-8 rounded-3xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
              <div className="w-12 h-12 rounded-xl mb-6 flex items-center justify-center bg-[#005b52] text-[#dbf226]">
                <span className="text-2xl font-bold">3</span>
              </div>
              <h4 className="text-xl font-bold mb-3 text-white">Risk Detective</h4>
              <p className="text-white/70 leading-relaxed">
                Detects circular trading patterns, ghost invoices, and spider web networks through graph analysis.
              </p>
            </div>

            {/* Agent 4 */}
            <div className="p-8 rounded-3xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
              <div className="w-12 h-12 rounded-xl mb-6 flex items-center justify-center bg-[#005b52] text-[#dbf226]">
                <span className="text-2xl font-bold">4</span>
              </div>
              <h4 className="text-xl font-bold mb-3 text-white">Predictive Analyst</h4>
              <p className="text-white/70 leading-relaxed">
                Uses Explainable Boosting Machines to predict fraud risk with transparent feature contributions.
              </p>
            </div>

            {/* Agent 5 */}
            <div className="p-8 rounded-3xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
              <div className="w-12 h-12 rounded-xl mb-6 flex items-center justify-center bg-[#005b52] text-[#dbf226]">
                <span className="text-2xl font-bold">5</span>
              </div>
              <h4 className="text-xl font-bold mb-3 text-white">Niyati Explainer</h4>
              <p className="text-white/70 leading-relaxed">
                Generates plain-language audit narratives using LLMs for non-technical stakeholders.
              </p>
            </div>

            {/* Orchestration Concept */}
            <div className="p-8 rounded-3xl bg-[#dbf226] border border-[#dbf226]/50 shadow-[0_0_30px_rgba(219,242,38,0.15)]">
              <div className="w-12 h-12 rounded-xl mb-6 flex items-center justify-center bg-[#04221f] text-[#dbf226]">
                <span className="text-2xl font-bold">⚡</span>
              </div>
              <h4 className="text-xl font-bold mb-3 text-[#04221f]">Seamless Sync</h4>
              <p className="text-[#04221f]/80 leading-relaxed font-medium">
                Coordinates all agents in a seamless workflow with real-time observability and auto-recovery.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Detection Capabilities */}
      <section id="agents" className="px-6 py-24 bg-[#f7faf9]">
        <div className="max-w-7xl mx-auto">
          <h3 className="text-4xl md:text-5xl font-serif font-bold text-center mb-16 text-[#005b52]">
            What We Detect
          </h3>
          <div className="grid md:grid-cols-3 gap-10">
            <div className="text-center group">
              <div className="w-20 h-20 rounded-full mx-auto mb-6 flex items-center justify-center bg-white shadow-xl shadow-black/5 group-hover:scale-110 group-hover:bg-[#dbf226] transition-all duration-300">
                <span className="text-3xl">🔄</span>
              </div>
              <h4 className="text-2xl font-bold mb-4 text-[#04221f]">Circular Trading</h4>
              <p className="text-[#005b52]/70 leading-relaxed">
                Identifies complex transaction loops (A → B → C → A) designed to generate fraudulent Input Tax Credits (ITC).
              </p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 rounded-full mx-auto mb-6 flex items-center justify-center bg-white shadow-xl shadow-black/5 group-hover:scale-110 group-hover:bg-[#dbf226] transition-all duration-300">
                <span className="text-3xl">👻</span>
              </div>
              <h4 className="text-2xl font-bold mb-4 text-[#04221f]">Ghost Invoices</h4>
              <p className="text-[#005b52]/70 leading-relaxed">
                Isolates high-value GSTR-1 invoices completely lacking corresponding E-Way Bills or actual goods movement.
              </p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 rounded-full mx-auto mb-6 flex items-center justify-center bg-white shadow-xl shadow-black/5 group-hover:scale-110 group-hover:bg-[#dbf226] transition-all duration-300">
                <span className="text-3xl">🕸️</span>
              </div>
              <h4 className="text-2xl font-bold mb-4 text-[#04221f]">Spider Web Networks</h4>
              <p className="text-[#005b52]/70 leading-relaxed">
                Discovers hidden clusters of shell companies sharing identical contact parameters across different GSTINs.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section id="security" className="px-6 py-24 bg-white">
        <div className="max-w-7xl mx-auto rounded-[3rem] p-12 md:p-20 bg-[#04221f] text-white relative overflow-hidden shadow-2xl">
          {/* Decorative glow */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-[#005b52] rounded-full blur-[120px] opacity-50 -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

          <div className="relative z-10">
            <h3 className="text-4xl md:text-5xl font-serif font-bold mb-16 text-[#dbf226]">
              Why Choose Niyati?
            </h3>
            <div className="grid md:grid-cols-2 gap-12">
              <div className="flex gap-6 group">
                <div className="shrink-0 mt-1">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center bg-[#dbf226]/10 text-[#dbf226] group-hover:bg-[#dbf226] group-hover:text-[#04221f] transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                  </div>
                </div>
                <div>
                  <h4 className="text-xl font-bold mb-3">Explainable AI</h4>
                  <p className="text-white/60 leading-relaxed">
                    Understand exactly why an entity is flagged. Niyati breaks down risk scores with transparent feature contributions (SHAP).
                  </p>
                </div>
              </div>

              <div className="flex gap-6 group">
                <div className="shrink-0 mt-1">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center bg-[#dbf226]/10 text-[#dbf226] group-hover:bg-[#dbf226] group-hover:text-[#04221f] transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                  </div>
                </div>
                <div>
                  <h4 className="text-xl font-bold mb-3">Role-Based Access</h4>
                  <p className="text-white/60 leading-relaxed">
                    Admins have full visibility into the intelligence graph, while business owners securely view only their localized supply chain risk.
                  </p>
                </div>
              </div>

              <div className="flex gap-6 group">
                <div className="shrink-0 mt-1">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center bg-[#dbf226]/10 text-[#dbf226] group-hover:bg-[#dbf226] group-hover:text-[#04221f] transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                  </div>
                </div>
                <div>
                  <h4 className="text-xl font-bold mb-3">Real-Time Monitoring</h4>
                  <p className="text-white/60 leading-relaxed">
                    Watch the execution of LangGraph workflows live via Server-Sent Events spanning data ingestion to final narrative generation.
                  </p>
                </div>
              </div>

              <div className="flex gap-6 group">
                <div className="shrink-0 mt-1">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center bg-[#dbf226]/10 text-[#dbf226] group-hover:bg-[#dbf226] group-hover:text-[#04221f] transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                  </div>
                </div>
                <div>
                  <h4 className="text-xl font-bold mb-3">Military-Grade PII Protection</h4>
                  <p className="text-white/60 leading-relaxed">
                    All sensitive compliance configurations and entity identifiers are hashed before storage using SHA-256 encryption methodologies.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>



      {/* Footer */}
      <footer className="bg-white py-12">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between">
          <div className="flex items-center gap-2 mb-4 md:mb-0">
            <span className="font-serif text-2xl font-bold text-[#04221f]">Niyati</span>
          </div>
          <p className="text-[#005b52]/50 font-medium text-sm">
            © 2026 Project Niyati. Forensic Intelligence & Fraud Detection Platform. All Rights Reserved.
          </p>
        </div>
      </footer>
    </>
  );
}
