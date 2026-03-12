'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/Button';

// â”€â”€â”€ Types â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

interface PipelineStep {
  agent: string;
  action: string;
  detail: string;
  elapsed_ms: number;
}

interface PriorityAlert {
  gstin: string;
  risk: number;
  reasons: string[];
}

interface VendorRisk {
  vendor_gstin: string;
  vendor_name: string;
  risk_level: string;
  risk_probability: number;
  fraud_flags: string[];
  itc_at_risk: number;
}

interface MockResult {
  status: string;
  message: string;
  execution_time_seconds: number;
  summary: {
    invoices_processed: number;
    entities_analyzed: number;
    circular_trade_patterns: number;
    ghost_invoices: number;
    spider_webs: number;
    high_risk_entities: number;
    medium_risk_entities: number;
    low_risk_entities: number;
    avg_filing_delay_days: number;
    avg_tax_gap_inr: number;
    max_tax_gap_inr: number;
  };
  pipeline_steps: PipelineStep[];
  priority_alerts: PriorityAlert[];
  vendor_risks: VendorRisk[];
  fraud_breakdown: {
    circular_trade_gstins: string[];
    ghost_invoice_gstins: string[];
    spider_web_gstins: string[];
  };
}

// â”€â”€â”€ Agent config â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

const AGENTS = [
  { id: 'IngestionWrangler', label: 'Ingestion Wrangler', icon: '📥', color: 'blue', description: 'Validating & ingesting all 6 CSV datasets' },
  { id: 'GraphArchitect', label: 'Graph Architect', icon: 'ðŸ•¸ï¸', color: 'purple', description: 'Building Neo4j knowledge graph & detecting cycles' },
  { id: 'RiskDetective', label: 'Risk Detective', icon: 'ðŸ”', color: 'orange', description: 'Computing risk scores & tax-gap analysis' },
  { id: 'PredictiveAnalyst', label: 'Predictive Analyst', icon: '📊', color: 'indigo', description: 'Running EBM model & generating SHAP explanations' },
  { id: 'NiyatiExplainer', label: 'Niyati Explainer', icon: 'ðŸ“', color: 'green', description: 'Generating audit narratives & priority alerts' },
];

const COLOR_MAP: Record<string, { bg: string; border: string; text: string }> = {
  blue: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-800' },
  purple: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-800' },
  orange: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-800' },
  indigo: { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-800' },
  green: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-800' },
};

const MOCK_DATASETS = [
  { label: 'E-Invoices', desc: '1,000 B2B invoices (2023)', icon: '🧾' },
  { label: 'E-Way Bills', desc: '1,000 transport records', icon: '🚛' },
  { label: 'Entity Master', desc: '500 registered taxpayers', icon: 'ðŸ¢' },
  { label: 'Filing History', desc: '12-month GSTR delay data', icon: '📅' },
  { label: 'Purchase Register', desc: '800 purchase transactions', icon: '🛒' },
  { label: 'Returns Summary', desc: 'GSTR-1 vs GSTR-3B liability', icon: '💰' },
];

interface UploadResponse {
  status: string;
  message: string;
  summary: {
    invoices_processed: number;
    circular_trade_patterns: number;
    ghost_invoices: number;
    spider_webs: number;
    high_risk_entities: number;
  };
  execution_time_seconds: number;
}

const FILE_TYPES = [
  { key: 'e_invoices', label: 'E-Invoices' },
  { key: 'eway_bills', label: 'E-Way Bills' },
  { key: 'entity_master', label: 'Entity Master' },
  { key: 'filing_history', label: 'Filing History' },
  { key: 'purchase_register', label: 'Purchase Register' },
  { key: 'returns_summary', label: 'Returns Summary' },
];

// â”€â”€â”€ Helper components â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function Spinner({ size = 5 }: { size?: number }) {
  return (
    <svg className={`animate-spin h-${size} w-${size} text-current`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
    </svg>
  );
}

function RiskBadge({ level }: { level: string }) {
  const map: Record<string, string> = {
    HIGH_RISK: 'bg-red-100 text-red-800 border border-red-200',
    MEDIUM_RISK: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
    LOW_RISK: 'bg-green-100 text-green-800 border border-green-200',
  };
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${map[level] ?? 'bg-gray-100 text-gray-600'}`}>
      {level?.replace('_', ' ')}
    </span>
  );
}

export default function UploadPage() {
  const { token } = useAuth();

  // â”€â”€ Mock mode state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  type Mode = 'idle' | 'running' | 'done' | 'error';
  const [mode, setMode] = useState<Mode>('idle');
  const [activeAgentIdx, setActiveAgentIdx] = useState(-1);
  const [agentLogs, setAgentLogs] = useState<Record<string, string[]>>({});
  const [result, setResult] = useState<MockResult | null>(null);
  const [mockError, setMockError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'summary' | 'alerts' | 'vendors' | 'fraud'>('summary');

  // â”€â”€ Real upload state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  const [files, setFiles] = useState<Record<string, File | null>>(
    Object.fromEntries(FILE_TYPES.map((t) => [t.key, null]))
  );
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<UploadResponse | null>(null);

  const logRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [agentLogs]);

  // â”€â”€ Mock run â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  const runMock = async () => {
    if (!token) return;
    setMode('running');
    setResult(null);
    setMockError(null);
    setAgentLogs({});
    setActiveAgentIdx(0);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
    const fetchPromise = fetch(`${apiUrl}/mock-sync`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    }).then((r) => r.json());

    // Animate agents while API runs in background
    for (let i = 0; i < AGENTS.length; i++) {
      await new Promise((res) => setTimeout(res, 1100));
      setActiveAgentIdx(i);
      setAgentLogs((prev) => ({
        ...prev,
        [AGENTS[i].id]: [`âš™ï¸  ${AGENTS[i].description}—¦`],
      }));
    }

    try {
      const data: MockResult = await fetchPromise;
      if (data.status !== 'success') throw new Error(data.message || 'Analysis failed');

      // Replace placeholder logs with real pipeline step output
      const logsByAgent: Record<string, string[]> = {};
      for (const step of data.pipeline_steps) {
        if (!logsByAgent[step.agent]) logsByAgent[step.agent] = [];
        logsByAgent[step.agent].push(`✅  [${step.action}] ${step.detail}`);
      }
      setAgentLogs(logsByAgent);
      setResult(data);
      setMode('done');
      setActiveAgentIdx(AGENTS.length);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'An error occurred';
      setMockError(msg);
      setMode('error');
    }
  };

  // â”€â”€ Real file upload â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  const handleFileChange = (key: string, file: File | null) => {
    if (file && !file.name.endsWith('.csv')) {
      setUploadError(`${key}: Only CSV files are allowed`); return;
    }
    setUploadError(null);
    setFiles((prev) => ({ ...prev, [key]: file }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploadError(null);
    setUploadSuccess(null);
    const missing = FILE_TYPES.filter((t) => !files[t.key]);
    if (missing.length) { setUploadError(`Missing: ${missing.map((f) => f.label).join(', ')}`); return; }
    setUploading(true);
    try {
      const formData = new FormData();
      FILE_TYPES.forEach((t) => { if (files[t.key]) formData.append(t.key, files[t.key]!); });
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
      const resp = await fetch(`${apiUrl}/sync`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (resp.status === 401) { window.location.href = '/login'; return; }
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ message: 'Upload failed' }));
        throw new Error(err.message);
      }
      const res: UploadResponse = await resp.json();
      setUploadSuccess(res);
      setFiles(Object.fromEntries(FILE_TYPES.map((t) => [t.key, null])));
    } catch (err: unknown) {
      setUploadError(err instanceof Error ? err.message : 'Upload error');
    } finally {
      setUploading(false);
    }
  };

  // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  return (
    <div className="min-h-screen bg-[#f7faf9]">
      <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">

        {/* â”€â”€ Page Header â”€â”€ */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-[#04221f]">Upload GST Data</h1>
            <p className="text-[#005b52]/70 mt-1">Upload 6 CSV files to analyze GST fraud patterns</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => (window.location.href = '/')}
              className="text-sm bg-white border border-[#005b52]/20 hover:bg-[#005b52]/5 text-[#04221f] px-4 py-2 rounded-lg font-medium transition">
              Home
            </button>
            <button onClick={() => (window.location.href = '/dashboard')}
              className="text-sm bg-[#005b52] hover:bg-[#04221f] text-[#dbf226] px-4 py-2 rounded-lg font-medium transition shadow-md shadow-[#005b52]/20">
              Dashboard
            </button>
          </div>
        </div>

        {/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
            MOCK GST FILING CARD
        â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */}
        <div className="bg-linear-to-br from-[#004a43] to-[#005b52] rounded-2xl shadow-2xl shadow-[#005b52]/30 p-8 text-white">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <span className="text-[#dbf226] text-xs font-bold uppercase tracking-widest bg-[#dbf226]/10 px-2 py-0.5 rounded-full">
                Pre-filled Demo
              </span>
              <h2 className="text-2xl font-bold text-white mt-3">Mock GST Filing Analysis</h2>
              <p className="text-white/60 text-sm mt-1">
                Instantly run the full 5-agent pipeline on bundled sample data — no files needed.
              </p>
            </div>
            <button onClick={runMock} disabled={mode === 'running'}
              className="shrink-0 flex items-center gap-2 bg-[#dbf226] hover:bg-[#c4da1e] disabled:opacity-60 disabled:cursor-not-allowed text-[#04221f] font-bold px-8 py-4 rounded-xl text-lg shadow-lg shadow-black/20 transition-all">
              {mode === 'running'
                ? <><Spinner size={5} /> Running...</>
                : <><span className="text-xl">⚡</span> Run Mock Analysis</>
              }
            </button>
          </div>

          {/* Dataset preview chips */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-6">
            {MOCK_DATASETS.map((ds) => (
              <div key={ds.label} className="bg-white/10 backdrop-blur rounded-xl p-3 flex items-start gap-3">
                <span className="text-2xl">{ds.icon}</span>
                <div>
                  <p className="text-sm font-semibold text-white">{ds.label}</p>
                  <p className="text-xs text-white/60">{ds.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
            PIPELINE VISUALIZER
        â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */}
        {mode !== 'idle' && (
          <div className="bg-white rounded-2xl shadow-xl shadow-black/5 border border-[#005b52]/10 p-6">
            <h3 className="text-lg font-bold text-[#04221f] mb-5 flex items-center gap-2">
              <span>🤖</span> Agent Pipeline
              {mode === 'done' && (
                <span className="ml-auto text-sm font-normal text-green-600 bg-green-50 border border-green-200 px-3 py-1 rounded-full">
                  ✅ Complete in {result?.execution_time_seconds}s
                </span>
              )}
              {mode === 'running' && (
                <span className="ml-auto text-sm font-normal text-blue-600 bg-blue-50 border border-blue-200 px-3 py-1 rounded-full flex items-center gap-1">
                  <Spinner size={3} /> Processing...
                </span>
              )}
              {mode === 'error' && (
                <span className="ml-auto text-sm font-normal text-red-600 bg-red-50 border border-red-200 px-3 py-1 rounded-full">
                  âš ï¸ {mockError}
                </span>
              )}
            </h3>

            <div className="space-y-3">
              {AGENTS.map((agent, idx) => {
                const colors = COLOR_MAP[agent.color];
                const isActive = idx === activeAgentIdx && mode === 'running';
                const isDone = idx < activeAgentIdx || mode === 'done';
                const isPending = idx > activeAgentIdx && mode === 'running';
                const logs = agentLogs[agent.id] || [];

                return (
                  <div key={agent.id}
                    className={`rounded-xl border p-4 transition-all duration-500 ${isDone ? `${colors.bg} ${colors.border}` :
                        isActive ? `${colors.bg} ${colors.border} ring-2 ring-offset-1` :
                          'bg-gray-50 border-gray-200 opacity-40'
                      }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{agent.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`font-semibold text-sm ${isDone || isActive ? colors.text : 'text-gray-500'}`}>
                            {agent.label}
                          </span>
                          {isActive && <span className={`flex items-center gap-1 text-xs ${colors.text}`}><Spinner size={3} /> running</span>}
                          {isDone && <span className="text-xs text-green-600 font-medium">✅ done</span>}
                          {isPending && <span className="text-xs text-gray-400">queued</span>}
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">{agent.description}</p>
                      </div>
                    </div>

                    {logs.length > 0 && (
                      <div ref={idx === AGENTS.length - 1 ? logRef : undefined}
                        className="mt-3 bg-black/5 rounded-lg p-3 space-y-1 max-h-32 overflow-y-auto">
                        {logs.map((line, i) => (
                          <p key={i} className={`text-xs font-mono ${colors.text}`}>{line}</p>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
            RESULTS
        â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */}
        {mode === 'done' && result && (
          <div className="space-y-6">

            {/* KPI row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Invoices Processed', value: result.summary.invoices_processed, color: 'text-[#005b52]', bg: 'bg-[#005b52]/5' },
                { label: 'Entities Analyzed', value: result.summary.entities_analyzed, color: 'text-indigo-700', bg: 'bg-indigo-50' },
                { label: 'High Risk Entities', value: result.summary.high_risk_entities, color: 'text-red-700', bg: 'bg-red-50' },
                { label: 'Avg Tax Gap', value: `₹${result.summary.avg_tax_gap_inr.toLocaleString('en-IN')}`, color: 'text-orange-700', bg: 'bg-orange-50' },
              ].map((kpi) => (
                <div key={kpi.label} className={`${kpi.bg} rounded-2xl p-5 border border-black/5`}>
                  <p className="text-xs text-gray-500 mb-1">{kpi.label}</p>
                  <p className={`text-3xl font-extrabold ${kpi.color}`}>{kpi.value}</p>
                </div>
              ))}
            </div>

            {/* Tabs */}
            <div className="bg-white rounded-2xl shadow-xl shadow-black/5 border border-[#005b52]/10 overflow-hidden">
              <div className="flex border-b border-[#005b52]/10">
                {(['summary', 'alerts', 'vendors', 'fraud'] as const).map((tab) => (
                  <button key={tab} onClick={() => setActiveTab(tab)}
                    className={`flex-1 py-3 text-sm font-semibold capitalize transition ${activeTab === tab
                        ? 'text-[#005b52] border-b-2 border-[#005b52] bg-[#005b52]/5'
                        : 'text-gray-400 hover:text-gray-700'
                      }`}
                  >
                    {tab === 'summary' && '📊 Summary'}
                    {tab === 'alerts' && `ðŸš¨ Alerts (${result.priority_alerts.length})`}
                    {tab === 'vendors' && `ðŸ¢ Risk Table (${result.vendor_risks.length})`}
                    {tab === 'fraud' && 'ðŸ•µï¸ Fraud Breakdown'}
                  </button>
                ))}
              </div>

              <div className="p-6">
                {activeTab === 'summary' && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {[
                      { label: 'Circular Trade', value: result.summary.circular_trade_patterns, icon: '🔄', color: 'text-orange-700' },
                      { label: 'Ghost Invoices', value: result.summary.ghost_invoices, icon: '👻', color: 'text-red-700' },
                      { label: 'Spider-Web Nets', value: result.summary.spider_webs, icon: 'ðŸ•¸ï¸', color: 'text-purple-700' },
                      { label: 'Medium Risk', value: result.summary.medium_risk_entities, icon: 'âš ï¸', color: 'text-yellow-700' },
                      { label: 'Avg Filing Delay', value: `${result.summary.avg_filing_delay_days} days`, icon: '📅', color: 'text-blue-700' },
                      { label: 'Max Tax Gap', value: `₹${result.summary.max_tax_gap_inr.toLocaleString('en-IN')}`, icon: '💸', color: 'text-red-700' },
                    ].map((item) => (
                      <div key={item.label} className="bg-[#f7faf9] rounded-xl p-4 border border-[#005b52]/10">
                        <div className="flex items-center gap-2 mb-1">
                          <span>{item.icon}</span>
                          <span className="text-xs text-gray-500">{item.label}</span>
                        </div>
                        <p className={`text-2xl font-bold ${item.color}`}>{item.value}</p>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'alerts' && (
                  <div className="space-y-3">
                    {result.priority_alerts.length === 0
                      ? <p className="text-gray-400 text-sm text-center py-8">No priority alerts generated</p>
                      : result.priority_alerts.map((alert, i) => (
                        <div key={i} className="flex items-start gap-4 bg-red-50 border border-red-200 rounded-xl p-4">
                          <div className="shrink-0 w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center text-lg font-bold text-red-700">{i + 1}</div>
                          <div className="flex-1 min-w-0">
                            <p className="font-mono text-sm font-semibold text-red-900">{alert.gstin}</p>
                            <p className="text-xs text-red-600 mt-0.5">Risk: <strong>{(alert.risk * 100).toFixed(1)}%</strong></p>
                            <div className="flex flex-wrap gap-1 mt-2">
                              {alert.reasons.map((r) => (
                                <span key={r} className="text-xs bg-red-100 text-red-800 border border-red-200 px-2 py-0.5 rounded-full">{r}</span>
                              ))}
                            </div>
                          </div>
                          <span className="text-xs font-bold bg-red-600 text-white px-3 py-1 rounded-full shrink-0">HIGH RISK</span>
                        </div>
                      ))
                    }
                  </div>
                )}

                {activeTab === 'vendors' && (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-[#005b52]/10 text-left text-xs text-gray-500 uppercase tracking-wider">
                          <th className="pb-3 pr-4">GSTIN</th>
                          <th className="pb-3 pr-4">Risk Level</th>
                          <th className="pb-3 pr-4">Score</th>
                          <th className="pb-3 pr-4">Fraud Flags</th>
                          <th className="pb-3 text-right">ITC at Risk</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#005b52]/5">
                        {result.vendor_risks.map((v) => (
                          <tr key={v.vendor_gstin} className="hover:bg-[#f7faf9]">
                            <td className="py-3 pr-4 font-mono text-xs text-[#04221f]">{v.vendor_gstin}</td>
                            <td className="py-3 pr-4"><RiskBadge level={v.risk_level} /></td>
                            <td className="py-3 pr-4">
                              <div className="flex items-center gap-2">
                                <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                                  <div className={`h-full rounded-full ${v.risk_level === 'HIGH_RISK' ? 'bg-red-500' : v.risk_level === 'MEDIUM_RISK' ? 'bg-yellow-500' : 'bg-green-500'}`}
                                    style={{ width: `${v.risk_probability * 100}%` }} />
                                </div>
                                <span className="text-xs text-gray-600">{(v.risk_probability * 100).toFixed(0)}%</span>
                              </div>
                            </td>
                            <td className="py-3 pr-4">
                              <div className="flex flex-wrap gap-1">
                                {v.fraud_flags.length === 0
                                  ? <span className="text-xs text-gray-400">—</span>
                                  : v.fraud_flags.map((f) => (
                                    <span key={f} className="text-xs bg-yellow-50 text-yellow-800 border border-yellow-200 px-1.5 py-0.5 rounded">{f}</span>
                                  ))
                                }
                              </div>
                            </td>
                            <td className="py-3 text-right text-xs font-semibold text-red-700">
                              {v.itc_at_risk > 0 ? `₹${v.itc_at_risk.toLocaleString('en-IN')}` : '—'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {activeTab === 'fraud' && (
                  <div className="grid md:grid-cols-3 gap-6">
                    {[
                      { label: 'Circular Trade', icon: '🔄', color: 'orange', gstins: result.fraud_breakdown.circular_trade_gstins },
                      { label: 'Ghost Invoices', icon: '👻', color: 'red', gstins: result.fraud_breakdown.ghost_invoice_gstins },
                      { label: 'Spider Web Nets', icon: 'ðŸ•¸ï¸', color: 'purple', gstins: result.fraud_breakdown.spider_web_gstins },
                    ].map(({ label, icon, color, gstins }) => {
                      const c = COLOR_MAP[color] || COLOR_MAP.blue;
                      return (
                        <div key={label} className={`${c.bg} ${c.border} border rounded-xl p-4`}>
                          <h4 className={`font-semibold text-sm ${c.text} mb-3 flex items-center gap-1`}>
                            <span>{icon}</span> {label}
                            <span className="ml-auto text-xs font-bold">{gstins.length}</span>
                          </h4>
                          <div className="space-y-1 max-h-48 overflow-y-auto">
                            {gstins.length === 0
                              ? <p className="text-xs text-gray-400">None detected</p>
                              : gstins.map((g) => (
                                <p key={g} className={`text-xs font-mono ${c.text} bg-white/60 rounded px-2 py-1`}>{g}</p>
                              ))
                            }
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* CTAs after mock */}
            <div className="flex justify-center gap-4">
              <button onClick={() => { setMode('idle'); setResult(null); }}
                className="text-sm border border-[#005b52]/20 text-[#005b52] hover:bg-[#005b52]/5 px-5 py-2 rounded-lg font-medium transition">
                Run again
              </button>
              <button onClick={() => (window.location.href = '/dashboard')}
                className="text-sm bg-[#005b52] hover:bg-[#04221f] text-[#dbf226] px-5 py-2 rounded-lg font-medium transition shadow-md shadow-[#005b52]/20">
                View Dashboard →
              </button>
            </div>
          </div>
        )}

        {/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
            REAL FILE UPLOAD
        â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */}
        <div className="bg-white rounded-2xl shadow-xl shadow-black/5 border border-[#005b52]/10 p-8">
          <h2 className="text-lg font-bold text-[#04221f] mb-1">Upload Your Own Files</h2>
          <p className="text-sm text-[#005b52]/60 mb-6">Upload all 6 CSV files to run a full analysis on your own GST data.</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            {FILE_TYPES.map((type) => (
              <div key={type.key}>
                <label htmlFor={type.key} className="block text-sm font-medium text-[#005b52] mb-2">
                  {type.label} <span className="text-red-500">*</span>
                </label>
                <div className="flex items-center gap-4">
                  <input id={type.key} type="file" accept=".csv" disabled={uploading}
                    onChange={(e) => handleFileChange(type.key, e.target.files?.[0] || null)}
                    className="block w-full text-sm text-[#04221f] border border-[#005b52]/20 rounded-lg cursor-pointer bg-[#f7faf9] focus:outline-none focus:ring-2 focus:ring-[#005b52] file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[#005b52]/5 file:text-[#005b52] hover:file:bg-[#005b52]/10"
                  />
                  {files[type.key] && (
                    <span className="text-sm text-green-600 flex items-center gap-1 shrink-0">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      {files[type.key]!.name}
                    </span>
                  )}
                </div>
              </div>
            ))}

            {uploadError && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{uploadError}</div>
            )}

            {uploadSuccess && (
              <div className="bg-green-50 border border-green-200 rounded-xl p-6">
                <h3 className="text-base font-semibold text-green-900 mb-1">✅ {uploadSuccess.message}</h3>
                <p className="text-xs text-green-600 mb-4">Completed in {uploadSuccess.execution_time_seconds?.toFixed(1)}s</p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {([
                    ['Invoices', uploadSuccess.summary?.invoices_processed],
                    ['Circular Trade', uploadSuccess.summary?.circular_trade_patterns],
                    ['Ghost Invoices', uploadSuccess.summary?.ghost_invoices],
                    ['Spider Webs', uploadSuccess.summary?.spider_webs],
                    ['High Risk', uploadSuccess.summary?.high_risk_entities],
                  ] as [string, number | undefined][]).map(([label, val]) => (
                    <div key={label} className="bg-white rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-500">{label}</p>
                      <p className="text-xl font-bold text-gray-900">{val ?? '—'}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {uploading && (
              <div className="bg-[#005b52]/5 border border-[#005b52]/20 rounded-lg p-4 flex items-center gap-3">
                <Spinner size={5} />
                <div>
                  <p className="text-sm font-medium text-[#04221f]">Processing your files...</p>
                  <p className="text-xs text-[#005b52]/60 mt-0.5">Validating data, building graphs, detecting fraud patterns.</p>
                </div>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-2">
              <button type="button" disabled={uploading}
                onClick={() => { setFiles(Object.fromEntries(FILE_TYPES.map((t) => [t.key, null]))); setUploadError(null); setUploadSuccess(null); }}
                className="px-5 py-2.5 rounded-lg font-medium text-[#005b52] bg-white border border-[#005b52]/20 hover:bg-[#005b52]/5 disabled:opacity-50 transition">
                Clear
              </button>
              <Button type="submit" isLoading={uploading}>
                {uploading ? 'Uploading—¦' : 'Upload & Analyze'}
              </Button>
            </div>
          </form>
        </div>

      </div>
    </div>
  );
}
