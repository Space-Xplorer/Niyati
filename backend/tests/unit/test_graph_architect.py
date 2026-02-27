"""
Unit Tests for Agent 2: Graph Architect

This module tests the Graph Architect agent's ability to build a Neo4j knowledge graph
from validated CSV data, including node creation, relationship creation, and batching.

Requirements: 3.1-3.9, 17.2
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import asyncio

from orchestration.state import NiyatiState, create_initial_state
from orchestration.agent_graph_architect import (
    graph_architect_node,
    _prepare_taxpayer_nodes,
    _prepare_invoice_nodes,
    _prepare_eway_bill_nodes,
    _prepare_issued_relationships,
    _prepare_to_relationships,
    _prepare_backed_by_relationships,
    _prepare_shared_contact_relationships
)
from utils.pii_hashing import hash_pii


@pytest.fixture
def sample_entity_master():
    """Sample entity_master DataFrame for testing."""
    return pd.DataFrame([
        {
            'GSTIN': '27AAPFU0939F1ZV',
            'Legal Name': 'ABC Corp',
            'Phone': '9876543210',
            'Email': 'abc@example.com',
            'Address': '123 Main St'
        },
        {
            'GSTIN': '29AABCU9603R1ZX',
            'Legal Name': 'XYZ Ltd',
            'Phone': '9876543210',  # Shared phone
            'Email': 'xyz@example.com',
            'Address': '456 Oak Ave'
        },
        {
            'GSTIN': '24AACDE1234F1Z5',
            'Legal Name': 'DEF Inc',
            'Phone': '8765432109',
            'Email': 'def@example.com',
            'Address': '789 Pine Rd'
        }
    ])


@pytest.fixture
def sample_e_invoices():
    """Sample e_invoices DataFrame for testing."""
    return pd.DataFrame([
        {
            'IRN': 'IRN001',
            'DocNo': 'DOC001',
            'Taxable Value': 100000.0,
            'Doc Date': '2024-01-15',
            'Supplier GSTIN': '27AAPFU0939F1ZV',
            'Recipient GSTIN': '29AABCU9603R1ZX'
        },
        {
            'IRN': 'IRN002',
            'DocNo': 'DOC002',
            'Taxable Value': 150000.0,
            'Doc Date': '2024-01-20',
            'Supplier GSTIN': '29AABCU9603R1ZX',
            'Recipient GSTIN': '24AACDE1234F1Z5'
        },
        {
            'IRN': 'IRN003',
            'DocNo': 'DOC003',
            'Taxable Value': 200000.0,
            'Doc Date': '2024-01-25',
            'Supplier GSTIN': '24AACDE1234F1Z5',
            'Recipient GSTIN': '27AAPFU0939F1ZV'
        }
    ])


@pytest.fixture
def sample_eway_bills():
    """Sample eway_bills DataFrame for testing."""
    return pd.DataFrame([
        {
            'DocNo': 'DOC001',
            'Vehicle No': 'MH01AB1234',
            'Distance': 150,
            'Generated Date': '2024-01-16'
        },
        {
            'DocNo': 'DOC002',
            'Vehicle No': 'MH02CD5678',
            'Distance': 200,
            'Generated Date': '2024-01-21'
        }
        # DOC003 has no eway bill (ghost invoice)
    ])


@pytest.fixture
def validated_state(sample_entity_master, sample_e_invoices, sample_eway_bills):
    """Create a validated state for testing."""
    state = create_initial_state({})
    state['validated_data'] = {
        'entity_master': sample_entity_master,
        'e_invoices': sample_e_invoices,
        'eway_bills': sample_eway_bills
    }
    return state


class TestTaxpayerNodePreparation:
    """Test Taxpayer node data preparation."""
    
    def test_prepare_taxpayer_nodes_basic(self, sample_entity_master):
        """Test basic Taxpayer node preparation."""
        nodes = _prepare_taxpayer_nodes(sample_entity_master)
        
        assert len(nodes) == 3
        assert nodes[0]['gstin'] == '27AAPFU0939F1ZV'
        assert nodes[0]['business_name'] == 'ABC Corp'
        assert nodes[0]['address'] == '123 Main St'
    
    def test_prepare_taxpayer_nodes_pii_hashing(self, sample_entity_master):
        """Test that PII fields are hashed (Requirement 16.2)."""
        nodes = _prepare_taxpayer_nodes(sample_entity_master)
        
        # Check that phone and email are hashed
        assert 'phone_hash' in nodes[0]
        assert 'email_hash' in nodes[0]
        
        # Verify hash values match expected
        expected_phone_hash = hash_pii('9876543210')
        expected_email_hash = hash_pii('abc@example.com')
        
        assert nodes[0]['phone_hash'] == expected_phone_hash
        assert nodes[0]['email_hash'] == expected_email_hash
    
    def test_prepare_taxpayer_nodes_shared_phone(self, sample_entity_master):
        """Test that shared phone numbers produce same hash."""
        nodes = _prepare_taxpayer_nodes(sample_entity_master)
        
        # First two entities share phone number
        assert nodes[0]['phone_hash'] == nodes[1]['phone_hash']
        assert nodes[0]['phone_hash'] != nodes[2]['phone_hash']


class TestInvoiceNodePreparation:
    """Test Invoice node data preparation."""
    
    def test_prepare_invoice_nodes_basic(self, sample_e_invoices):
        """Test basic Invoice node preparation (Requirement 3.2)."""
        nodes = _prepare_invoice_nodes(sample_e_invoices)
        
        assert len(nodes) == 3
        assert nodes[0]['irn'] == 'IRN001'
        assert nodes[0]['doc_no'] == 'DOC001'
        assert nodes[0]['invoice_value'] == 100000.0
        assert nodes[0]['invoice_date'] == '2024-01-15'
        assert nodes[0]['seller_gstin'] == '27AAPFU0939F1ZV'
        assert nodes[0]['buyer_gstin'] == '29AABCU9603R1ZX'
    
    def test_prepare_invoice_nodes_all_fields(self, sample_e_invoices):
        """Test that all required fields are present."""
        nodes = _prepare_invoice_nodes(sample_e_invoices)
        
        required_fields = ['irn', 'doc_no', 'invoice_value', 'invoice_date', 
                          'seller_gstin', 'buyer_gstin']
        
        for node in nodes:
            for field in required_fields:
                assert field in node


class TestEwayBillNodePreparation:
    """Test EwayBill node data preparation."""
    
    def test_prepare_eway_bill_nodes_basic(self, sample_eway_bills):
        """Test basic EwayBill node preparation (Requirement 3.3)."""
        nodes = _prepare_eway_bill_nodes(sample_eway_bills)
        
        assert len(nodes) == 2
        assert nodes[0]['doc_no'] == 'DOC001'
        assert nodes[0]['vehicle_no'] == 'MH01AB1234'
        assert nodes[0]['distance'] == 150
        assert nodes[0]['generated_date'] == '2024-01-16'


class TestRelationshipPreparation:
    """Test relationship data preparation."""
    
    def test_prepare_issued_relationships(self, sample_e_invoices):
        """Test ISSUED relationship preparation (Requirement 3.6)."""
        rels = _prepare_issued_relationships(sample_e_invoices)
        
        assert len(rels) == 3
        assert rels[0]['source_id'] == '27AAPFU0939F1ZV'
        assert rels[0]['target_id'] == 'IRN001'
    
    def test_prepare_to_relationships(self, sample_e_invoices):
        """Test TO relationship preparation (Requirement 3.7)."""
        rels = _prepare_to_relationships(sample_e_invoices)
        
        assert len(rels) == 3
        assert rels[0]['source_id'] == 'IRN001'
        assert rels[0]['target_id'] == '29AABCU9603R1ZX'
    
    def test_prepare_backed_by_relationships(self, sample_e_invoices, sample_eway_bills):
        """Test BACKED_BY relationship preparation (Requirement 3.8)."""
        rels = _prepare_backed_by_relationships(sample_e_invoices, sample_eway_bills)
        
        # Only 2 invoices have matching eway bills
        assert len(rels) == 2
        assert rels[0]['source_id'] == 'IRN001'
        assert rels[0]['target_id'] == 'DOC001'
        assert rels[1]['source_id'] == 'IRN002'
        assert rels[1]['target_id'] == 'DOC002'
    
    def test_prepare_backed_by_ghost_invoice(self, sample_e_invoices, sample_eway_bills):
        """Test that ghost invoices (no eway bill) don't get BACKED_BY relationships."""
        rels = _prepare_backed_by_relationships(sample_e_invoices, sample_eway_bills)
        
        # IRN003 should not have a BACKED_BY relationship
        irn003_rels = [r for r in rels if r['source_id'] == 'IRN003']
        assert len(irn003_rels) == 0
    
    def test_prepare_shared_contact_relationships(self, sample_entity_master):
        """Test SHARED_CONTACT relationship preparation (Requirement 3.9)."""
        rels = _prepare_shared_contact_relationships(sample_entity_master)
        
        # First two entities share phone number
        assert len(rels) >= 1
        
        # Find the phone sharing relationship
        phone_rels = [r for r in rels if r['contact_type'] == 'phone']
        assert len(phone_rels) == 1
        
        # Check that it connects the right entities
        rel = phone_rels[0]
        assert rel['source_id'] == '27AAPFU0939F1ZV'
        assert rel['target_id'] == '29AABCU9603R1ZX'
        assert rel['contact_value'] == hash_pii('9876543210')
    
    def test_prepare_shared_contact_no_duplicates(self, sample_entity_master):
        """Test that no duplicate relationships are created."""
        rels = _prepare_shared_contact_relationships(sample_entity_master)
        
        # Check for duplicate pairs
        pairs = set()
        for rel in rels:
            pair = tuple(sorted([rel['source_id'], rel['target_id']]))
            assert pair not in pairs, "Duplicate relationship found"
            pairs.add(pair)


class TestGraphArchitectNode:
    """Test the complete Graph Architect node."""
    
    @pytest.mark.asyncio
    async def test_graph_architect_node_success(self, validated_state):
        """Test successful graph construction."""
        with patch('orchestration.agent_graph_architect.get_neo4j_driver') as mock_driver:
            # Mock Neo4j driver and session
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
            
            # Mock session.run to return successful results
            mock_result = MagicMock()
            mock_result.single.return_value = {"created": 1}
            mock_session.run.return_value = mock_result
            
            # Run the agent
            result_state = await graph_architect_node(validated_state)
            
            # Verify state was updated
            assert result_state['graph_built'] is True
            assert len(result_state['errors']) == 0
    
    @pytest.mark.asyncio
    async def test_graph_architect_node_error_handling(self, validated_state):
        """Test error handling when Neo4j connection fails."""
        with patch('orchestration.agent_graph_architect.get_neo4j_driver') as mock_driver:
            # Simulate connection failure
            mock_driver.side_effect = Exception("Connection failed")
            
            # Run the agent
            result_state = await graph_architect_node(validated_state)
            
            # Verify error was captured
            assert result_state['graph_built'] is False
            assert len(result_state['errors']) > 0
            assert "Agent 2 failed" in result_state['errors'][0]
    
    @pytest.mark.asyncio
    async def test_graph_architect_node_batching(self, validated_state):
        """Test that batching is used for large datasets (Requirement 17.2)."""
        # Create a larger dataset
        large_invoices = pd.DataFrame([
            {
                'IRN': f'IRN{i:04d}',
                'DocNo': f'DOC{i:04d}',
                'Taxable Value': 100000.0,
                'Doc Date': '2024-01-15',
                'Supplier GSTIN': '27AAPFU0939F1ZV',
                'Recipient GSTIN': '29AABCU9603R1ZX'
            }
            for i in range(1500)  # 1500 invoices
        ])
        
        validated_state['validated_data']['e_invoices'] = large_invoices
        
        with patch('orchestration.agent_graph_architect.get_neo4j_driver') as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.single.return_value = {"created": 500}
            mock_session.run.return_value = mock_result
            
            # Run the agent
            result_state = await graph_architect_node(validated_state)
            
            # Verify batching occurred (should have multiple calls)
            # With batch_size=500 and 1500 invoices, we expect 3 batches
            assert mock_session.run.call_count >= 3


class TestPerformance:
    """Test performance requirements."""
    
    @pytest.mark.asyncio
    async def test_graph_construction_performance(self, validated_state):
        """Test that graph construction completes in < 30 seconds for 1,500 invoices (Requirement 17.2)."""
        # Create dataset with 1500 invoices
        large_invoices = pd.DataFrame([
            {
                'IRN': f'IRN{i:04d}',
                'DocNo': f'DOC{i:04d}',
                'Taxable Value': 100000.0,
                'Doc Date': '2024-01-15',
                'Supplier GSTIN': '27AAPFU0939F1ZV',
                'Recipient GSTIN': '29AABCU9603R1ZX'
            }
            for i in range(1500)
        ])
        
        validated_state['validated_data']['e_invoices'] = large_invoices
        
        with patch('orchestration.agent_graph_architect.get_neo4j_driver') as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.single.return_value = {"created": 500}
            mock_session.run.return_value = mock_result
            
            # Measure execution time
            import time
            start_time = time.time()
            
            result_state = await graph_architect_node(validated_state)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should complete in < 30 seconds (with mocked Neo4j, should be much faster)
            assert execution_time < 30, f"Graph construction took {execution_time}s, expected < 30s"
            assert result_state['graph_built'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
