'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/Button';

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

export default function UploadPage() {
  const { token } = useAuth();
  const [files, setFiles] = useState<Record<string, File | null>>({
    e_invoices: null,
    eway_bills: null,
    entity_master: null,
    filing_history: null,
    purchase_register: null,
    returns_summary: null,
  });
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<UploadResponse | null>(null);

  const handleFileChange = (key: string, file: File | null) => {
    if (file && !file.name.endsWith('.csv')) {
      setError(`${key}: Only CSV files are allowed`);
      return;
    }
    setError(null);
    setFiles((prev) => ({ ...prev, [key]: file }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Validate all files are selected
    const missingFiles = FILE_TYPES.filter((type) => !files[type.key]);
    if (missingFiles.length > 0) {
      setError(`Missing files: ${missingFiles.map((f) => f.label).join(', ')}`);
      return;
    }

    // Validate all files are CSV
    const invalidFiles = FILE_TYPES.filter(
      (type) => files[type.key] && !files[type.key]!.name.endsWith('.csv')
    );
    if (invalidFiles.length > 0) {
      setError(`Invalid file types: ${invalidFiles.map((f) => f.label).join(', ')}. Only CSV files are allowed.`);
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      FILE_TYPES.forEach((type) => {
        if (files[type.key]) {
          formData.append(type.key, files[type.key]!);
        }
      });

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
      const response = await fetch(`${apiUrl}/sync`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.status === 401) {
        // Token expired, redirect to login
        window.location.href = '/login';
        return;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Upload failed' }));
        throw new Error(errorData.message || `Upload failed with status ${response.status}`);
      }

      const result: UploadResponse = await response.json();
      setSuccess(result);

      // Reset form
      setFiles({
        e_invoices: null,
        eway_bills: null,
        entity_master: null,
        filing_history: null,
        purchase_register: null,
        returns_summary: null,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f7faf9]">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-[#04221f]">Upload GST Data</h1>
            <p className="text-[#005b52]/70 mt-2">Upload 6 CSV files to analyze GST fraud patterns</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => (window.location.href = '/')}
              className="text-sm bg-white border border-[#005b52]/20 hover:bg-[#005b52]/5 text-[#04221f] px-4 py-2 rounded-lg font-medium transition"
            >
              Home
            </button>
            <button
              onClick={() => (window.location.href = '/dashboard')}
              className="text-sm bg-[#005b52] hover:bg-[#04221f] text-[#dbf226] px-4 py-2 rounded-lg font-medium transition shadow-md shadow-[#005b52]/20"
            >
              Dashboard
            </button>
          </div>
        </div>

        {/* Upload Form */}
        <div className="bg-white rounded-2xl shadow-xl shadow-black/5 border border-[#005b52]/10 p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {FILE_TYPES.map((type) => (
              <div key={type.key}>
                <label htmlFor={type.key} className="block text-sm font-medium text-[#005b52] mb-2">
                  {type.label} <span className="text-red-500">*</span>
                </label>
                <div className="flex items-center gap-4">
                  <input
                    id={type.key}
                    type="file"
                    accept=".csv"
                    onChange={(e) => handleFileChange(type.key, e.target.files?.[0] || null)}
                    className="block w-full text-sm text-[#04221f] border border-[#005b52]/20 rounded-lg cursor-pointer bg-[#f7faf9] focus:outline-none focus:ring-2 focus:ring-[#005b52] file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[#005b52]/5 file:text-[#005b52] hover:file:bg-[#005b52]/10"
                    disabled={uploading}
                  />
                  {files[type.key] && (
                    <span className="text-sm text-green-600 flex items-center gap-1">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clipRule="evenodd"
                        />
                      </svg>
                      {files[type.key]!.name}
                    </span>
                  )}
                </div>
              </div>
            ))}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2">
                <svg className="w-5 h-5 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>{error}</span>
              </div>
            )}

            {/* Success Message */}
            {success && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                <div className="flex items-start gap-2 mb-4">
                  <svg className="w-6 h-6 text-green-600 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-green-900">{success.message}</h3>
                    <p className="text-sm text-green-700 mt-1">
                      Completed in {success.execution_time_seconds.toFixed(1)} seconds
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-600">Invoices Processed</p>
                    <p className="text-2xl font-bold text-gray-900">{success.summary.invoices_processed}</p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-600">Circular Trade Patterns</p>
                    <p className="text-2xl font-bold text-orange-600">{success.summary.circular_trade_patterns}</p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-600">Ghost Invoices</p>
                    <p className="text-2xl font-bold text-red-600">{success.summary.ghost_invoices}</p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <p className="text-sm text-gray-600">Spider Webs</p>
                    <p className="text-2xl font-bold text-purple-600">{success.summary.spider_webs}</p>
                  </div>
                  <div className="bg-white rounded-lg p-4 col-span-2">
                    <p className="text-sm text-gray-600">High Risk Entities</p>
                    <p className="text-2xl font-bold text-red-700">{success.summary.high_risk_entities}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-end gap-4">
              <button
                type="button"
                onClick={() => {
                  setFiles({
                    e_invoices: null,
                    eway_bills: null,
                    entity_master: null,
                    filing_history: null,
                    purchase_register: null,
                    returns_summary: null,
                  });
                  setError(null);
                  setSuccess(null);
                }}
                className="px-6 py-3 rounded-lg font-medium text-[#005b52] bg-white border border-[#005b52]/20 hover:bg-[#005b52]/5 focus:outline-none focus:ring-2 focus:ring-[#005b52]/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={uploading}
              >
                Clear
              </button>
              <Button type="submit" isLoading={uploading}>
                {uploading ? 'Uploading...' : 'Upload and Analyze'}
              </Button>
            </div>
          </form>
        </div>

        {/* Progress Indicator */}
        {uploading && (
          <div className="mt-6 bg-[#005b52]/5 border border-[#005b52]/20 rounded-lg p-6">
            <div className="flex items-center gap-3">
              <svg className="animate-spin h-6 w-6 text-[#005b52]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <div className="flex-1">
                <p className="text-sm font-medium text-[#04221f]">Processing your files...</p>
                <p className="text-xs text-[#005b52]/70 mt-1">
                  This may take up to 60 seconds. The system is validating data, building knowledge graphs, and detecting fraud patterns.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Info Box */}
        <div className="mt-6 bg-[#005b52]/5 border border-[#005b52]/20 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-[#04221f] mb-2">Required Files</h3>
          <ul className="text-sm text-[#005b52]/70 space-y-1">
            {FILE_TYPES.map((type) => (
              <li key={type.key} className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                {type.label} (CSV format)
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
