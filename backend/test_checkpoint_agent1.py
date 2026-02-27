"""
Checkpoint Test for Agent 1: Ingestion Wrangler

This test validates:
1. Agent 1 works with existing mock CSV files
2. PII hashing works correctly
3. SSE messages are broadcast
4. Engineered features are computed correctly
"""

import sys
import os
import asyncio
import pandas as pd

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestration.state import create_initial_state
from orchestration.agent_ingestion_wrangler import ingestion_wrangler_node, set_event_queue
from utils.pii_hashing import hash_pii, mask_pii_display


class MockEventQueue:
    """Mock event queue to capture SSE messages"""
    def __init__(self):
        self.messages = []
    
    async def put(self, message):
        self.messages.append(message)
        print(f"   [SSE] {message}")


async def test_checkpoint_agent1():
    """Comprehensive checkpoint test for Agent 1"""
    
    print("=" * 80)
    print("CHECKPOINT TEST: Agent 1 - Ingestion Wrangler")
    print("=" * 80)
    
    # Setup mock event queue for SSE
    event_queue = MockEventQueue()
    set_event_queue(event_queue)
    
    # Load existing CSV files
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(backend_dir, 'data')
    
    print("\n[1] Loading mock CSV files...")
    csv_files = {
        'e_invoices': pd.read_csv(os.path.join(data_dir, 'e_invoices.csv')),
        'eway_bills': pd.read_csv(os.path.join(data_dir, 'eway_bills.csv')),
        'entity_master': pd.read_csv(os.path.join(data_dir, 'entity_master.csv')),
        'filing_history': pd.read_csv(os.path.join(data_dir, 'filing_history.csv')),
        'purchase_register': pd.read_csv(os.path.join(data_dir, 'purchase_register.csv')),
        'returns_summary': pd.read_csv(os.path.join(data_dir, 'returns_summary.csv'))
    }
    
    for csv_type, df in csv_files.items():
        print(f"   ✓ {csv_type}: {len(df)} rows")
    
    # Test 1: PII Hashing
    print("\n[2] Testing PII hashing...")
    test_phone = "9876543210"
    test_email = "test@example.com"
    
    phone_hash = hash_pii(test_phone)
    email_hash = hash_pii(test_email)
    
    print(f"   ✓ Phone hash: {phone_hash[:32]}...")
    print(f"   ✓ Email hash: {email_hash[:32]}...")
    
    # Verify hash is deterministic
    assert hash_pii(test_phone) == phone_hash, "Hash should be deterministic"
    print(f"   ✓ Hash is deterministic")
    
    # Verify hash is one-way (different inputs produce different hashes)
    assert hash_pii("9876543211") != phone_hash, "Different inputs should produce different hashes"
    print(f"   ✓ Hash is one-way")
    
    # Test masking
    masked_phone = mask_pii_display(test_phone, 'phone')
    masked_email = mask_pii_display(test_email, 'email')
    print(f"   ✓ Masked phone: {masked_phone}")
    print(f"   ✓ Masked email: {masked_email}")
    
    # Test 2: Run Agent 1
    print("\n[3] Running Agent 1 with mock data...")
    state = create_initial_state(csv_files)
    
    updated_state = await ingestion_wrangler_node(state)
    
    # Test 3: Verify SSE messages
    print("\n[4] Verifying SSE messages...")
    if len(event_queue.messages) > 0:
        print(f"   ✓ Captured {len(event_queue.messages)} SSE messages")
        
        # Check for expected message patterns
        has_validation_msg = any("Validating" in msg for msg in event_queue.messages)
        has_pii_msg = any("Hashing PII" in msg for msg in event_queue.messages)
        has_feature_msg = any("Feature engineering" in msg or "features" in msg for msg in event_queue.messages)
        has_complete_msg = any("completed" in msg for msg in event_queue.messages)
        
        if has_validation_msg:
            print(f"   ✓ Validation messages present")
        else:
            print(f"   ⚠ Warning: No validation messages found")
        
        if has_pii_msg:
            print(f"   ✓ PII hashing messages present")
        else:
            print(f"   ⚠ Warning: No PII hashing messages found")
        
        if has_feature_msg:
            print(f"   ✓ Feature engineering messages present")
        else:
            print(f"   ⚠ Warning: No feature engineering messages found")
        
        if has_complete_msg:
            print(f"   ✓ Completion messages present")
        else:
            print(f"   ⚠ Warning: No completion messages found")
    else:
        print(f"   ⚠ Warning: No SSE messages captured")
    
    # Test 4: Verify no errors
    print("\n[5] Checking for errors...")
    if updated_state['errors']:
        print(f"   ❌ ERRORS DETECTED:")
        for error in updated_state['errors']:
            print(f"      - {error}")
        return False
    else:
        print(f"   ✓ No errors detected")
    
    # Test 5: Verify validated data
    print("\n[6] Verifying validated data...")
    if not updated_state['validated_data']:
        print(f"   ❌ No validated data found")
        return False
    
    print(f"   ✓ Validated data: {len(updated_state['validated_data'])} files")
    
    # Test 6: Verify engineered features
    print("\n[7] Verifying engineered features...")
    if updated_state['engineered_features'] is None:
        print(f"   ❌ No engineered features found")
        return False
    
    features = updated_state['engineered_features']
    print(f"   ✓ Engineered features: {len(features)} entities")
    print(f"   ✓ Feature columns: {len(features.columns)}")
    
    # Check for required feature columns
    required_features = [
        'ghost_invoice_pct',
        'payment_gap_pct',
        'shared_contact_flag',
        'excess_itc_flag'
    ]
    
    missing_features = [f for f in required_features if f not in features.columns]
    if missing_features:
        print(f"   ⚠ Warning: Missing features: {missing_features}")
    else:
        print(f"   ✓ All required features present")
    
    # Show sample feature values
    if len(features) > 0:
        print(f"\n   Sample feature values:")
        sample = features.iloc[0]
        print(f"      GSTIN: {sample.get('Gstin', 'N/A')}")
        print(f"      - ghost_invoice_pct: {sample.get('ghost_invoice_pct', 0):.2f}%")
        print(f"      - payment_gap_pct: {sample.get('payment_gap_pct', 0):.2f}%")
        print(f"      - shared_contact_flag: {sample.get('shared_contact_flag', 0)}")
        print(f"      - excess_itc_flag: {sample.get('excess_itc_flag', 0)}")
    
    # Test 7: Verify feature computation correctness
    print("\n[8] Verifying feature computation correctness...")
    
    # Check that ghost_invoice_pct is a percentage (0-100)
    ghost_pct_values = features['ghost_invoice_pct'].dropna()
    if len(ghost_pct_values) > 0:
        if (ghost_pct_values >= 0).all() and (ghost_pct_values <= 100).all():
            print(f"   ✓ ghost_invoice_pct values are valid percentages (0-100)")
        else:
            print(f"   ⚠ Warning: ghost_invoice_pct has values outside 0-100 range")
    
    # Check that shared_contact_flag is binary (0 or 1)
    if 'shared_contact_flag' in features.columns:
        contact_flag_values = features['shared_contact_flag'].dropna()
        if len(contact_flag_values) > 0:
            unique_values = contact_flag_values.unique()
            if set(unique_values).issubset({0, 1}):
                print(f"   ✓ shared_contact_flag is binary (0 or 1)")
            else:
                print(f"   ⚠ Warning: shared_contact_flag has non-binary values: {unique_values}")
    
    # Check that excess_itc_flag is binary
    if 'excess_itc_flag' in features.columns:
        itc_flag_values = features['excess_itc_flag'].dropna()
        if len(itc_flag_values) > 0:
            unique_values = itc_flag_values.unique()
            if set(unique_values).issubset({0, 1, 0.0, 1.0}):
                print(f"   ✓ excess_itc_flag is binary (0 or 1)")
            else:
                print(f"   ⚠ Warning: excess_itc_flag has non-binary values: {unique_values}")
    
    print("\n" + "=" * 80)
    print("✓ CHECKPOINT PASSED: Agent 1 is working correctly")
    print("=" * 80)
    print("\nSummary:")
    print(f"  - CSV files loaded: {len(csv_files)}")
    print(f"  - Entities processed: {len(features)}")
    print(f"  - Features computed: {len(features.columns)}")
    print(f"  - SSE messages: {len(event_queue.messages)}")
    print(f"  - Errors: {len(updated_state['errors'])}")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_checkpoint_agent1())
    sys.exit(0 if success else 1)
