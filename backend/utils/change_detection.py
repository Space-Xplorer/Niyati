"""
Change Detection Utility

This module provides functions to detect new and updated records in CSV files
by comparing against existing data in PostgreSQL. This enables incremental
ingestion where only changed data is processed and pushed to Neo4j.

Requirements: Incremental data ingestion
"""

import pandas as pd
from typing import Dict, Tuple, List
import hashlib


def compute_record_hash(row: pd.Series, key_columns: List[str]) -> str:
    """
    Compute a hash for a record based on its content.
    
    Args:
        row: DataFrame row
        key_columns: Columns to include in hash computation
    
    Returns:
        SHA-256 hash of the record
    """
    # Create a string representation of the record
    record_str = '|'.join([str(row[col]) for col in key_columns if col in row.index])
    return hashlib.sha256(record_str.encode('utf-8')).hexdigest()


def detect_changes(
    new_data: pd.DataFrame,
    existing_data: pd.DataFrame,
    primary_key: str,
    content_columns: List[str]
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Detect new, updated, and unchanged records by comparing DataFrames.
    
    Args:
        new_data: New CSV data
        existing_data: Existing data from database
        primary_key: Column name for primary key (e.g., 'Irn', 'Gstin')
        content_columns: Columns to check for changes
    
    Returns:
        Tuple of (new_records, updated_records, unchanged_records)
    """
    if existing_data.empty:
        # No existing data - all records are new
        return new_data, pd.DataFrame(), pd.DataFrame()
    
    # Compute hashes for new data
    new_data = new_data.copy()
    new_data['_record_hash'] = new_data.apply(
        lambda row: compute_record_hash(row, content_columns),
        axis=1
    )
    
    # Compute hashes for existing data
    existing_data = existing_data.copy()
    existing_data['_record_hash'] = existing_data.apply(
        lambda row: compute_record_hash(row, content_columns),
        axis=1
    )
    
    # Find new records (primary key not in existing)
    new_records = new_data[~new_data[primary_key].isin(existing_data[primary_key])]
    
    # Find potentially updated records (primary key exists but hash differs)
    common_keys = new_data[new_data[primary_key].isin(existing_data[primary_key])]
    
    # Merge to compare hashes
    comparison = common_keys.merge(
        existing_data[[primary_key, '_record_hash']],
        on=primary_key,
        suffixes=('_new', '_existing')
    )
    
    # Updated records have different hashes
    updated_mask = comparison['_record_hash_new'] != comparison['_record_hash_existing']
    updated_keys = comparison[updated_mask][primary_key]
    updated_records = new_data[new_data[primary_key].isin(updated_keys)]
    
    # Unchanged records have same hash
    unchanged_keys = comparison[~updated_mask][primary_key]
    unchanged_records = new_data[new_data[primary_key].isin(unchanged_keys)]
    
    # Remove temporary hash column
    new_records = new_records.drop(columns=['_record_hash'])
    updated_records = updated_records.drop(columns=['_record_hash'])
    unchanged_records = unchanged_records.drop(columns=['_record_hash'])
    
    return new_records, updated_records, unchanged_records


def detect_all_changes(
    csv_files: Dict[str, pd.DataFrame],
    existing_data: Dict[str, pd.DataFrame]
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Detect changes across all CSV file types.
    
    Args:
        csv_files: Dictionary of new CSV DataFrames
        existing_data: Dictionary of existing DataFrames from database
    
    Returns:
        Dictionary mapping CSV type to {new, updated, unchanged} DataFrames
    """
    change_detection_config = {
        'e_invoices': {
            'primary_key': 'Irn',
            'content_columns': ['SellerGstin', 'BuyerGstin', 'DocNo', 'DocDt', 'TotalVal']
        },
        'eway_bills': {
            'primary_key': 'DocNo',
            'content_columns': ['VehicleNo', 'Distance']
        },
        'entity_master': {
            'primary_key': 'Gstin',
            'content_columns': ['Status', 'KycScore', 'SharedContact', 'Sector']
        },
        'filing_history': {
            'primary_key': 'Gstin',  # Note: May need composite key with Month
            'content_columns': ['Month', 'DelayDays']
        },
        'purchase_register': {
            'primary_key': 'Irn',
            'content_columns': ['SellerGstin', 'BuyerGstin', 'DocNo', 'TotalVal']
        },
        'returns_summary': {
            'primary_key': 'Gstin',
            'content_columns': ['Gstr1_Liability', 'Gstr3b_Paid']
        }
    }
    
    changes = {}
    
    for csv_type, config in change_detection_config.items():
        if csv_type not in csv_files:
            continue
        
        new_data = csv_files[csv_type]
        existing = existing_data.get(csv_type, pd.DataFrame())
        
        new_records, updated_records, unchanged_records = detect_changes(
            new_data,
            existing,
            config['primary_key'],
            config['content_columns']
        )
        
        changes[csv_type] = {
            'new': new_records,
            'updated': updated_records,
            'unchanged': unchanged_records,
            'total_new': len(new_records),
            'total_updated': len(updated_records),
            'total_unchanged': len(unchanged_records)
        }
    
    return changes
