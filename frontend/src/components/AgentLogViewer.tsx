'use client';

import React, { useEffect, useState, useRef } from 'react';

interface LogMessage {
  id: string;
  message: string;
  timestamp: Date;
  agent?: number;
  isError?: boolean;
}

export const AgentLogViewer: React.FC = () => {
  const [logs, setLogs] = useState<LogMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Connect to SSE endpoint
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
    const eventSource = new EventSource(`${apiUrl}/logs/stream`);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      addLog('Connected to agent log stream', false);
    };

    eventSource.onmessage = (event) => {
      const message = event.data;
      const isError = message.includes('ERROR');
      addLog(message, isError);
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      addLog('Connection to log stream lost', true);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom when new logs arrive
    if (isExpanded) {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, isExpanded]);

  const addLog = (message: string, isError: boolean) => {
    const newLog: LogMessage = {
      id: `${Date.now()}-${Math.random()}`,
      message,
      timestamp: new Date(),
      agent: extractAgentNumber(message),
      isError,
    };
    setLogs(prev => [...prev, newLog]);
  };

  const extractAgentNumber = (message: string): number | undefined => {
    const match = message.match(/Agent (\d+):/);
    return match ? parseInt(match[1]) : undefined;
  };

  const getAgentColor = (agent?: number): string => {
    if (!agent) return 'text-[#005b52]/70';
    const colors = [
      'text-blue-600 font-bold',
      'text-purple-600 font-bold',
      'text-emerald-600 font-bold',
      'text-amber-600 font-bold',
      'text-pink-600 font-bold',
    ];
    return colors[(agent - 1) % colors.length];
  };

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div className="bg-[#f7faf9] rounded-3xl border border-[#005b52]/10 overflow-hidden shadow-xl mt-8">
      {/* Terminal Header */}
      <div className="px-6 py-4 border-b border-[#005b52]/10 flex items-center justify-between bg-white">
        <div className="flex items-center space-x-4">
          <div className="flex gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-amber-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
          </div>
          <h2 className="text-sm font-mono font-bold text-[#04221f] uppercase tracking-widest flex items-center gap-2">
            <span>&gt;_ Agent Orchestration Stream</span>
          </h2>
          <div className="flex items-center space-x-2 bg-[#f7faf9] px-2 py-1 rounded-full border border-[#005b52]/10">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className={`text-[10px] uppercase font-bold tracking-wider ${isConnected ? 'text-emerald-600' : 'text-red-600'}`}>
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={clearLogs}
            className="px-4 py-1.5 text-xs font-mono font-bold text-[#005b52]/70 hover:text-[#04221f] bg-[#f7faf9] hover:bg-gray-100 rounded-md transition-colors border border-transparent hover:border-[#005b52]/10"
          >
            CLEAR
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-4 py-1.5 text-xs font-mono font-bold bg-[#005b52]/5 text-[#005b52] border border-[#005b52]/10 rounded-md hover:bg-[#005b52]/10 transition-colors shadow-sm"
          >
            {isExpanded ? 'MINIMIZE' : 'EXPAND'}
          </button>
        </div>
      </div>

      {/* Terminal Body */}
      <div className={`overflow-y-auto ${isExpanded ? 'h-[500px]' : 'h-64'} transition-all duration-500 custom-scroll`}>
        {logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-3 opacity-50">
            <svg className="w-8 h-8 text-[#005b52]/30 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M8 9l3 3-3 3m5 0h3M4 15V9c0-1.1.9-2 2-2h12c1.1 0 2 .9 2 2v6c0 1.1-.9 2-2 2H6c-1.1 0-2-.9-2-2z"></path></svg>
            <p className="font-mono text-[#005b52]/60 text-sm tracking-widest uppercase">Awaiting Events...</p>
          </div>
        ) : (
          <div className="p-6 space-y-3 font-mono text-[13px] leading-relaxed">
            {logs.map((log) => (
              <div
                key={log.id}
                className={`flex items-start space-x-4 p-2 rounded hover:bg-white transition-colors ${log.isError ? 'bg-red-50 border-l-2 border-red-500' : ''}`}
              >
                <div className="text-[#005b52]/40 text-xs mt-0.5 shrink-0 select-none">
                  [{formatTime(log.timestamp)}]
                </div>
                <div className={`flex-1 break-words ${log.isError ? 'text-red-600 font-bold' : getAgentColor(log.agent)}`}>
                  {log.message}
                </div>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        )}
      </div>

      {/* Terminal Footer (Legend) */}
      <div className="px-6 py-3 bg-[#f7faf9] border-t border-[#005b52]/10 rounded-b-3xl">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-xs font-mono text-[#005b52]/60">
          <span className="bg-white px-3 py-1 rounded-full border border-[#005b52]/10">
            Buffer: {logs.length} lines
          </span>
          <div className="flex flex-wrap items-center gap-4 justify-center">
            <div className="flex items-center space-x-1.5">
              <div className="w-2 h-2 rounded-full bg-blue-500"></div>
              <span>Ag1 Ingest</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-2 h-2 rounded-full bg-purple-500"></div>
              <span>Ag2 Graph</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
              <span>Ag3 Risk</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-2 h-2 rounded-full bg-amber-500"></div>
              <span>Ag4 Predict</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-2 h-2 rounded-full bg-pink-500"></div>
              <span>Ag5 Explain</span>
            </div>
            <div className="flex items-center space-x-1.5 opacity-80">
              <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
              <span className="text-red-600 font-bold">Error</span>
            </div>
          </div>
        </div>
      </div>
      {/* Custom Scrollbar Styles appended directly since Next.js standard tailwind doesn't have scrollbar-thin without plugins */}
      <style dangerouslySetInnerHTML={{
        __html: `
  .custom-scroll::-webkit-scrollbar {
    width: 6px;
  }
  .custom-scroll::-webkit-scrollbar-track {
    background: transparent; 
  }
  .custom-scroll::-webkit-scrollbar-thumb {
    background: rgba(0, 91, 82, 0.1); 
    border-radius: 10px;
  }
  .custom-scroll::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 91, 82, 0.2); 
  }
`}} />
    </div>
  );
};
