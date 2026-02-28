'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useAuth } from '@/context/AuthContext';
import dynamic from 'next/dynamic';

// Dynamically import ForceGraph2D from the 2D-only package (react-force-graph-2d)
// react-force-graph-2d exports the component as its default export
const ForceGraph2D = dynamic(
  () => import('react-force-graph-2d'),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#005b52]"></div>
      </div>
    )
  }
) as any;

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

  // Track mouse position
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

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

  // Detect cycles in the graph
  const detectCycles = useCallback((nodes: GraphNode[], edges: GraphEdge[]) => {
    const cycleNodes = new Set<string>();
    const adjacencyList = new Map<string, string[]>();

    // Build adjacency list
    edges.forEach(edge => {
      if (!adjacencyList.has(edge.source)) {
        adjacencyList.set(edge.source, []);
      }
      adjacencyList.get(edge.source)!.push(edge.target);
    });

    // DFS to detect cycles
    const visited = new Set<string>();
    const recStack = new Set<string>();
    const currentPath: string[] = [];

    const dfs = (nodeId: string): boolean => {
      visited.add(nodeId);
      recStack.add(nodeId);
      currentPath.push(nodeId);

      const neighbors = adjacencyList.get(nodeId) || [];
      for (const neighbor of neighbors) {
        if (!visited.has(neighbor)) {
          if (dfs(neighbor)) {
            return true;
          }
        } else if (recStack.has(neighbor)) {
          // Found a cycle - mark all nodes in the cycle
          const cycleStartIndex = currentPath.indexOf(neighbor);
          for (let i = cycleStartIndex; i < currentPath.length; i++) {
            cycleNodes.add(currentPath[i]);
          }
          cycleNodes.add(neighbor);
          return true;
        }
      }

      recStack.delete(nodeId);
      currentPath.pop();
      return false;
    };

    // Check all nodes for cycles
    nodes.forEach(node => {
      if (!visited.has(node.id)) {
        dfs(node.id);
      }
    });

    return cycleNodes;
  }, []);

  // Detect cycles when data loads
  const [cycleNodes, setCycleNodes] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (data && data.nodes && data.edges) {
      const cycles = detectCycles(data.nodes, data.edges);
      setCycleNodes(cycles);
      console.log(`Detected ${cycles.size} nodes involved in cycles`);
    }
  }, [data, detectCycles]);

  // Detect cycle edges
  const [cycleEdges, setCycleEdges] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (data && data.edges && cycleNodes.size > 0) {
      const edges = new Set<string>();
      data.edges.forEach(edge => {
        if (cycleNodes.has(edge.source) && cycleNodes.has(edge.target)) {
          edges.add(`${edge.source}-${edge.target}`);
        }
      });
      setCycleEdges(edges);
    }
  }, [data, cycleNodes]);

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
  const handleNodeHover = useCallback((node: any) => {
    setHoveredNode(node);
  }, []);

  // Render node canvas with pulsing animation for circular trade nodes
  const paintNode = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.label || '';
    const size = node.label === 'Taxpayer' ? 8 : 5;
    const color = getNodeColor(node);
    const isInCycle = cycleNodes.has(node.id) || node.in_circular_trade;

    // Draw pulsing animation for circular trade nodes
    if (isInCycle) {
      const pulseSize = size + Math.sin(Date.now() / 200) * 3;
      ctx.beginPath();
      ctx.arc(node.x, node.y, pulseSize, 0, 2 * Math.PI);
      ctx.fillStyle = 'rgba(239, 68, 68, 0.3)'; // Red with transparency
      ctx.fill();

      // Draw outer ring for cycle nodes
      ctx.beginPath();
      ctx.arc(node.x, node.y, size + 4, 0, 2 * Math.PI);
      ctx.strokeStyle = '#EF4444';
      ctx.lineWidth = 2 / globalScale;
      ctx.stroke();
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
  }, [getNodeColor, cycleNodes]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f7faf9] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#005b52] mx-auto"></div>
          <p className="mt-4 text-[#005b52]/70">Loading graph...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#f7faf9] flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500">Error: {error}</p>
        </div>
      </div>
    );
  }

  if (!data || data.nodes.length === 0) {
    return (
      <div className="min-h-screen bg-[#f7faf9] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[#005b52]/70">No graph data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f7faf9]">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-[#04221f]">Transaction Graph</h1>
            <p className="text-[#005b52]/70 mt-2">
              {user?.role === 'admin' ? 'Global View' : `GSTIN: ${user?.email}`}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => window.location.href = '/'}
              className="text-sm bg-white border border-[#005b52]/20 hover:bg-[#005b52]/5 text-[#04221f] px-4 py-2 rounded-lg font-medium transition"
            >
              Home
            </button>
            <button
              onClick={() => window.location.href = '/dashboard'}
              className="text-sm bg-[#dbf226] hover:bg-[#c4da1e] border border-[#04221f]/10 text-[#04221f] px-4 py-2 rounded-lg font-medium shadow-md shadow-black/5 transition"
            >
              Dashboard
            </button>
            <button
              onClick={logout}
              className="text-sm bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium shadow-md transition"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Legend and Stats */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-900">Legend</h2>
            <div className="flex items-center gap-4 text-sm">
              <span className="text-gray-600">
                Nodes: <span className="font-semibold text-gray-900">{data.nodes.length}</span>
              </span>
              <span className="text-gray-600">
                Edges: <span className="font-semibold text-gray-900">{data.edges.length}</span>
              </span>
              {cycleNodes.size > 0 && (
                <span className="text-red-600">
                  Cycle Nodes: <span className="font-semibold">{cycleNodes.size}</span>
                </span>
              )}
            </div>
          </div>
          <div className="flex flex-wrap gap-6">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-red-500"></div>
              <span className="text-sm text-[#005b52] font-medium">High Risk</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
              <span className="text-sm text-[#005b52] font-medium">Medium Risk</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-green-500"></div>
              <span className="text-sm text-[#005b52] font-medium">Low Risk</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-gray-400"></div>
              <span className="text-sm text-[#005b52] font-medium">Invoice/EwayBill</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative">
                <div className="w-6 h-6 rounded-full bg-red-500 animate-pulse"></div>
                <div className="absolute inset-0 rounded-full border-2 border-red-500"></div>
              </div>
              <span className="text-sm text-gray-700">Circular Trade / Cycle</span>
            </div>
          </div>
        </div>

        {/* Graph Container */}
        <div className="bg-white rounded-2xl shadow-xl shadow-black/5 border border-[#005b52]/10 overflow-hidden" style={{ height: '700px' }}>
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
            linkColor={(link: any) => {
              const edgeKey = `${link.source.id || link.source}-${link.target.id || link.target}`;
              return cycleEdges.has(edgeKey) ? '#EF4444' : '#D1D5DB';
            }}
            linkWidth={(link: any) => {
              const edgeKey = `${link.source.id || link.source}-${link.target.id || link.target}`;
              return cycleEdges.has(edgeKey) ? 2.5 : 1.5;
            }}
            linkDirectionalArrowLength={3.5}
            linkDirectionalArrowRelPos={1}
            linkDirectionalParticles={2}
            linkDirectionalParticleWidth={2}
            backgroundColor="#ffffff"
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
            className="fixed bg-[#04221f] text-[#f7faf9] border border-[#dbf226]/20 px-4 py-3 rounded-lg shadow-2xl z-50 pointer-events-none"
            style={{
              left: `${mousePosition.x + 15}px`,
              top: `${mousePosition.y + 15}px`,
              maxWidth: '300px',
            }}
          >
            <div className="space-y-1">
              {hoveredNode.label === 'Taxpayer' && (
                <>
                  <div className="font-semibold text-sm text-[#dbf226]">
                    {hoveredNode.name || hoveredNode.id}
                  </div>
                  <div className="text-xs text-white/70">
                    GSTIN: {hoveredNode.id}
                  </div>
                  {hoveredNode.risk_level && (
                    <div className="text-xs">
                      Risk: <span className={`font-medium ${hoveredNode.risk_level === 'HIGH_RISK' ? 'text-red-400' :
                        hoveredNode.risk_level === 'MEDIUM_RISK' ? 'text-yellow-400' :
                          'text-green-400'
                        }`}>
                        {hoveredNode.risk_level.replace('_', ' ')}
                      </span>
                    </div>
                  )}
                  {(hoveredNode.in_circular_trade || cycleNodes.has(hoveredNode.id)) && (
                    <div className="text-xs text-red-400 font-medium">
                      ⚠ Involved in Circular Trade / Cycle
                    </div>
                  )}
                </>
              )}
              {hoveredNode.label === 'Invoice' && (
                <>
                  <div className="font-semibold text-sm text-[#dbf226]">Invoice</div>
                  <div className="text-xs text-white/70">
                    ID: {hoveredNode.id}
                  </div>
                  {hoveredNode.value && (
                    <div className="text-xs">
                      Value: ₹{hoveredNode.value.toLocaleString()}
                    </div>
                  )}
                  {hoveredNode.date && (
                    <div className="text-xs text-white/70">
                      Date: {hoveredNode.date}
                    </div>
                  )}
                  {cycleNodes.has(hoveredNode.id) && (
                    <div className="text-xs text-red-400 font-medium">
                      ⚠ Part of Circular Trade
                    </div>
                  )}
                </>
              )}
              {hoveredNode.label === 'EwayBill' && (
                <>
                  <div className="font-semibold text-sm text-[#dbf226]">E-Way Bill</div>
                  <div className="text-xs text-white/70">
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
