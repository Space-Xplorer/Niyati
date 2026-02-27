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
    if (!agent) return 'text-gray-700';
    const colors = [
      'text-blue-600',
      'text-purple-600',
      'text-green-600',
      'text-orange-600',
      'text-pink-600',
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
    <div className="bg-white rounded-2xl shadow-xl shadow-black/5 border border-[#005b52]/10 overflow-hidden">
      <div className="px-6 py-4 border-b border-[#005b52]/5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <h2 className="text-lg font-semibold text-[#04221f]">Agent Activity Log</h2>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-xs text-[#005b52]/70">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={clearLogs}
            className="px-3 py-1 text-sm text-[#005b52]/70 hover:text-[#04221f] transition-colors"
          >
            Clear
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-3 py-1 text-sm bg-[#005b52] text-[#dbf226] rounded hover:bg-[#04221f] transition-colors shadow-sm"
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </button>
        </div>
      </div>
      <div className={`overflow-y-auto bg-[#f7faf9] ${isExpanded ? 'h-96' : 'h-48'} transition-all duration-300`}>
        {logs.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-[#04221f]/70 text-sm">Waiting for agent activity...</p>
          </div>
        ) : (
          <div className="p-4 space-y-2 font-mono text-sm">
            {logs.map((log) => (
              <div
                key={log.id}
                className={`flex items-start space-x-3 ${log.isError ? 'bg-red-50 border-l-4 border-red-500 pl-2' : ''}`}
              >
                <span className="text-[#04221f]/50 text-xs whitespace-nowrap">
                  {formatTime(log.timestamp)}
                </span>
                <span className={`flex-1 ${log.isError ? 'text-red-700 font-semibold' : getAgentColor(log.agent)}`}>
                  {log.message}
                </span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        )}
      </div>
      <div className="px-6 py-3 bg-white border-t border-[#005b52]/5">
        <div className="flex items-center justify-between text-xs text-[#005b52]/70">
          <span>{logs.length} messages</span>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-blue-600"></div>
              <span>Agent 1</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-purple-600"></div>
              <span>Agent 2</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-green-600"></div>
              <span>Agent 3</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-orange-600"></div>
              <span>Agent 4</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-pink-600"></div>
              <span>Agent 5</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-red-600"></div>
              <span>Error</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
