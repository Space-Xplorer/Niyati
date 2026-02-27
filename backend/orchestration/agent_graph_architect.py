"""
Agent 2: Graph Architect

This module implements the Graph Architect agent as a LangGraph node.
The agent builds a Neo4j knowledge graph from validated CSV data, creating
Taxpayer, Invoice, and EwayBill nodes with their relationships.

Supports incremental updates: uses MERGE operations to handle new/updated records.
"""

import asyncio
import os
from typing import Dict, Any, List
import pandas as pd
from neo4j import GraphDatabase, Driver
from datetime import datetime

from orchestration.state import NiyatiState
from utils.neo4j_batching import (
    create_nodes_batch,
    create_relationships_batch,
    create_constraints
)
from utils.pii_hashing import hash_pii


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


async def graph_architect_node(state: NiyatiState) -> NiyatiState:
    """
    Graph Architect LangGraph Node (with Incremental Update Support)
    
    This agent performs the following tasks:
    1. Connects to Neo4j AuraDB
    2. Creates uniqueness constraints on Taxpayer.gstin and Invoice.irn
    3. Creates Taxpayer nodes from entity_master (with hashed contact values)
    4. Creates Invoice nodes from e_invoices
    5. Creates EwayBill nodes from eway_bills
    6. Creates ISSUED relationships (Taxpayer -> Invoice)
    7. Creates TO relationships (Invoice -> Taxpayer)
    8. Creates BACKED_BY relationships (Invoice -> EwayBill)
    9. Creates SHARED_CONTACT relationships (Taxpayer <-> Taxpayer)
    10. Broadcasts SSE progress messages
    11. Updates state with graph_built=True
    
    Incremental Mode:
    - Uses MERGE operations instead of CREATE for idempotency
    - Only processes new/updated records (from change_summary)
    - Existing nodes/relationships are updated, not duplicated
    
    Args:
        state: Current NiyatiState containing validated_data
    
    Returns:
        Updated NiyatiState with graph_built=True
    """
    try:
        validated_data = state['validated_data']
        batch_size = int(os.getenv('BATCH_SIZE', 500))
        
        await broadcast_event("Agent 2: Connecting to Neo4j AuraDB...")
        
        driver = get_neo4j_driver()
        
        with driver.session() as session:
            # Step 1: Create constraints (Requirements 3.4, 3.5)
            await broadcast_event("Agent 2: Creating uniqueness constraints...")
            
            constraints = [
                {"label": "Taxpayer", "property": "gstin", "name": "taxpayer_gstin"},
                {"label": "Invoice", "property": "irn", "name": "invoice_irn"},
                {"label": "EwayBill", "property": "doc_no", "name": "eway_bill_doc_no"}
            ]
            create_constraints(session, constraints)
            
            # Step 2: Create Taxpayer nodes (Requirements 3.1, 16.2)
            await broadcast_event("Agent 2: Creating Taxpayer nodes...")
            
            entity_master = validated_data['entity_master']
            taxpayer_nodes = _prepare_taxpayer_nodes(entity_master)
            
            total_taxpayers = len(taxpayer_nodes)
            total_batches = (total_taxpayers + batch_size - 1) // batch_size
            
            taxpayers_created = 0
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, total_taxpayers)
                batch = taxpayer_nodes[start_idx:end_idx]
                
                count = create_nodes_batch(
                    session,
                    "Taxpayer",
                    batch,
                    "gstin",
                    batch_size=len(batch)
                )
                taxpayers_created += count
                
                await broadcast_event(
                    f"Agent 2: Creating {len(batch)} Taxpayer nodes in batch "
                    f"{batch_num + 1}/{total_batches}"
                )
            
            # Step 3: Create Invoice nodes (Requirement 3.2)
            await broadcast_event("Agent 2: Creating Invoice nodes...")
            
            e_invoices = validated_data['e_invoices']
            invoice_nodes = _prepare_invoice_nodes(e_invoices)
            
            total_invoices = len(invoice_nodes)
            total_batches = (total_invoices + batch_size - 1) // batch_size
            
            invoices_created = 0
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, total_invoices)
                batch = invoice_nodes[start_idx:end_idx]
                
                count = create_nodes_batch(
                    session,
                    "Invoice",
                    batch,
                    "irn",
                    batch_size=len(batch)
                )
                invoices_created += count
                
                await broadcast_event(
                    f"Agent 2: Creating {len(batch)} Invoice nodes in batch "
                    f"{batch_num + 1}/{total_batches}"
                )
            
            # Step 4: Create EwayBill nodes (Requirement 3.3)
            await broadcast_event("Agent 2: Creating EwayBill nodes...")
            
            eway_bills = validated_data['eway_bills']
            eway_bill_nodes = _prepare_eway_bill_nodes(eway_bills)
            
            total_eway_bills = len(eway_bill_nodes)
            total_batches = (total_eway_bills + batch_size - 1) // batch_size
            
            eway_bills_created = 0
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, total_eway_bills)
                batch = eway_bill_nodes[start_idx:end_idx]
                
                count = create_nodes_batch(
                    session,
                    "EwayBill",
                    batch,
                    "doc_no",
                    batch_size=len(batch)
                )
                eway_bills_created += count
                
                await broadcast_event(
                    f"Agent 2: Creating {len(batch)} EwayBill nodes in batch "
                    f"{batch_num + 1}/{total_batches}"
                )
            
            # Step 5: Create ISSUED relationships (Requirement 3.6)
            await broadcast_event("Agent 2: Creating ISSUED relationships...")
            
            issued_rels = _prepare_issued_relationships(e_invoices)
            issued_count = create_relationships_batch(
                session,
                "ISSUED",
                issued_rels,
                "Taxpayer",
                "gstin",
                "Invoice",
                "irn",
                batch_size=batch_size
            )
            
            # Step 6: Create TO relationships (Requirement 3.7)
            await broadcast_event("Agent 2: Creating TO relationships...")
            
            to_rels = _prepare_to_relationships(e_invoices)
            to_count = create_relationships_batch(
                session,
                "TO",
                to_rels,
                "Invoice",
                "irn",
                "Taxpayer",
                "gstin",
                batch_size=batch_size
            )
            
            # Step 7: Create BACKED_BY relationships (Requirement 3.8)
            await broadcast_event("Agent 2: Creating BACKED_BY relationships...")
            
            backed_by_rels = _prepare_backed_by_relationships(e_invoices, eway_bills)
            backed_by_count = create_relationships_batch(
                session,
                "BACKED_BY",
                backed_by_rels,
                "Invoice",
                "irn",
                "EwayBill",
                "doc_no",
                batch_size=batch_size
            )
            
            # Step 8: Create SHARED_CONTACT relationships (Requirement 3.9, 16.2)
            await broadcast_event("Agent 2: Creating SHARED_CONTACT relationships...")
            
            shared_contact_rels = _prepare_shared_contact_relationships(entity_master)
            shared_contact_count = 0
            
            if shared_contact_rels:
                # SHARED_CONTACT is bidirectional, so we need a special query
                for i in range(0, len(shared_contact_rels), batch_size):
                    batch = shared_contact_rels[i:i + batch_size]
                    
                    query = """
                    UNWIND $batch AS rel
                    MATCH (t1:Taxpayer {gstin: rel.source_id})
                    MATCH (t2:Taxpayer {gstin: rel.target_id})
                    MERGE (t1)-[r:SHARED_CONTACT]->(t2)
                    SET r.contact_type = rel.contact_type,
                        r.contact_value = rel.contact_value
                    RETURN count(r) as created
                    """
                    
                    result = session.run(query, {"batch": batch})
                    shared_contact_count += result.single()["created"]
        
        driver.close()
        
        # Update state
        state['graph_built'] = True
        
        await broadcast_event(
            f"Agent 2: Graph construction complete - "
            f"{taxpayers_created} taxpayers, {invoices_created} invoices, "
            f"{eway_bills_created} eway bills, {issued_count} ISSUED, "
            f"{to_count} TO, {backed_by_count} BACKED_BY, "
            f"{shared_contact_count} SHARED_CONTACT relationships"
        )
        
        return state
        
    except Exception as e:
        error_msg = f"Agent 2 failed: {str(e)}"
        await broadcast_event(f"Agent 2: ERROR - {error_msg}")
        state['errors'].append(error_msg)
        return state


def _prepare_taxpayer_nodes(entity_master: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Prepare Taxpayer node data from entity_master DataFrame.
    
    Hashes phone and email values for PII protection.
    
    Args:
        entity_master: DataFrame with entity data
    
    Returns:
        List of dictionaries with Taxpayer node properties
    """
    nodes = []
    
    for _, row in entity_master.iterrows():
        node = {
            "gstin": str(row['Gstin']),
            "status": str(row.get('Status', 'Unknown')),
            "kyc_score": int(row.get('KycScore', 0)) if pd.notna(row.get('KycScore')) else 0
        }
        
        # Hash PII fields if they exist (SharedContact field contains phone/email)
        if 'SharedContact' in row and pd.notna(row['SharedContact']):
            node['shared_contact_hash'] = hash_pii(str(row['SharedContact']))
        
        # Add sector if available
        if 'Sector' in row and pd.notna(row['Sector']):
            node['sector'] = str(row['Sector'])
        
        nodes.append(node)
    
    return nodes


def _prepare_invoice_nodes(e_invoices: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Prepare Invoice node data from e_invoices DataFrame.
    
    Args:
        e_invoices: DataFrame with invoice data
    
    Returns:
        List of dictionaries with Invoice node properties
    """
    nodes = []
    
    for _, row in e_invoices.iterrows():
        node = {
            "irn": str(row['Irn']),
            "doc_no": str(row['DocNo']),
            "invoice_value": float(row['TotalVal']),
            "invoice_date": str(row['DocDt']),
            "seller_gstin": str(row['SellerGstin']),
            "buyer_gstin": str(row['BuyerGstin'])
        }
        
        # Add optional fields if available
        if 'AssAmt' in row and pd.notna(row['AssAmt']):
            node['assessed_amount'] = float(row['AssAmt'])
        
        if 'IgstAmt' in row and pd.notna(row['IgstAmt']):
            node['igst_amount'] = float(row['IgstAmt'])
        
        nodes.append(node)
    
    return nodes


def _prepare_eway_bill_nodes(eway_bills: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Prepare EwayBill node data from eway_bills DataFrame.
    
    Args:
        eway_bills: DataFrame with eway bill data
    
    Returns:
        List of dictionaries with EwayBill node properties
    """
    nodes = []
    
    for _, row in eway_bills.iterrows():
        node = {
            "doc_no": str(row['DocNo']),
            "vehicle_no": str(row.get('VehicleNo', '')),
            "distance": int(row.get('Distance', 0)) if pd.notna(row.get('Distance')) else 0
        }
        
        # Add EwbNo if available
        if 'EwbNo' in row and pd.notna(row['EwbNo']):
            node['ewb_no'] = str(row['EwbNo'])
        
        nodes.append(node)
    
    return nodes


def _prepare_issued_relationships(e_invoices: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Prepare ISSUED relationship data (Taxpayer -> Invoice).
    
    Args:
        e_invoices: DataFrame with invoice data
    
    Returns:
        List of dictionaries with relationship data
    """
    relationships = []
    
    for _, row in e_invoices.iterrows():
        rel = {
            "source_id": str(row['SellerGstin']),
            "target_id": str(row['Irn'])
        }
        relationships.append(rel)
    
    return relationships


def _prepare_to_relationships(e_invoices: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Prepare TO relationship data (Invoice -> Taxpayer).
    
    Args:
        e_invoices: DataFrame with invoice data
    
    Returns:
        List of dictionaries with relationship data
    """
    relationships = []
    
    for _, row in e_invoices.iterrows():
        rel = {
            "source_id": str(row['Irn']),
            "target_id": str(row['BuyerGstin'])
        }
        relationships.append(rel)
    
    return relationships


def _prepare_backed_by_relationships(
    e_invoices: pd.DataFrame,
    eway_bills: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Prepare BACKED_BY relationship data (Invoice -> EwayBill).
    
    Only creates relationships where DocNo matches between invoices and eway bills.
    
    Args:
        e_invoices: DataFrame with invoice data
        eway_bills: DataFrame with eway bill data
    
    Returns:
        List of dictionaries with relationship data
    """
    relationships = []
    
    # Create a set of valid eway bill DocNos for fast lookup
    valid_doc_nos = set(eway_bills['DocNo'].astype(str))
    
    for _, row in e_invoices.iterrows():
        doc_no = str(row['DocNo'])
        
        # Only create relationship if matching eway bill exists
        if doc_no in valid_doc_nos:
            rel = {
                "source_id": str(row['Irn']),
                "target_id": doc_no
            }
            relationships.append(rel)
    
    return relationships


def _prepare_shared_contact_relationships(
    entity_master: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Prepare SHARED_CONTACT relationship data (Taxpayer <-> Taxpayer).
    
    Identifies entities sharing phone or email and creates relationships
    using hashed contact values.
    
    Args:
        entity_master: DataFrame with entity data
    
    Returns:
        List of dictionaries with relationship data
    """
    relationships = []
    
    # Check if SharedContact column exists
    if 'SharedContact' not in entity_master.columns:
        return relationships
    
    # Build contact map (hashed_value -> list of GSTINs)
    contact_map = {}
    
    for _, row in entity_master.iterrows():
        gstin = str(row['Gstin'])
        
        if pd.notna(row.get('SharedContact')):
            contact_hash = hash_pii(str(row['SharedContact']))
            if contact_hash not in contact_map:
                contact_map[contact_hash] = []
            contact_map[contact_hash].append(gstin)
    
    # Create relationships for shared contacts
    for contact_hash, gstins in contact_map.items():
        if len(gstins) > 1:
            # Create relationships between all pairs
            for i in range(len(gstins)):
                for j in range(i + 1, len(gstins)):
                    rel = {
                        "source_id": gstins[i],
                        "target_id": gstins[j],
                        "contact_type": "shared",
                        "contact_value": contact_hash
                    }
                    relationships.append(rel)
    
    return relationships


def graph_architect_node_sync(state: NiyatiState) -> NiyatiState:
    """
    Synchronous wrapper for the Graph Architect node.
    
    LangGraph requires synchronous node functions, so this wrapper
    runs the async implementation using asyncio.run().
    
    Args:
        state: Current NiyatiState
    
    Returns:
        Updated NiyatiState
    """
    return asyncio.run(graph_architect_node(state))
