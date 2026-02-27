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
        return 'bg-red-100 text-red-800';
      case 'MEDIUM_RISK':
        return 'bg-yellow-100 text-yellow-800';
      case 'LOW_RISK':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
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
      <div className="bg-white rounded-2xl shadow-xl shadow-black/5 border border-[#005b52]/10 p-6">
        <h2 className="text-lg font-semibold text-[#04221f] mb-4">Vendor Risk Analysis</h2>
        <p className="text-[#005b52]/70 text-sm">No vendor risk data available</p>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white rounded-2xl shadow-xl shadow-black/5 border border-[#005b52]/10 overflow-hidden">
        <div className="px-6 py-4 border-b border-[#005b52]/5">
          <h2 className="text-lg font-semibold text-[#04221f]">Vendor Risk Analysis</h2>
          <p className="text-sm text-[#005b52]/70 mt-1">Click on a row to view detailed risk narrative</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-[#f7faf9]">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-[#005b52]/80 uppercase tracking-wider">
                  Vendor GSTIN
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-[#005b52]/80 uppercase tracking-wider">
                  Vendor Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-[#005b52]/80 uppercase tracking-wider">
                  Risk Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-[#005b52]/80 uppercase tracking-wider">
                  ITC at Risk
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-[#005b52]/80 uppercase tracking-wider">
                  Last Transaction
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-[#005b52]/5">
              {vendors.map((vendor, index) => (
                <tr
                  key={index}
                  onClick={() => handleRowClick(vendor)}
                  className="hover:bg-[#005b52]/5 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#04221f]">
                    {vendor.vendor_gstin}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-[#04221f]">
                    {vendor.vendor_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskBadgeColor(vendor.risk_level)}`}>
                      {formatRiskLevel(vendor.risk_level)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-[#04221f]">
                    {formatCurrency(vendor.itc_at_risk)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-[#04221f]/70">
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
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="px-6 py-4 border-b border-[#005b52]/10 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-[#04221f]">Risk Narrative</h3>
                <p className="text-sm text-[#005b52]/70 mt-1">
                  {selectedVendor.vendor_name} ({selectedVendor.vendor_gstin})
                </p>
              </div>
              <button
                onClick={closeModal}
                className="text-[#005b52]/50 hover:text-[#04221f] transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="px-6 py-4 overflow-y-auto max-h-[60vh]">
              {loadingNarrative ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#005b52]"></div>
                </div>
              ) : (
                <div className="prose prose-sm max-w-none">
                  <p className="text-[#04221f] whitespace-pre-wrap">{narrative}</p>
                </div>
              )}
            </div>
            <div className="px-6 py-4 border-t border-[#005b52]/10 flex justify-end">
              <button
                onClick={closeModal}
                className="px-4 py-2 bg-[#005b52] text-[#dbf226] rounded-lg hover:bg-[#04221f] transition-colors shadow-md"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
