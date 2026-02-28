'use client';

import React, { useState } from 'react';

export interface LiveFilingResult {
  status: string;
  message: string;
  irn?: string;
  new_invoice_id?: string;
  timestamp: string;
  seller_gstin: string;
  buyer_gstin: string;
  amount: number;
  risk_score: number;
  risk_level: 'HIGH_RISK' | 'MEDIUM_RISK' | 'LOW_RISK';
  is_circular: boolean;
  cycle_path: string[];
  audit_trail: string;
  top_drivers: any[];
  neo4j_injected: boolean;
}

export default function MockGovPortalPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LiveFilingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    seller_gstin: '27AAAAA7009A1Z0', // default to demo admin
    buyer_gstin: '',
    amount: '',
    tax_amount: '',
    hsn_code: '9801'
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value.toUpperCase() }));
  };

  const handleGenerateIRN = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.buyer_gstin || !formData.amount) {
      setError("Please fill required fields (Buyer GSTIN, Amount)");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
      const response = await fetch(`${apiUrl}/api/v1/live-file`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // No Authorization header needed anymore - endpoint is public for the mock portal
        },
        body: JSON.stringify({
          seller_gstin: formData.seller_gstin,
          buyer_gstin: formData.buyer_gstin,
          amount: parseFloat(formData.amount),
          tax_amount: parseFloat(formData.tax_amount) || parseFloat(formData.amount) * 0.18,
          hsn_code: formData.hsn_code
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const data: LiveFilingResult = await response.json();
      setResult(data);

      // Clear amounts for next filing but keep GSTINs
      setFormData(prev => ({
        ...prev,
        amount: '',
        tax_amount: ''
      }));

    } catch (err: any) {
      console.error("Live Filing Error:", err);
      setError(err.message || 'Failed to submit filing. Check if backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#04221f] to-[#005b52] p-4 flex items-center justify-center">
      <div className="w-full max-w-xl">
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden border border-white/20">

          {/* Header */}
          <div className="bg-[#f2f4f8] px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-800">GSTN e-Invoice Portal</h2>
                <p className="text-xs text-gray-500 font-mono mt-1">Simulated Filing Terminal v1.0</p>
              </div>
              <div className="bg-blue-100 text-blue-800 p-2 rounded-full shadow-inner">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
              </div>
            </div>
          </div>

          <div className="p-6">
            <form onSubmit={handleGenerateIRN} className="space-y-5">

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider">Seller GSTIN</label>
                  <input
                    name="seller_gstin"
                    value={formData.seller_gstin}
                    onChange={handleChange}
                    className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm font-mono text-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition uppercase"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider">Buyer GSTIN *</label>
                  <input
                    name="buyer_gstin"
                    value={formData.buyer_gstin}
                    onChange={handleChange}
                    placeholder="27BBBBB..."
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono text-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition uppercase bg-white relative z-10"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1 col-span-1">
                  <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider">Amount (₹) *</label>
                  <input
                    type="number"
                    name="amount"
                    value={formData.amount}
                    onChange={handleChange}
                    placeholder="50000"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition bg-white"
                  />
                </div>
                <div className="space-y-1 col-span-1">
                  <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider">Tax (₹)</label>
                  <input
                    type="number"
                    name="tax_amount"
                    value={formData.tax_amount}
                    onChange={handleChange}
                    placeholder="Auto (18%)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition bg-white"
                  />
                </div>
                <div className="space-y-1 col-span-1">
                  <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider">HSN Code</label>
                  <input
                    name="hsn_code"
                    value={formData.hsn_code}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono text-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition bg-white"
                  />
                </div>
              </div>

              {error && (
                <div className="p-3 bg-red-50 text-red-600 rounded-lg text-sm font-medium border border-red-200">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className={`w-full py-3 rounded-xl font-bold text-white shadow-lg transition-all flex justify-center items-center gap-2 ${loading
                    ? 'bg-blue-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 hover:-translate-y-0.5 hover:shadow-blue-500/30 active:translate-y-0'
                  }`}
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    Filing to Gov Network...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                    Generate IRN
                  </>
                )}
              </button>

            </form>

            {/* Results Banner Slide-down animation defined in globals.css */}
            {result && !loading && (
              <div className="mt-6 pt-5 border-t border-gray-100 animate-[slideDown_0.3s_ease-out_forwards]">
                <div className={`p-4 rounded-xl shadow-inner border ${result.risk_level === 'HIGH_RISK' ? 'bg-[#fff5f5] border-red-300' :
                    result.risk_level === 'MEDIUM_RISK' ? 'bg-[#fffff0] border-yellow-400' :
                      'bg-[#f0fff4] border-green-300'
                  }`}>
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-gray-500">IRN Generated</span>
                    <span className={`text-xs font-bold px-2 py-1 rounded-full uppercase ${result.risk_level === 'HIGH_RISK' ? 'bg-red-100 text-red-700' :
                        result.risk_level === 'MEDIUM_RISK' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-700'
                      }`}>
                      {result.risk_level.replace('_', ' ')} ({(result.risk_score * 100).toFixed(0)}%)
                    </span>
                  </div>

                  <div className="font-mono text-[10px] break-all text-gray-600 bg-white/50 p-2 rounded border border-gray-200 mb-3">
                    {result.irn || result.new_invoice_id}
                  </div>

                  <p className="text-sm font-medium text-gray-800 mb-1 leading-snug">
                    <span className="font-bold text-black border-b border-gray-300 pb-0.5">Audit Context:</span> {result.audit_trail}
                  </p>

                  {result.is_circular && result.cycle_path && (
                    <div className="mt-2 bg-red-100/50 p-2 rounded text-xs text-red-800 font-mono border border-red-200">
                      <span className="font-bold">DETECTED LOOP:</span> {result.cycle_path.join(" → ")}
                    </div>
                  )}

                  <div className="mt-3 flex items-center justify-between text-[11px] text-gray-500">
                    <span className="flex items-center gap-1">
                      {result.neo4j_injected ? (
                        <>
                          <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div> Connected to Graph
                        </>
                      ) : (
                        <>
                          <div className="w-1.5 h-1.5 rounded-full bg-gray-400"></div> Node Offline
                        </>
                      )}
                    </span>
                    <span>{new Date(result.timestamp).toLocaleTimeString()}</span>
                  </div>

                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}
