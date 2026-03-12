'use client';

import React, { useState } from 'react';

interface Vendor {
  vendor_gstin: string;
  vendor_name: string;
  risk_level: string;
  itc_at_risk: number;
  last_transaction_date: string;
}

interface VendorRiskTableProps {
  vendors: Vendor[];
}

export const VendorRiskTable: React.FC<VendorRiskTableProps> = ({ vendors }) => {
  const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);
  const [narrative, setNarrative] = useState<string>('');
  const [loadingNarrative, setLoadingNarrative] = useState(false);

  const getRiskBadgeColor = (level: string) => {
    switch (level) {
      case 'HIGH_RISK':
        return 'bg-red-500/20 text-red-400 border border-red-500/30 shadow-[0_0_10px_rgba(239,68,68,0.2)]';
      case 'MEDIUM_RISK':
        return 'bg-amber-500/20 text-amber-400 border border-amber-500/30 shadow-[0_0_10px_rgba(245,158,11,0.2)]';
      case 'LOW_RISK':
        return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.2)]';
      default:
        return 'bg-gray-50 text-gray-700 border border-gray-200';
    }
  };

  const formatRiskLevel = (level: string) => {
    return level.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleRowClick = async (vendor: Vendor) => {
    setSelectedVendor(vendor);
    setLoadingNarrative(true);
    setNarrative('');

    try {
      const token = localStorage.getItem('token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
      const response = await fetch(`${apiUrl}/risk/${vendor.vendor_gstin}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setNarrative(data.narrative || 'No narrative available for this vendor.');
      } else {
        setNarrative('Failed to load narrative. Please try again.');
      }
    } catch (error) {
      setNarrative('Error loading narrative. Please try again.');
    } finally {
      setLoadingNarrative(false);
    }
  };

  const closeModal = () => {
    setSelectedVendor(null);
    setNarrative('');
  };

  if (!vendors || vendors.length === 0) {
    return (
      <div className="bg-[#f7faf9] border border-[#005b52]/10 rounded-3xl shadow-xl p-8">
        <h2 className="text-xl font-bold text-[#04221f] tracking-wide mb-4">Vendor Risk Analysis</h2>
        <p className="text-[#005b52]/60 text-sm">No vendor risk data available</p>
      </div>
    );
  }

  return (
    <>
      <div className="bg-[#f7faf9] border border-[#005b52]/10 rounded-3xl shadow-xl overflow-hidden">
        <div className="px-8 py-6 border-b border-[#005b52]/10 flex items-center gap-3 bg-white">
          <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center text-xl shadow-sm border border-[#005b52]/5">📋</div>
          <div>
            <h2 className="text-xl font-bold text-[#04221f] tracking-wide">Vendor Risk Analysis</h2>
            <p className="text-sm font-medium text-[#005b52]/60 mt-1">Click on a row to view detailed AI risk narrative</p>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-[#005b52]/10">
            <thead className="bg-[#f7faf9]">
              <tr>
                <th className="px-8 py-4 text-left text-xs font-bold text-[#005b52]/60 uppercase tracking-widest whitespace-nowrap">
                  Vendor GSTIN
                </th>
                <th className="px-8 py-4 text-left text-xs font-bold text-[#005b52]/60 uppercase tracking-widest whitespace-nowrap">
                  Vendor Name
                </th>
                <th className="px-8 py-4 text-left text-xs font-bold text-[#005b52]/60 uppercase tracking-widest whitespace-nowrap">
                  Risk Level
                </th>
                <th className="px-8 py-4 text-left text-xs font-bold text-[#005b52]/60 uppercase tracking-widest whitespace-nowrap">
                  ITC at Risk
                </th>
                <th className="px-8 py-4 text-left text-xs font-bold text-[#005b52]/60 uppercase tracking-widest whitespace-nowrap">
                  Last Transaction
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-[#005b52]/5">
              {vendors.map((vendor, index) => (
                <tr
                  key={index}
                  onClick={() => handleRowClick(vendor)}
                  className="hover:bg-[#f7faf9] cursor-pointer transition-colors group"
                >
                  <td className="px-8 py-5 whitespace-nowrap text-sm font-mono font-medium text-[#04221f]">
                    {vendor.vendor_gstin}
                  </td>
                  <td className="px-8 py-5 whitespace-nowrap text-sm font-medium text-[#04221f]">
                    {vendor.vendor_name}
                  </td>
                  <td className="px-8 py-5 whitespace-nowrap">
                    <span className={`inline-flex px-3 py-1 text-xs font-bold uppercase tracking-wider rounded-full ${getRiskBadgeColor(vendor.risk_level)}`}>
                      {formatRiskLevel(vendor.risk_level)}
                    </span>
                  </td>
                  <td className="px-8 py-5 whitespace-nowrap text-sm font-mono font-medium text-[#04221f]">
                    {formatCurrency(vendor.itc_at_risk)}
                  </td>
                  <td className="px-8 py-5 whitespace-nowrap text-sm font-medium text-[#005b52]/60">
                    {formatDate(vendor.last_transaction_date)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {selectedVendor && (
        <div className="fixed inset-0 bg-[#04221f]/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white border border-[#005b52]/20 rounded-3xl shadow-2xl max-w-3xl w-full max-h-[85vh] flex flex-col overflow-hidden relative">
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#005b52]/5 rounded-full blur-[100px] opacity-10 pointer-events-none"></div>

            <div className="px-8 py-6 border-b border-[#005b52]/10 flex items-center justify-between bg-[#f7faf9] relative z-10">
              <div>
                <h3 className="text-2xl font-bold text-[#04221f] tracking-tight flex items-center gap-3">
                  <span className="w-8 h-8 rounded-full bg-white flex items-center justify-center text-sm shadow-sm">🤖</span>
                  Niyati Explainer AI
                </h3>
                <p className="text-sm font-medium text-[#005b52]/60 mt-2 flex items-center gap-2">
                  Analyzing: <span className="font-bold text-[#04221f]">{selectedVendor.vendor_name}</span>
                  <span className="font-mono bg-white px-2 py-0.5 rounded text-[#04221f] border border-[#005b52]/10">{selectedVendor.vendor_gstin}</span>
                </p>
              </div>
              <button
                onClick={closeModal}
                className="w-10 h-10 rounded-full bg-white hover:bg-gray-50 border border-[#005b52]/10 flex items-center justify-center text-gray-500 hover:text-gray-700 transition-colors shadow-sm"
                title="Close"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="px-8 py-6 overflow-y-auto flex-1 relative z-10">
              {loadingNarrative ? (
                <div className="flex flex-col items-center justify-center py-16 gap-4">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#005b52]"></div>
                  <p className="text-[#005b52]/80 font-mono text-sm animate-pulse tracking-widest">GENERATING NARRATIVE...</p>
                </div>
              ) : (
                <div className="prose prose-sm max-w-none text-[#04221f]">
                  <pre className="text-[#04221f] whitespace-pre-wrap font-mono leading-relaxed bg-[#f7faf9] p-6 rounded-2xl border border-[#005b52]/10 shadow-sm">
                    {narrative}
                  </pre>
                </div>
              )}
            </div>
            <div className="px-8 py-5 border-t border-[#005b52]/10 flex justify-end bg-[#f7faf9] relative z-10">
              <button
                onClick={closeModal}
                className="px-6 py-2.5 bg-[#005b52] text-white rounded-full font-bold hover:bg-[#04221f] transition-colors shadow-md"
              >
                Acknowledge
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
