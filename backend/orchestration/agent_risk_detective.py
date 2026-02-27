"""
Agent 3: Risk Detective

This module implements the Risk Detective agent as a LangGraph node.
The agent runs structural graph queries on Neo4j to detect fraud patterns:
- Circular trade (A -> B -> C -> A loops)
- Ghost invoices (high-value invoices without eway bills)
- Spider webs (entities connected via shared contacts)

Requirements: 4.1-4.7, 19.5
"""

import asyncio
import os
from typing import Dict, Any, List
from neo4j import GraphDatabase, Driver

from orchestration.state import NiyatiState


# Global event queue for SSE broadcasting (will be set by main app)
event_queue = None


def set_event_queue(queue):
    """Set the global event queue for SSE broadcasting."""
    global event_queue
    event_queue = queue


async def broadcast_event(message: str):
    """Broadcast an SSE event message."""
    if event_queue is not None:
        await event_queue.put(message)


def get_neo4j_driver() -> Driver:
    """
    Create and return a Neo4j driver instance.
    
    Returns:
        Neo4j Driver connected to AuraDB
    
    Raises:
        ValueError: If required environment variables are missing
    """
    neo4j_uri = os.getenv('NEO4J_URI')
    neo4j_user = os.getenv('NEO4J_USER')
    neo4j_password = os.getenv('NEO4J_PASSWORD')
    
    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        raise ValueError(
            "Missing Neo4j configuration. Required: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD"
        )
    
    return GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))


async def risk_detective_node(state: NiyatiState) -> NiyatiState:
    """
    Risk Detective LangGraph Node
    
    This agent performs the following tasks:
    1. Connects to Neo4j knowledge graph
    2. Detects circular trade patterns (A -> B -> C -> A loops)
    3. Detects ghost invoices (high-value invoices without BACKED_BY relationships)
    4. Detects spider web networks (entities connected via SHARED_CONTACT)
    5. Computes aggregations: loop_length, total_value, cluster_size, transaction_volume
    6. Broadcasts SSE progress messages
    7. Updates state with structural_patterns
    
    Args:
        state: Current NiyatiState with graph_built=True
    
    Returns:
        Updated NiyatiState with structural_patterns populated
    
    Requirements: 4.1-4.7, 19.5
    """
    try:
        if not state.get('graph_built', False):
            error_msg = "Agent 3 requires graph_built=True. Graph Architect must run first."
            await broadcast_event(f"Agent 3: ERROR - {error_msg}")
            state['errors'].append(error_msg)
            return state
        
        await broadcast_event("Agent 3: Connecting to Neo4j for structural analysis...")
        
        driver = get_neo4j_driver()
        structural_patterns = []
        
        with driver.session() as session:
            # Pattern 1: Circular Trade Detection (Requirements 4.1, 4.2)
            await broadcast_event("Agent 3: Analyzing 3-hop circular trading paths...")
            
            circular_trade_patterns = _detect_circular_trade(session)
            structural_patterns.extend(circular_trade_patterns)
            
            await broadcast_event(
                f"Agent 3: Found {len(circular_trade_patterns)} circular trade patterns"
            )
            
            # Pattern 2: Ghost Invoice Detection (Requirements 4.3, 4.4)
            await broadcast_event("Agent 3: Detecting ghost invoices (high-value without eway bills)...")
            
            ghost_invoice_patterns = _detect_ghost_invoices(session)
            structural_patterns.extend(ghost_invoice_patterns)
            
            await broadcast_event(
                f"Agent 3: Found {len(ghost_invoice_patterns)} entities with ghost invoices"
            )
            
            # Pattern 3: Spider Web Detection (Requirements 4.5, 4.6)
            await broadcast_event("Agent 3: Identifying spider web networks via shared contacts...")
            
            spider_web_patterns = _detect_spider_webs(session)
            structural_patterns.extend(spider_web_patterns)
            
            await broadcast_event(
                f"Agent 3: Found {len(spider_web_patterns)} spider web clusters"
            )
        
        driver.close()
        
        # Update state with detected patterns (Requirement 4.7)
        state['structural_patterns'] = structural_patterns
        
        await broadcast_event(
            f"Agent 3: Risk Detective completed - "
            f"{len(structural_patterns)} total patterns detected"
        )
        
        return state
        
    except Exception as e:
        error_msg = f"Agent 3 failed: {str(e)}"
        await broadcast_event(f"Agent 3: ERROR - {error_msg}")
        state['errors'].append(error_msg)
        return state


def _detect_circular_trade(session) -> List[Dict[str, Any]]:
    """
    Detect circular trade patterns (A -> B -> C -> A loops).
    
    Uses Cypher to find 3-hop paths where the start and end taxpayers are the same.
    Computes loop_length (number of hops) and total_value (sum of invoice values).
    
    Args:
        session: Neo4j session
    
    Returns:
        List of circular trade pattern dictionaries
    
    Requirements: 4.1, 4.2
    """
    query = """
    MATCH path = (a:Taxpayer)-[:ISSUED]->(i1:Invoice)-[:TO]->(b:Taxpayer)
                 -[:ISSUED]->(i2:Invoice)-[:TO]->(c:Taxpayer)
                 -[:ISSUED]->(i3:Invoice)-[:TO]->(a)
    WHERE a.gstin < b.gstin AND b.gstin < c.gstin
    RETURN 
        a.gstin as gstin_a,
        COALESCE(a.status, 'Unknown') as name_a,
        b.gstin as gstin_b,
        COALESCE(b.status, 'Unknown') as name_b,
        c.gstin as gstin_c,
        COALESCE(c.status, 'Unknown') as name_c,
        i1.invoice_value + i2.invoice_value + i3.invoice_value as total_value,
        3 as loop_length,
        [i1.irn, i2.irn, i3.irn] as invoice_irns
    """
    
    result = session.run(query)
    patterns = []
    
    for record in result:
        pattern = {
            "pattern_type": "circular_trade",
            "gstin_list": [
                record["gstin_a"],
                record["gstin_b"],
                record["gstin_c"]
            ],
            "entity_names": [
                record["name_a"],
                record["name_b"],
                record["name_c"]
            ],
            "loop_length": record["loop_length"],
            "total_value": float(record["total_value"]),
            "invoice_irns": record["invoice_irns"],
            "risk_score": _compute_circular_trade_risk_score(
                record["loop_length"],
                float(record["total_value"])
            )
        }
        patterns.append(pattern)
    
    return patterns


def _detect_ghost_invoices(session, threshold: float = 100000.0) -> List[Dict[str, Any]]:
    """
    Detect ghost invoices (high-value invoices without BACKED_BY relationships).
    
    Identifies invoices above the threshold value that lack eway bill backing.
    Aggregates by seller_gstin with counts and total values.
    
    Args:
        session: Neo4j session
        threshold: Minimum invoice value to consider (default: 100,000)
    
    Returns:
        List of ghost invoice pattern dictionaries
    
    Requirements: 4.3, 4.4
    """
    query = """
    MATCH (t:Taxpayer)-[:ISSUED]->(i:Invoice)
    WHERE i.invoice_value > $threshold 
      AND NOT (i)-[:BACKED_BY]->(:EwayBill)
    RETURN 
        t.gstin as seller_gstin,
        COALESCE(t.status, 'Unknown') as seller_name,
        count(i) as ghost_count,
        sum(i.invoice_value) as ghost_value,
        collect(i.irn) as ghost_irns
    ORDER BY ghost_value DESC
    """
    
    result = session.run(query, {"threshold": threshold})
    patterns = []
    
    for record in result:
        pattern = {
            "pattern_type": "ghost_invoice",
            "gstin_list": [record["seller_gstin"]],
            "seller_gstin": record["seller_gstin"],
            "seller_name": record["seller_name"],
            "ghost_count": record["ghost_count"],
            "ghost_value": float(record["ghost_value"]),
            "ghost_irns": record["ghost_irns"],
            "risk_score": _compute_ghost_invoice_risk_score(
                record["ghost_count"],
                float(record["ghost_value"])
            )
        }
        patterns.append(pattern)
    
    return patterns


def _detect_spider_webs(session, min_cluster_size: int = 3) -> List[Dict[str, Any]]:
    """
    Detect spider web networks (entities connected via SHARED_CONTACT).
    
    Identifies connected components in the SHARED_CONTACT relationship graph
    where 3 or more taxpayers are connected. Computes cluster_size and
    total transaction_volume.
    
    Args:
        session: Neo4j session
        min_cluster_size: Minimum number of entities to consider a spider web
    
    Returns:
        List of spider web pattern dictionaries
    
    Requirements: 4.5, 4.6
    """
    query = """
    MATCH (t1:Taxpayer)-[sc:SHARED_CONTACT]-(t2:Taxpayer)
    WITH t1, collect(DISTINCT t2) as connected
    WHERE size(connected) >= $min_cluster_size - 1
    RETURN 
        t1.gstin as anchor_gstin,
        COALESCE(t1.status, 'Unknown') as anchor_name,
        [t IN connected | t.gstin] as cluster_gstins,
        [t IN connected | COALESCE(t.status, 'Unknown')] as cluster_names,
        size(connected) + 1 as cluster_size
    ORDER BY cluster_size DESC
    LIMIT 100
    """
    
    result = session.run(query, {"min_cluster_size": min_cluster_size})
    patterns = []
    seen_clusters = set()
    
    for record in result:
        # Create a unique identifier for this cluster (sorted GSTINs)
        cluster_gstins = [record["anchor_gstin"]] + record["cluster_gstins"]
        cluster_id = tuple(sorted(cluster_gstins))
        
        # Skip if we've already seen this cluster
        if cluster_id in seen_clusters:
            continue
        
        seen_clusters.add(cluster_id)
        
        # Calculate transaction volume for this cluster
        transaction_volume = _calculate_cluster_transaction_volume(session, cluster_gstins)
        
        pattern = {
            "pattern_type": "spider_web",
            "gstin_list": cluster_gstins,
            "entity_names": [record["anchor_name"]] + record["cluster_names"],
            "cluster_size": record["cluster_size"],
            "transaction_volume": transaction_volume,
            "risk_score": _compute_spider_web_risk_score(
                record["cluster_size"],
                transaction_volume
            )
        }
        patterns.append(pattern)
    
    return patterns


def _calculate_cluster_transaction_volume(session, gstins: List[str]) -> float:
    """
    Calculate total transaction volume for a cluster of GSTINs.
    
    Args:
        session: Neo4j session
        gstins: List of GSTINs in the cluster
    
    Returns:
        Total transaction volume
    """
    query = """
    MATCH (t:Taxpayer)-[:ISSUED]->(i:Invoice)
    WHERE t.gstin IN $gstins
    RETURN COALESCE(sum(i.invoice_value), 0) as total_volume
    """
    
    result = session.run(query, {"gstins": gstins})
    record = result.single()
    
    return float(record["total_volume"]) if record else 0.0


def _compute_circular_trade_risk_score(loop_length: int, total_value: float) -> float:
    """
    Compute risk score for circular trade patterns.
    
    Higher scores for longer loops and higher transaction values.
    
    Args:
        loop_length: Number of hops in the circular path
        total_value: Total transaction value in the loop
    
    Returns:
        Risk score between 0 and 1
    """
    # Normalize loop length (3-hop is baseline, longer is riskier)
    loop_factor = min(loop_length / 3.0, 1.0)
    
    # Normalize value (100k is baseline, higher is riskier)
    value_factor = min(total_value / 100000.0, 1.0)
    
    # Weighted combination
    risk_score = (loop_factor * 0.4) + (value_factor * 0.6)
    
    return min(risk_score, 1.0)


def _compute_ghost_invoice_risk_score(ghost_count: int, ghost_value: float) -> float:
    """
    Compute risk score for ghost invoice patterns.
    
    Higher scores for more ghost invoices and higher total values.
    
    Args:
        ghost_count: Number of ghost invoices
        ghost_value: Total value of ghost invoices
    
    Returns:
        Risk score between 0 and 1
    """
    # Normalize count (10 invoices is baseline)
    count_factor = min(ghost_count / 10.0, 1.0)
    
    # Normalize value (1M is baseline)
    value_factor = min(ghost_value / 1000000.0, 1.0)
    
    # Weighted combination
    risk_score = (count_factor * 0.3) + (value_factor * 0.7)
    
    return min(risk_score, 1.0)


def _compute_spider_web_risk_score(cluster_size: int, transaction_volume: float) -> float:
    """
    Compute risk score for spider web patterns.
    
    Higher scores for larger clusters and higher transaction volumes.
    
    Args:
        cluster_size: Number of entities in the cluster
        transaction_volume: Total transaction volume in the cluster
    
    Returns:
        Risk score between 0 and 1
    """
    # Normalize cluster size (5 entities is baseline)
    size_factor = min(cluster_size / 5.0, 1.0)
    
    # Normalize volume (5M is baseline)
    volume_factor = min(transaction_volume / 5000000.0, 1.0)
    
    # Weighted combination
    risk_score = (size_factor * 0.5) + (volume_factor * 0.5)
    
    return min(risk_score, 1.0)


def risk_detective_node_sync(state: NiyatiState) -> NiyatiState:
    """
    Synchronous wrapper for the Risk Detective node.
    
    LangGraph requires synchronous node functions, so this wrapper
    runs the async implementation using asyncio.run().
    
    Args:
        state: Current NiyatiState
    
    Returns:
        Updated NiyatiState
    """
    return asyncio.run(risk_detective_node(state))
