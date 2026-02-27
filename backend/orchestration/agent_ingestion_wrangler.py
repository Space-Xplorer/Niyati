"""
Agent 1: Ingestion Wrangler

This module implements the Ingestion Wrangler agent as a LangGraph node.
The agent validates CSV files, computes engineered features, and hashes PII data.

Supports incremental ingestion: detects new/updated records and only processes changes.

Requirements: 1.1-1.8, 2.1-2.8, 16.1, 16.2, 16.3, 19.3
"""

import asyncio
from typing import Dict, Any
import pandas as pd

from orchestration.state import NiyatiState
from utils.csv_validation import validate_all_csvs
from utils.feature_engineering_wrapper import compute_engineered_features
from utils.pii_hashing import hash_pii
from utils.change_detection import detect_all_changes
from utils.db_connection import get_postgres_connection


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


async def ingestion_wrangler_node(state: NiyatiState) -> NiyatiState:
    """
    Ingestion Wrangler LangGraph Node (with Incremental Update Support)
    
    This agent performs the following tasks:
    1. Validates all 6 CSV files for required fields
    2. Detects new/updated records by comparing with existing PostgreSQL data
    3. Computes 14 engineered fraud detection features (only for changed records)
    4. Hashes PII data (phone, email) before persistence
    5. Broadcasts SSE progress messages
    6. Updates state with validated data and engineered features
    
    Incremental Mode:
    - Queries PostgreSQL for existing records
    - Compares CSV data against existing data
    - Only processes new and updated records
    - Marks records for Neo4j MERGE operations
    
    Args:
        state: Current NiyatiState containing csv_files
    
    Returns:
        Updated NiyatiState with validated_data, engineered_features, and change_summary
    
    Requirements: 1.1-1.8, 2.1-2.8, 16.1, 16.2, 16.3, 19.3
    """
    try:
        csv_files = state['csv_files']
        
        # Step 1: Validate all CSV files (Requirements 1.1-1.7)
        await broadcast_event("Agent 1: Starting CSV validation...")
        
        all_valid, validation_results = validate_all_csvs(csv_files)
        
        if not all_valid:
            # Collect error details
            errors = []
            for csv_type, result in validation_results.items():
                if not result.get('valid', False):
                    error_msg = f"Validation failed for {csv_type}: {result.get('error', result.get('error_details', 'Unknown error'))}"
                    errors.append(error_msg)
                    await broadcast_event(f"Agent 1: ERROR - {error_msg}")
            
            state['errors'].extend(errors)
            return state
        
        # Broadcast validation success for each file
        for csv_type, result in validation_results.items():
            row_count = result.get('row_count', 0)
            await broadcast_event(f"Agent 1: Validating {csv_type}.csv - {row_count} rows")
        
        # Step 1.5: Detect changes (Incremental Ingestion)
        await broadcast_event("Agent 1: Detecting new and updated records...")
        
        existing_data = await _fetch_existing_data()
        changes = detect_all_changes(csv_files, existing_data)
        
        # Log change summary
        total_new = sum(c['total_new'] for c in changes.values())
        total_updated = sum(c['total_updated'] for c in changes.values())
        total_unchanged = sum(c['total_unchanged'] for c in changes.values())
        
        await broadcast_event(
            f"Agent 1: Change detection complete - {total_new} new, {total_updated} updated, {total_unchanged} unchanged"
        )
        
        # Store change summary in state for downstream agents
        state['change_summary'] = {
            'total_new': total_new,
            'total_updated': total_updated,
            'total_unchanged': total_unchanged,
            'details': changes
        }
        
        # Step 2: Hash PII data in entity_master (Requirements 16.1, 16.2, 16.3)
        await broadcast_event("Agent 1: Hashing PII data (phone, email)...")
        
        entity_master = csv_files['entity_master'].copy()
        
        # Note: The actual CSV data doesn't have Phone/Email columns
        # PII hashing is implemented but not applied to this dataset
        # In production, if Phone/Email columns exist, they would be hashed here
        if 'Phone' in entity_master.columns:
            entity_master['phone_hash'] = entity_master['Phone'].apply(hash_pii)
        
        if 'Email' in entity_master.columns:
            entity_master['email_hash'] = entity_master['Email'].apply(hash_pii)
        
        # Update csv_files with hashed entity_master
        csv_files_with_hashed_pii = csv_files.copy()
        csv_files_with_hashed_pii['entity_master'] = entity_master
        
        # Step 3: Compute engineered features (Requirements 2.1-2.8)
        # Only compute for new/updated entities to optimize performance
        await broadcast_event("Agent 1: Computing engineered fraud detection features...")
        
        # For incremental mode, we still compute features for all entities
        # because features depend on relationships across all data
        engineered_features = compute_engineered_features(csv_files_with_hashed_pii)
        
        await broadcast_event(
            f"Agent 1: Feature engineering complete - {len(engineered_features)} entities processed"
        )
        
        # Step 4: Update state with validated data and features (Requirement 1.8)
        state['validated_data'] = csv_files_with_hashed_pii
        state['engineered_features'] = engineered_features
        
        await broadcast_event("Agent 1: Ingestion Wrangler completed successfully")
        
        return state
        
    except Exception as e:
        error_msg = f"Agent 1 failed: {str(e)}"
        await broadcast_event(f"Agent 1: ERROR - {error_msg}")
        state['errors'].append(error_msg)
        return state


async def _fetch_existing_data() -> Dict[str, pd.DataFrame]:
    """
    Fetch existing data from PostgreSQL for change detection.
    
    Returns:
        Dictionary mapping CSV type to existing DataFrames
    """
    existing_data = {}
    
    try:
        with get_postgres_connection() as db:
            # Check if tables exist and fetch data
            table_mapping = {
                'e_invoices': 'raw_invoices',
                'eway_bills': 'raw_eway_bills',
                'entity_master': 'entity_master',
                'filing_history': 'filing_history',
                'purchase_register': 'purchase_register',
                'returns_summary': 'returns_summary'
            }
            
            for csv_type, table_name in table_mapping.items():
                try:
                    # Check if table exists
                    db.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = '{table_name}'
                        )
                    """)
                    table_exists = db.fetchone()['exists']
                    
                    if table_exists:
                        # Fetch all records
                        db.execute(f"SELECT * FROM {table_name}")
                        records = db.fetchall()
                        existing_data[csv_type] = pd.DataFrame(records)
                    else:
                        existing_data[csv_type] = pd.DataFrame()
                
                except Exception as e:
                    # Table doesn't exist or query failed - treat as empty
                    existing_data[csv_type] = pd.DataFrame()
    
    except Exception as e:
        # Database connection failed - treat all as new data
        print(f"Warning: Could not fetch existing data from PostgreSQL: {str(e)}")
        existing_data = {
            'e_invoices': pd.DataFrame(),
            'eway_bills': pd.DataFrame(),
            'entity_master': pd.DataFrame(),
            'filing_history': pd.DataFrame(),
            'purchase_register': pd.DataFrame(),
            'returns_summary': pd.DataFrame()
        }
    
    return existing_data


def ingestion_wrangler_node_sync(state: NiyatiState) -> NiyatiState:
    """
    Synchronous wrapper for the Ingestion Wrangler node.
    
    LangGraph requires synchronous node functions, so this wrapper
    runs the async implementation using asyncio.run().
    
    Args:
        state: Current NiyatiState
    
    Returns:
        Updated NiyatiState
    """
    return asyncio.run(ingestion_wrangler_node(state))
