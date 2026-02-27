'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useAuth } from '@/context/AuthContext';
import dynamic from 'next/dynamic';

// Dynamically import ForceGraph2D (2D-only package, no VR dependencies)
const ForceGraph2D = dynamic(
  () => import('react-force-graph-2d'),
  { 
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
);

interface GraphNode {
  id: string;
  label: string;
  name: string;
  risk_level?: 'HIGH_RISK' | 'MEDIUM_RISK' | 'LOW_RISK';
  value?: number;
  date?: string;
  in_circular_trade?: boolean;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export default function GraphPage() {
  const { token, user, logout } = useAuth();
  const [data, setData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const graphRef = useRef<any>(null);

  useEffect(() => {
    const fetchGraphData = async () => {
      if (!token) return;

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
        const response = await fetch(`${apiUrl}/graph`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.status === 401) {
          // Token expired or invalid, logout user
          logout();
          return;
        }

        if (!response.ok) {
          throw new Error('Failed to fetch graph data');
        }

        const result = await response.json();
        console.log(`Graph data loaded: ${result.count?.nodes || result.nodes?.length || 0} nodes, ${result.count?.edges || result.edges?.length || 0} edges from ${result.source || 'unknown'}`);
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchGraphData();
  }, [token, logout]);

  // Get node color based on risk level
  const getNodeColor = useCallback((node: GraphNode) => {
    if (node.label === 'Invoice' || node.label === 'EwayBill') {
      return '#9CA3AF'; // Gray for invoices and eway bills
    }
    
    if (node.label === 'Taxpayer') {
      switch (node.risk_level) {
        case 'HIGH_RISK':
          return '#EF4444'; // Red
        case 'MEDIUM_RISK':
          return '#F59E0B'; // Yellow/Orange
        case 'LOW_RISK':
          return '#10B981'; // Green
        default:
          return '#6B7280'; // Default gray
      }
    }
    
    return '#6B7280';
  }, []);

  // Handle node hover
  const handleNodeHover = useCallback((node: GraphNode | null, event?: MouseEvent) => {
    setHoveredNode(node);
    if (event) {
      setMousePosition({ x: event.clientX, y: event.clientY });
    }
  }, []);

  // Render node canvas with pulsing animation for circular trade nodes
  const paintNode = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.label || '';
    const size = node.label === 'Taxpayer' ? 8 : 5;
    const color = getNodeColor(node);

    // Draw pulsing animation for circular trade nodes
    if (node.in_circular_trade) {
      const pulseSize = size + Math.sin(Date.now() / 200) * 3;
      ctx.beginPath();
      ctx.arc(node.x, node.y, pulseSize, 0, 2 * Math.PI);
      ctx.fillStyle = 'rgba(239, 68, 68, 0.3)'; // Red with transparency
      ctx.fill();
    }

    // Draw main node
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();

    // Draw border for taxpayer nodes
    if (node.label === 'Taxpayer') {
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 1.5 / globalScale;
      ctx.stroke();
    }

    // Draw label for taxpayer nodes
    if (node.label === 'Taxpayer' && globalScale > 1.5) {
      const fontSize = 12 / globalScale;
      ctx.font = `${fontSize}px Sans-Serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#1F2937';
      ctx.fillText(label, node.x, node.y + size + fontSize);
    }
  }, [getNodeColor]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading graph...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Error: {error}</p>
        </div>
      </div>
    );
  }

  if (!data || data.nodes.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No graph data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Transaction Graph</h1>
            <p className="text-gray-600 mt-2">
              {user?.role === 'admin' ? 'Global View' : `GSTIN: ${user?.email}`}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => window.location.href = '/'}
              className="text-sm bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded transition"
            >
              Home
            </button>
            <button
              onClick={() => window.location.href = '/dashboard'}
              className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition"
            >
              Dashboard
            </button>
            <button
              onClick={logout}
              className="text-sm bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Legend */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">Legend</h2>
          <div className="flex flex-wrap gap-6">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-red-500"></div>
              <span className="text-sm text-gray-700">High Risk</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
              <span className="text-sm text-gray-700">Medium Risk</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-green-500"></div>
              <span className="text-sm text-gray-700">Low Risk</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-gray-400"></div>
              <span className="text-sm text-gray-700">Invoice/EwayBill</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-red-500 animate-pulse"></div>
              <span className="text-sm text-gray-700">Circular Trade</span>
            </div>
          </div>
        </div>

        {/* Graph Container */}
        <div className="bg-white rounded-lg shadow overflow-hidden" style={{ height: '700px' }}>
          <ForceGraph2D
            ref={graphRef}
            graphData={{
              nodes: data.nodes,
              links: data.edges.map(edge => ({
                source: edge.source,
                target: edge.target,
                type: edge.type,
              })),
            }}
            nodeCanvasObject={paintNode}
            nodePointerAreaPaint={(node: any, color: string, ctx: CanvasRenderingContext2D) => {
              const size = node.label === 'Taxpayer' ? 8 : 5;
              ctx.fillStyle = color;
              ctx.beginPath();
              ctx.arc(node.x, node.y, size + 2, 0, 2 * Math.PI);
              ctx.fill();
            }}
            onNodeHover={handleNodeHover}
            linkColor={() => '#D1D5DB'}
            linkWidth={1.5}
            linkDirectionalArrowLength={3.5}
            linkDirectionalArrowRelPos={1}
            linkDirectionalParticles={2}
            linkDirectionalParticleWidth={2}
            backgroundColor="#F9FAFB"
            cooldownTicks={100}
            onEngineStop={() => {
              if (graphRef.current) {
                graphRef.current.zoomToFit(400, 50);
              }
            }}
          />
        </div>

        {/* Tooltip */}
        {hoveredNode && (
          <div
            className="fixed bg-gray-900 text-white px-4 py-3 rounded-lg shadow-lg z-50 pointer-events-none"
            style={{
              left: `${mousePosition.x + 15}px`,
              top: `${mousePosition.y + 15}px`,
              maxWidth: '300px',
            }}
          >
            <div className="space-y-1">
              {hoveredNode.label === 'Taxpayer' && (
                <>
                  <div className="font-semibold text-sm">
                    {hoveredNode.name || hoveredNode.id}
                  </div>
                  <div className="text-xs text-gray-300">
                    GSTIN: {hoveredNode.id}
                  </div>
                  {hoveredNode.risk_level && (
                    <div className="text-xs">
                      Risk: <span className={`font-medium ${
                        hoveredNode.risk_level === 'HIGH_RISK' ? 'text-red-400' :
                        hoveredNode.risk_level === 'MEDIUM_RISK' ? 'text-yellow-400' :
                        'text-green-400'
                      }`}>
                        {hoveredNode.risk_level.replace('_', ' ')}
                      </span>
                    </div>
                  )}
                  {hoveredNode.in_circular_trade && (
                    <div className="text-xs text-red-400 font-medium">
                      ⚠ Involved in Circular Trade
                    </div>
                  )}
                </>
              )}
              {hoveredNode.label === 'Invoice' && (
                <>
                  <div className="font-semibold text-sm">Invoice</div>
                  <div className="text-xs text-gray-300">
                    ID: {hoveredNode.id}
                  </div>
                  {hoveredNode.value && (
                    <div className="text-xs">
                      Value: ₹{hoveredNode.value.toLocaleString()}
                    </div>
                  )}
                  {hoveredNode.date && (
                    <div className="text-xs text-gray-300">
                      Date: {hoveredNode.date}
                    </div>
                  )}
                </>
              )}
              {hoveredNode.label === 'EwayBill' && (
                <>
                  <div className="font-semibold text-sm">E-Way Bill</div>
                  <div className="text-xs text-gray-300">
                    ID: {hoveredNode.id}
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
