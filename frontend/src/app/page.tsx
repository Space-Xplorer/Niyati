'use client';

import { useState } from 'react';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { useAuth } from '@/context/AuthContext';

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [adminData, setAdminData] = useState<any>(null);
  const { token, logout, user } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
      const response = await fetch(`${apiUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ prompt }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Something went wrong');
      }

      setResult(data.data);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend.');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchAdminData = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
      const response = await fetch(`${apiUrl}/api/admin/data`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || data.message || 'Failed to fetch admin data');
      setAdminData(data);
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <main className="min-h-screen bg-black text-white p-8 font-[family-name:var(--font-geist-sans)]">
      <div className="max-w-3xl mx-auto space-y-8">

        {/* Header */}
        <div className="relative space-y-4 text-center pb-8 border-b border-gray-800">
          {user && (
            <div className="absolute top-0 right-0 flex flex-col items-end space-y-2">
              <div className="flex items-center space-x-4">
                <span className="text-gray-400 text-sm hidden sm:inline-block">
                  Logged in as {user.email}
                  <span className={`ml-2 px-2 py-0.5 rounded text-xs font-bold ${user.role === 'admin' ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'}`}>
                    {user.role?.toUpperCase() || 'USER'}
                  </span>
                </span>
                <button
                  onClick={logout}
                  className="text-xs bg-gray-800 hover:bg-gray-700 text-white px-3 py-1.5 rounded transition"
                >
                  Logout
                </button>
              </div>
              {user.role === 'admin' && (
                <button
                  onClick={fetchAdminData}
                  className="text-xs bg-red-600/20 hover:bg-red-600/40 text-red-400 border border-red-900/50 px-3 py-1.5 rounded transition"
                >
                  Test Admin Access
                </button>
              )}
            </div>
          )}

          <h1 className="text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            Niyati
          </h1>
          <p className="text-gray-400 text-lg">
            Rapid prototyping with Next.js, Tailwind, and a Flask AI backend.
          </p>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4">
          <Input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your prompt for the AI..."
            autoFocus
          />
          <Button type="submit" isLoading={isLoading}>
            Generate
          </Button>
        </form>

        {/* Status / Results */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 min-h-[300px]">
          {isLoading && (
            <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-4 pt-16">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <p>Analyzing and calling backend...</p>
            </div>
          )}

          {error && (
            <div className="text-red-400 bg-red-950/30 p-4 rounded-lg border border-red-900 mt-4">
              <span className="font-semibold">Error:</span> {error}
            </div>
          )}

          {!isLoading && !error && result && (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500 mt-4">
              <h3 className="text-gray-400 uppercase tracking-widest text-xs font-semibold">Response</h3>
              <div className="text-gray-100 whitespace-pre-wrap leading-relaxed">
                {result}
              </div>
            </div>
          )}

          {!isLoading && !error && !result && (
            <div className="flex items-center justify-center h-full text-gray-600 pt-16">
              <p>Your AI results will appear here.</p>
            </div>
          )}
        </div>

        {/* Admin Data Section */}
        {adminData && (
          <div className="bg-red-950/20 border border-red-900/50 rounded-xl p-6 mt-8">
            <h3 className="text-red-400 uppercase tracking-widest text-xs font-bold mb-4">Admin Dashboard Area</h3>
            <pre className="text-gray-300 text-sm overflow-x-auto bg-black/50 p-4 rounded-lg border border-red-900/30">
              {JSON.stringify(adminData, null, 2)}
            </pre>
          </div>
        )}

      </div>
    </main>
  );
}
