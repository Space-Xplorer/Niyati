"""
Comprehensive Unit Tests for Ingestion Wrangler Agent

This test suite validates the Ingestion Wrangler node functionality:
- CSV validation with existing mock data
- PII hashing for phone and email fields
- SSE message broadcasting
- State updates with validated_data and engineered_features
- Feature engineering computations

Requirements: 1.1-1.8, 2.1-2.8, 16.1, 16.2, 16.3, 19.3
"""

import sys
import os
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
from orchestration.state import create_initial_state, NiyatiState
from orchestration.agent_ingestion_wrangler import (
    ingestion_wrangler_node,
    set_event_queue,
    broadcast_event
)
from utils.pii_hashing import hash_pii


# Fixtures
@pytest.fixture
def mock_csv_files():
    """Create mock CSV files for testing with correct field names."""
    return {
        'e_invoices': pd.DataFrame({
            'Irn': ['IRN001', 'IRN002', 'IRN003'],
            'SellerGstin': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX', '27AAPFU0939F1ZV'],
            'BuyerGstin': ['29AABCU9603R1ZX', '27AAPFU0939F1ZV', '24AACCT1234E1Z5'],
            'TotalVal': [100000.0, 150000.0, 200000.0],
            'DocDt': ['2024-01-10', '2024-01-11', '2024-01-12'],
            'DocNo': ['DOC001', 'DOC002', 'DOC003']
        }),
        'eway_bills': pd.DataFrame({
            'DocNo': ['DOC001', 'DOC002'],
            'VehicleNo': ['MH01AB1234', 'MH02CD5678'],
            'Distance': [100, 200]
        }),
        'entity_master': pd.DataFrame({
            'Gstin': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX', '24AACCT1234E1Z5'],
            'Status': ['Active', 'Active', 'Active'],
            'KycScore': [85, 90, 75],
            'Phone': ['9876543210', '9876543211', '9876543210'],
            'Email': ['abc@example.com', 'xyz@example.com', 'pqr@example.com']
        }),
        'filing_history': pd.DataFrame({
            'Gstin': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX'],
            'Month': ['2024-01', '2024-01'],
            'DelayDays': [5, 10]
        }),
        'purchase_register': pd.DataFrame({
            'BuyerGstin': ['29AABCU9603R1ZX', '27AAPFU0939F1ZV'],
            'SellerGstin': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX'],
            'DocNo': ['DOC001', 'DOC002'],
            'TotalVal': [100000.0, 150000.0]
        }),
        'returns_summary': pd.DataFrame({
            'Gstin': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX'],
            'Gstr1_Liability': [1000000.0, 2000000.0],
            'Gstr3b_Paid': [1000000.0, 1950000.0]
        })
    }


@pytest.fixture
def mock_event_queue():
    """Create a mock event queue for SSE testing."""
    queue = asyncio.Queue()
    set_event_queue(queue)
    return queue


@pytest.fixture
def initial_state(mock_csv_files):
    """Create initial state with mock CSV files."""
    return create_initial_state(mock_csv_files)


# Test 1: CSV Validation with Mock Data
@pytest.mark.asyncio
async def test_csv_validation_with_mock_data(initial_state, mock_event_queue):
    """
    Test that the Ingestion Wrangler validates CSV files correctly.
    
    Requirements: 1.1-1.7
    """
    # Mock the database fetch to return empty data (first run)
    async def mock_fetch_existing():
        return {
            'e_invoices': pd.DataFrame(),
            'eway_bills': pd.DataFrame(),
            'entity_master': pd.DataFrame(),
            'filing_history': pd.DataFrame(),
            'purchase_register': pd.DataFrame(),
            'returns_summary': pd.DataFrame()
        }
    
    with patch('orchestration.agent_ingestion_wrangler._fetch_existing_data', 
               new=mock_fetch_existing):
        result_state = await ingestion_wrangler_node(initial_state)
    
    # Verify no errors
    assert len(result_state['errors']) == 0, f"Unexpected errors: {result_state['errors']}"
    
    # Verify validated_data is populated
    assert result_state['validated_data'] is not None
    assert len(result_state['validated_data']) == 6
    assert 'e_invoices' in result_state['validated_data']
    assert 'eway_bills' in result_state['validated_data']
    assert 'entity_master' in result_state['validated_data']


# Test 2: PII Hashing
@pytest.mark.asyncio
async def test_pii_hashing(initial_state, mock_event_queue):
    """
    Test that PII data (phone and email) is hashed correctly.
    
    Requirements: 16.1, 16.2, 16.3
    """
    async def mock_fetch_existing():
        return {
            'e_invoices': pd.DataFrame(),
            'eway_bills': pd.DataFrame(),
            'entity_master': pd.DataFrame(),
            'filing_history': pd.DataFrame(),
            'purchase_register': pd.DataFrame(),
            'returns_summary': pd.DataFrame()
        }
    
    with patch('orchestration.agent_ingestion_wrangler._fetch_existing_data', 
               new=mock_fetch_existing):
        result_state = await ingestion_wrangler_node(initial_state)
    
    # Get entity_master from validated_data
    entity_master = result_state['validated_data']['entity_master']
    
    # Verify phone_hash column exists
    assert 'phone_hash' in entity_master.columns, "phone_hash column not found"
    
    # Verify email_hash column exists
    assert 'email_hash' in entity_master.columns, "email_hash column not found"
    
    # Verify hashes are not empty
    assert entity_master['phone_hash'].notna().all(), "Some phone hashes are null"
    assert entity_master['email_hash'].notna().all(), "Some email hashes are null"
    
    # Verify hashes are SHA-256 (64 hex characters)
    first_phone_hash = entity_master['phone_hash'].iloc[0]
    assert len(first_phone_hash) == 64, f"Phone hash length is {len(first_phone_hash)}, expected 64"
    
    first_email_hash = entity_master['email_hash'].iloc[0]
    assert len(first_email_hash) == 64, f"Email hash length is {len(first_email_hash)}, expected 64"
    
    # Verify same phone numbers produce same hash (shared contact detection)
    phone_hashes = entity_master['phone_hash'].tolist()
    assert phone_hashes[0] == phone_hashes[2], "Same phone numbers should produce same hash"


# Test 3: SSE Message Broadcasting
@pytest.mark.asyncio
async def test_sse_broadcasting(initial_state, mock_event_queue):
    """
    Test that SSE messages are broadcast during processing.
    
    Requirements: 19.3
    """
    async def mock_fetch_existing():
        return {
            'e_invoices': pd.DataFrame(),
            'eway_bills': pd.DataFrame(),
            'entity_master': pd.DataFrame(),
            'filing_history': pd.DataFrame(),
            'purchase_register': pd.DataFrame(),
            'returns_summary': pd.DataFrame()
        }
    
    with patch('orchestration.agent_ingestion_wrangler._fetch_existing_data', 
               new=mock_fetch_existing):
        result_state = await ingestion_wrangler_node(initial_state)
    
    # Collect all messages from the queue
    messages = []
    while not mock_event_queue.empty():
        messages.append(await mock_event_queue.get())
    
    # Verify expected messages are present
    assert any("Agent 1: Starting CSV validation" in msg for msg in messages), \
        "Missing validation start message"
    
    assert any("Agent 1: Validating" in msg and "rows" in msg for msg in messages), \
        "Missing row count messages"
    
    assert any("Agent 1: Hashing PII data" in msg for msg in messages), \
        "Missing PII hashing message"
    
    assert any("Agent 1: Computing engineered fraud detection features" in msg for msg in messages), \
        "Missing feature engineering message"
    
    assert any("Agent 1: Ingestion Wrangler completed successfully" in msg for msg in messages), \
        "Missing completion message"
    
    print(f"\n✓ Captured {len(messages)} SSE messages")
    for msg in messages:
        print(f"  - {msg}")


# Test 4: State Updates
@pytest.mark.asyncio
async def test_state_updates(initial_state, mock_event_queue):
    """
    Test that state is updated correctly with validated_data and engineered_features.
    
    Requirements: 1.8, 2.8
    """
    async def mock_fetch_existing():
        return {
            'e_invoices': pd.DataFrame(),
            'eway_bills': pd.DataFrame(),
            'entity_master': pd.DataFrame(),
            'filing_history': pd.DataFrame(),
            'purchase_register': pd.DataFrame(),
            'returns_summary': pd.DataFrame()
        }
    
    with patch('orchestration.agent_ingestion_wrangler._fetch_existing_data', 
               new=mock_fetch_existing):
        result_state = await ingestion_wrangler_node(initial_state)
    
    # Verify validated_data is populated
    assert result_state['validated_data'] is not None
    assert isinstance(result_state['validated_data'], dict)
    assert len(result_state['validated_data']) == 6
    
    # Verify all CSV types are present
    expected_types = ['e_invoices', 'eway_bills', 'entity_master', 
                      'filing_history', 'purchase_register', 'returns_summary']
    for csv_type in expected_types:
        assert csv_type in result_state['validated_data'], f"Missing {csv_type} in validated_data"
        assert isinstance(result_state['validated_data'][csv_type], pd.DataFrame)
    
    # Verify engineered_features is populated
    assert result_state['engineered_features'] is not None
    assert isinstance(result_state['engineered_features'], pd.DataFrame)
    assert len(result_state['engineered_features']) > 0, "Engineered features DataFrame is empty"
    
    # Verify feature columns exist
    features = result_state['engineered_features']
    expected_features = [
        'ghost_invoice_pct', 'payment_gap_pct', 'shared_contact_flag',
        'excess_itc_flag', 'avg_delay_days'
    ]
    for feature in expected_features:
        assert feature in features.columns, f"Missing feature: {feature}"


# Test 5: Feature Engineering Computations
@pytest.mark.asyncio
async def test_feature_engineering(initial_state, mock_event_queue):
    """
    Test that engineered features are computed correctly.
    
    Requirements: 2.1-2.8
    """
    async def mock_fetch_existing():
        return {
            'e_invoices': pd.DataFrame(),
            'eway_bills': pd.DataFrame(),
            'entity_master': pd.DataFrame(),
            'filing_history': pd.DataFrame(),
            'purchase_register': pd.DataFrame(),
            'returns_summary': pd.DataFrame()
        }
    
    with patch('orchestration.agent_ingestion_wrangler._fetch_existing_data', 
               new=mock_fetch_existing):
        result_state = await ingestion_wrangler_node(initial_state)
    
    features = result_state['engineered_features']
    
    # Test ghost_invoice_pct computation (Requirement 2.3, 2.4)
    # Invoice IRN003 has no matching eway bill, so it should be flagged
    assert 'ghost_invoice_pct' in features.columns
    
    # Test shared_contact_flag (Requirement 2.5)
    # Entities with Gstin 27AAPFU0939F1ZV and 24AACCT1234E1Z5 share phone number
    assert 'shared_contact_flag' in features.columns
    shared_flags = features['shared_contact_flag'].tolist()
    assert any(flag == 1 for flag in shared_flags), "Expected at least one shared contact flag"
    
    # Test payment_gap computation (Requirement 2.6)
    # Entity 29AABCU9603R1ZX has payment gap: 2000000 - 1950000 = 50000
    assert 'payment_gap' in features.columns
    assert 'payment_gap_pct' in features.columns
    
    # Test excess_itc_flag (Requirement 2.7)
    # All ITC claims in mock data are valid (18% of invoice value)
    assert 'excess_itc_flag' in features.columns
    
    print(f"\n✓ Engineered features computed for {len(features)} entities")
    print(f"  Features: {', '.join(features.columns.tolist())}")


# Test 6: Error Handling - Invalid CSV
@pytest.mark.asyncio
async def test_invalid_csv_handling(mock_event_queue):
    """
    Test that invalid CSV files are handled correctly with descriptive errors.
    
    Requirements: 1.7
    """
    # Create CSV with missing required fields
    invalid_csv_files = {
        'e_invoices': pd.DataFrame({
            'Irn': ['IRN001'],
            # Missing required fields: SellerGstin, BuyerGstin, TotalVal, DocDt, DocNo
        }),
        'eway_bills': pd.DataFrame({
            'DocNo': ['DOC001'],
            'VehicleNo': ['MH01AB1234'],
            'Distance': [100]
        }),
        'entity_master': pd.DataFrame({
            'Gstin': ['27AAPFU0939F1ZV'],
            'Status': ['Active'],
            'KycScore': [85]
        }),
        'filing_history': pd.DataFrame({
            'Gstin': ['27AAPFU0939F1ZV'],
            'Month': ['2024-01'],
            'DelayDays': [5]
        }),
        'purchase_register': pd.DataFrame({
            'BuyerGstin': ['29AABCU9603R1ZX'],
            'SellerGstin': ['27AAPFU0939F1ZV'],
            'DocNo': ['DOC001'],
            'TotalVal': [100000.0]
        }),
        'returns_summary': pd.DataFrame({
            'Gstin': ['27AAPFU0939F1ZV'],
            'Gstr1_Liability': [1000000.0],
            'Gstr3b_Paid': [1000000.0]
        })
    }
    
    state = create_initial_state(invalid_csv_files)
    
    async def mock_fetch_existing():
        return {
            'e_invoices': pd.DataFrame(),
            'eway_bills': pd.DataFrame(),
            'entity_master': pd.DataFrame(),
            'filing_history': pd.DataFrame(),
            'purchase_register': pd.DataFrame(),
            'returns_summary': pd.DataFrame()
        }
    
    with patch('orchestration.agent_ingestion_wrangler._fetch_existing_data', 
               new=mock_fetch_existing):
        result_state = await ingestion_wrangler_node(state)
    
    # Verify errors are captured
    assert len(result_state['errors']) > 0, "Expected validation errors"
    
    # Verify error message contains CSV type
    error_msg = result_state['errors'][0]
    assert 'e_invoices' in error_msg, f"Error message should mention CSV type: {error_msg}"
    
    print(f"\n✓ Error handling test passed")
    print(f"  Error: {error_msg}")


# Test 7: Change Detection
@pytest.mark.asyncio
async def test_change_detection(initial_state, mock_event_queue):
    """
    Test that change detection works correctly for incremental ingestion.
    
    Requirements: Incremental ingestion support
    """
    async def mock_fetch_existing():
        return {
            'e_invoices': pd.DataFrame(),
            'eway_bills': pd.DataFrame(),
            'entity_master': pd.DataFrame(),
            'filing_history': pd.DataFrame(),
            'purchase_register': pd.DataFrame(),
            'returns_summary': pd.DataFrame()
        }
    
    with patch('orchestration.agent_ingestion_wrangler._fetch_existing_data', 
               new=mock_fetch_existing):
        result_state = await ingestion_wrangler_node(initial_state)
    
    # Verify change_summary is populated
    assert result_state['change_summary'] is not None
    assert 'total_new' in result_state['change_summary']
    assert 'total_updated' in result_state['change_summary']
    assert 'total_unchanged' in result_state['change_summary']
    
    # Since we're mocking empty existing data, all records should be new
    assert result_state['change_summary']['total_new'] > 0
    
    print(f"\n✓ Change detection test passed")
    print(f"  New: {result_state['change_summary']['total_new']}")
    print(f"  Updated: {result_state['change_summary']['total_updated']}")
    print(f"  Unchanged: {result_state['change_summary']['total_unchanged']}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
