"""
Test script for Ingestion Wrangler Agent

This script tests the Ingestion Wrangler node with the existing mock CSV data.
"""

import sys
import os
import asyncio

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from orchestration.state import create_initial_state
from orchestration.agent_ingestion_wrangler import ingestion_wrangler_node


async def test_ingestion_wrangler():
    """Test the Ingestion Wrangler with existing CSV data."""
    
    print("=" * 80)
    print("Testing Ingestion Wrangler Agent")
    print("=" * 80)
    
    # Load existing CSV files from data directory
    # Get the backend directory (parent of tests directory)
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(backend_dir, 'data')
    
    print("\n1. Loading CSV files...")
    csv_files = {
        'e_invoices': pd.read_csv(os.path.join(data_dir, 'e_invoices.csv')),
        'eway_bills': pd.read_csv(os.path.join(data_dir, 'eway_bills.csv')),
        'entity_master': pd.read_csv(os.path.join(data_dir, 'entity_master.csv')),
        'filing_history': pd.read_csv(os.path.join(data_dir, 'filing_history.csv')),
        'purchase_register': pd.read_csv(os.path.join(data_dir, 'purchase_register.csv')),
        'returns_summary': pd.read_csv(os.path.join(data_dir, 'returns_summary.csv'))
    }
    
    for csv_type, df in csv_files.items():
        print(f"   - {csv_type}: {len(df)} rows, {len(df.columns)} columns")
    
    # Create initial state
    print("\n2. Creating initial state...")
    state = create_initial_state(csv_files)
    print(f"   - State created with {len(state['csv_files'])} CSV files")
    
    # Run Ingestion Wrangler
    print("\n3. Running Ingestion Wrangler node...")
    updated_state = await ingestion_wrangler_node(state)
    
    # Check results
    print("\n4. Checking results...")
    
    if updated_state['errors']:
        print("   ❌ ERRORS DETECTED:")
        for error in updated_state['errors']:
            print(f"      - {error}")
        return False
    
    print("   ✓ No errors detected")
    
    # Check validated data
    if updated_state['validated_data']:
        print(f"   ✓ Validated data: {len(updated_state['validated_data'])} files")
        
        # Check PII hashing
        entity_master = updated_state['validated_data']['entity_master']
        if 'phone_hash' in entity_master.columns:
            print(f"   ✓ PII hashing: phone_hash column added")
            # Show example
            sample_hash = entity_master['phone_hash'].iloc[0]
            print(f"      Example hash: {sample_hash[:32]}...")
        else:
            print("   ⚠ Warning: phone_hash column not found")
        
        if 'email_hash' in entity_master.columns:
            print(f"   ✓ PII hashing: email_hash column added")
        else:
            print("   ⚠ Warning: email_hash column not found")
    else:
        print("   ❌ No validated data found")
        return False
    
    # Check engineered features
    if updated_state['engineered_features'] is not None:
        features = updated_state['engineered_features']
        print(f"   ✓ Engineered features: {len(features)} entities, {len(features.columns)} features")
        print(f"      Features: {', '.join(features.columns.tolist())}")
        
        # Show sample feature values
        if len(features) > 0:
            sample = features.iloc[0]
            print(f"\n   Sample feature values for {sample.get('Gstin', 'N/A')}:")
            print(f"      - ghost_invoice_pct: {sample.get('ghost_invoice_pct', 0):.2f}%")
            print(f"      - payment_gap_pct: {sample.get('payment_gap_pct', 0):.2f}%")
            print(f"      - shared_contact_flag: {sample.get('shared_contact_flag', 0)}")
            print(f"      - excess_itc_flag: {sample.get('excess_itc_flag', 0)}")
    else:
        print("   ❌ No engineered features found")
        return False
    
    print("\n" + "=" * 80)
    print("✓ Ingestion Wrangler test PASSED")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_ingestion_wrangler())
    sys.exit(0 if success else 1)
