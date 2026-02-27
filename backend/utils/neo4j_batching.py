"""
Neo4j UNWIND Batching Utility Module

This module provides functions for efficient batch operations in Neo4j using the UNWIND pattern.
It includes retry logic with exponential backoff for resilience.
"""

import time
from typing import List, Dict, Any, Callable
from neo4j import Driver, Session
from neo4j.exceptions import Neo4jError


def create_nodes_batch(
    session: Session,
    node_label: str,
    nodes_data: List[Dict[str, Any]],
    unique_key: str,
    batch_size: int = 500,
    max_retries: int = 3
) -> int:
    """
    Create nodes in Neo4j using UNWIND batching pattern with retry logic.
    
    This function efficiently creates multiple nodes in batches using the UNWIND
    Cypher pattern, which is much faster than individual CREATE statements.
    Uses MERGE to ensure idempotency (no duplicate nodes).
    
    Args:
        session: Active Neo4j session
        node_label: The label for the nodes (e.g., "Taxpayer", "Invoice")
        nodes_data: List of dictionaries containing node properties
        unique_key: The property name to use for uniqueness (e.g., "gstin", "irn")
        batch_size: Number of nodes to create per batch (default: 500)
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        Total number of nodes created/merged
    
    Example:
        >>> nodes = [
        ...     {"gstin": "27AAPFU0939F1ZV", "business_name": "ABC Corp"},
        ...     {"gstin": "29AABCU9603R1ZX", "business_name": "XYZ Ltd"}
        ... ]
        >>> create_nodes_batch(session, "Taxpayer", nodes, "gstin")
        2
    """
    if not nodes_data:
        return 0
    
    total_created = 0
    
    # Process in batches
    for i in range(0, len(nodes_data), batch_size):
        batch = nodes_data[i:i + batch_size]
        
        # Build UNWIND query
        query = f"""
        UNWIND $batch AS node
        MERGE (n:{node_label} {{{unique_key}: node.{unique_key}}})
        SET n += node
        RETURN count(n) as created
        """
        
        # Execute with retry logic
        result = _execute_with_retry(
            session,
            query,
            {"batch": batch},
            max_retries
        )
        
        if result:
            total_created += result[0]["created"]
    
    return total_created


def create_relationships_batch(
    session: Session,
    relationship_type: str,
    relationships_data: List[Dict[str, Any]],
    source_label: str,
    source_key: str,
    target_label: str,
    target_key: str,
    batch_size: int = 500,
    max_retries: int = 3
) -> int:
    """
    Create relationships in Neo4j using UNWIND batching pattern with retry logic.
    
    This function efficiently creates multiple relationships in batches using the
    UNWIND Cypher pattern. Uses MERGE to ensure idempotency.
    
    Args:
        session: Active Neo4j session
        relationship_type: The type of relationship (e.g., "ISSUED", "TO", "BACKED_BY")
        relationships_data: List of dicts with source_id, target_id, and optional properties
        source_label: Label of source nodes (e.g., "Taxpayer")
        source_key: Property name for matching source nodes (e.g., "gstin")
        target_label: Label of target nodes (e.g., "Invoice")
        target_key: Property name for matching target nodes (e.g., "irn")
        batch_size: Number of relationships to create per batch (default: 500)
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        Total number of relationships created/merged
    
    Example:
        >>> rels = [
        ...     {"source_id": "27AAPFU0939F1ZV", "target_id": "INV001"},
        ...     {"source_id": "29AABCU9603R1ZX", "target_id": "INV002"}
        ... ]
        >>> create_relationships_batch(
        ...     session, "ISSUED", rels, "Taxpayer", "gstin", "Invoice", "irn"
        ... )
        2
    """
    if not relationships_data:
        return 0
    
    total_created = 0
    
    # Process in batches
    for i in range(0, len(relationships_data), batch_size):
        batch = relationships_data[i:i + batch_size]
        
        # Build UNWIND query
        # Extract properties (everything except source_id and target_id)
        has_properties = any(
            key not in ['source_id', 'target_id'] 
            for rel in batch 
            for key in rel.keys()
        )
        
        if has_properties:
            query = f"""
            UNWIND $batch AS rel
            MATCH (source:{source_label} {{{source_key}: rel.source_id}})
            MATCH (target:{target_label} {{{target_key}: rel.target_id}})
            MERGE (source)-[r:{relationship_type}]->(target)
            SET r += rel
            RETURN count(r) as created
            """
        else:
            query = f"""
            UNWIND $batch AS rel
            MATCH (source:{source_label} {{{source_key}: rel.source_id}})
            MATCH (target:{target_label} {{{target_key}: rel.target_id}})
            MERGE (source)-[r:{relationship_type}]->(target)
            RETURN count(r) as created
            """
        
        # Execute with retry logic
        result = _execute_with_retry(
            session,
            query,
            {"batch": batch},
            max_retries
        )
        
        if result:
            total_created += result[0]["created"]
    
    return total_created


def _execute_with_retry(
    session: Session,
    query: str,
    parameters: Dict[str, Any],
    max_retries: int = 3
) -> List[Dict[str, Any]]:
    """
    Execute a Cypher query with exponential backoff retry logic.
    
    Implements resilience pattern for database operations:
    - Retry on transient failures
    - Exponential backoff: 1s, 2s, 4s
    - Re-raise exception after max retries
    
    Args:
        session: Active Neo4j session
        query: Cypher query to execute
        parameters: Query parameters
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        Query result as list of dictionaries
    
    Raises:
        Neo4jError: If all retry attempts fail
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            result = session.run(query, parameters)
            return list(result)
        
        except Neo4jError as e:
            last_exception = e
            
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                print(f"Neo4j query failed (attempt {attempt + 1}/{max_retries}), "
                      f"retrying in {wait_time}s: {str(e)}")
                time.sleep(wait_time)
            else:
                # Final attempt failed
                print(f"Neo4j query failed after {max_retries} attempts: {str(e)}")
                raise
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    
    return []


def create_constraints(session: Session, constraints: List[Dict[str, str]]) -> None:
    """
    Create uniqueness constraints in Neo4j.
    
    Constraints ensure data integrity and improve query performance by creating indexes.
    
    Args:
        session: Active Neo4j session
        constraints: List of constraint definitions with keys:
            - label: Node label
            - property: Property name for uniqueness
            - name: Constraint name
    
    Example:
        >>> constraints = [
        ...     {"label": "Taxpayer", "property": "gstin", "name": "taxpayer_gstin"},
        ...     {"label": "Invoice", "property": "irn", "name": "invoice_irn"}
        ... ]
        >>> create_constraints(session, constraints)
    """
    for constraint in constraints:
        label = constraint['label']
        prop = constraint['property']
        name = constraint['name']
        
        try:
            query = f"""
            CREATE CONSTRAINT {name} IF NOT EXISTS
            FOR (n:{label})
            REQUIRE n.{prop} IS UNIQUE
            """
            session.run(query)
            print(f"Created constraint: {name}")
        
        except Neo4jError as e:
            # Log warning but continue (constraint might already exist)
            print(f"Warning: Could not create constraint {name}: {str(e)}")
