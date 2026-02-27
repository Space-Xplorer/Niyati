"""
Integration Tests for Agent 2: Graph Architect

This module tests the Graph Architect agent with a real Neo4j connection
to verify end-to-end graph construction, batching, and performance.
Note: These tests require a running Neo4j instance with credentials in .env
"""

import pytest
import pandas as pd
import os
import time
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('backend/.env')

from orchestration.state import create_initial_state
from orchestration.agent_graph_architect import graph_architect_node, get_neo4j_driver


# Skip these tests if Neo4j is not configured
pytestmark = pytest.mark.skipif(
    not all([os.getenv('NEO4J_URI'), os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')]),
    reason="Neo4j credentials not configured"
)


@pytest.fixture(scope="module")
def neo4j_driver():
    """Create a Neo4j driver for testing."""
    driver = get_neo4j_driver()
    yield driver
    driver.close()


@pytest.fixture
def clean_neo4j(neo4j_driver):
    """Clean Neo4j database before each test."""
    with neo4j_driver.session() as session:
        # Delete all nodes and relationships
        session.run("MATCH (n) DETACH DELETE n")
    
    yield
    
    # Clean up after test
    with neo4j_driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")


@pytest.fixture
def sample_data():
    """Create sample data for integration testing."""
    entity_master = pd.DataFrame([
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
    
    e_invoices = pd.DataFrame([
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
    
    eway_bills = pd.DataFrame([
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
    ])
    
    state = create_initial_state({})
    state['validated_data'] = {
        'entity_master': entity_master,
        'e_invoices': e_invoices,
        'eway_bills': eway_bills
    }
    
    return state


@pytest.mark.asyncio
async def test_graph_construction_end_to_end(clean_neo4j, neo4j_driver, sample_data):
    """Test complete graph construction with real Neo4j (Requirements 3.1-3.9)."""
    # Run the agent
    result_state = await graph_architect_node(sample_data)
    
    # Verify state was updated
    assert result_state['graph_built'] is True
    assert len(result_state['errors']) == 0
    
    # Verify nodes were created
    with neo4j_driver.session() as session:
        # Check Taxpayer nodes
        result = session.run("MATCH (t:Taxpayer) RETURN count(t) as count")
        taxpayer_count = result.single()["count"]
        assert taxpayer_count == 3, f"Expected 3 Taxpayer nodes, got {taxpayer_count}"
        
        # Check Invoice nodes
        result = session.run("MATCH (i:Invoice) RETURN count(i) as count")
        invoice_count = result.single()["count"]
        assert invoice_count == 3, f"Expected 3 Invoice nodes, got {invoice_count}"
        
        # Check EwayBill nodes
        result = session.run("MATCH (e:EwayBill) RETURN count(e) as count")
        eway_bill_count = result.single()["count"]
        assert eway_bill_count == 2, f"Expected 2 EwayBill nodes, got {eway_bill_count}"
        
        # Check ISSUED relationships
        result = session.run("MATCH ()-[r:ISSUED]->() RETURN count(r) as count")
        issued_count = result.single()["count"]
        assert issued_count == 3, f"Expected 3 ISSUED relationships, got {issued_count}"
        
        # Check TO relationships
        result = session.run("MATCH ()-[r:TO]->() RETURN count(r) as count")
        to_count = result.single()["count"]
        assert to_count == 3, f"Expected 3 TO relationships, got {to_count}"
        
        # Check BACKED_BY relationships
        result = session.run("MATCH ()-[r:BACKED_BY]->() RETURN count(r) as count")
        backed_by_count = result.single()["count"]
        assert backed_by_count == 2, f"Expected 2 BACKED_BY relationships, got {backed_by_count}"
        
        # Check SHARED_CONTACT relationships
        result = session.run("MATCH ()-[r:SHARED_CONTACT]->() RETURN count(r) as count")
        shared_contact_count = result.single()["count"]
        assert shared_contact_count >= 1, f"Expected at least 1 SHARED_CONTACT relationship, got {shared_contact_count}"


@pytest.mark.asyncio
async def test_circular_trade_pattern(clean_neo4j, neo4j_driver, sample_data):
    """Test that circular trade pattern is created correctly."""
    # Run the agent
    result_state = await graph_architect_node(sample_data)
    
    # Verify circular trade pattern exists: A -> B -> C -> A
    with neo4j_driver.session() as session:
        query = """
        MATCH path = (a:Taxpayer)-[:ISSUED]->(:Invoice)-[:TO]->(b:Taxpayer)
                     -[:ISSUED]->(:Invoice)-[:TO]->(c:Taxpayer)
                     -[:ISSUED]->(:Invoice)-[:TO]->(a)
        RETURN count(path) as circular_paths
        """
        result = session.run(query)
        circular_paths = result.single()["circular_paths"]
        
        # Should find at least one circular path
        assert circular_paths > 0, "No circular trade patterns found"


@pytest.mark.asyncio
async def test_ghost_invoice_detection(clean_neo4j, neo4j_driver, sample_data):
    """Test that ghost invoices (no BACKED_BY) are identifiable."""
    # Run the agent
    result_state = await graph_architect_node(sample_data)
    
    # Verify ghost invoice exists (IRN003 has no eway bill)
    with neo4j_driver.session() as session:
        query = """
        MATCH (i:Invoice)
        WHERE NOT (i)-[:BACKED_BY]->(:EwayBill)
        RETURN i.irn as irn
        """
        result = session.run(query)
        ghost_invoices = [record["irn"] for record in result]
        
        assert 'IRN003' in ghost_invoices, "Ghost invoice IRN003 not detected"


@pytest.mark.asyncio
async def test_shared_contact_detection(clean_neo4j, neo4j_driver, sample_data):
    """Test that shared contact relationships are created correctly."""
    # Run the agent
    result_state = await graph_architect_node(sample_data)
    
    # Verify shared contact relationship exists
    with neo4j_driver.session() as session:
        query = """
        MATCH (t1:Taxpayer)-[r:SHARED_CONTACT]-(t2:Taxpayer)
        WHERE r.contact_type = 'phone'
        RETURN t1.gstin as gstin1, t2.gstin as gstin2, r.contact_type as type
        """
        result = session.run(query)
        shared_contacts = list(result)
        
        assert len(shared_contacts) > 0, "No shared contact relationships found"
        
        # Verify the right entities are connected
        gstins = {shared_contacts[0]["gstin1"], shared_contacts[0]["gstin2"]}
        assert '27AAPFU0939F1ZV' in gstins
        assert '29AABCU9603R1ZX' in gstins


@pytest.mark.asyncio
async def test_idempotency(clean_neo4j, neo4j_driver, sample_data):
    """Test that running the agent twice doesn't create duplicates."""
    # Run the agent first time
    result_state1 = await graph_architect_node(sample_data)
    
    # Count nodes after first run
    with neo4j_driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        count_after_first = result.single()["count"]
    
    # Run the agent second time
    result_state2 = await graph_architect_node(sample_data)
    
    # Count nodes after second run
    with neo4j_driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        count_after_second = result.single()["count"]
    
    # Should have same count (MERGE ensures idempotency)
    assert count_after_first == count_after_second, "Duplicate nodes created on second run"


@pytest.mark.asyncio
async def test_performance_large_dataset(clean_neo4j, neo4j_driver):
    """Test performance with 1,500 invoices (Requirement 17.2)."""
    # Create large dataset
    entity_master = pd.DataFrame([
        {
            'GSTIN': f'GSTIN{i:04d}',
            'Legal Name': f'Company {i}',
            'Address': f'Address {i}'
        }
        for i in range(100)
    ])
    
    e_invoices = pd.DataFrame([
        {
            'IRN': f'IRN{i:04d}',
            'DocNo': f'DOC{i:04d}',
            'Taxable Value': 100000.0,
            'Doc Date': '2024-01-15',
            'Supplier GSTIN': f'GSTIN{i % 100:04d}',
            'Recipient GSTIN': f'GSTIN{(i + 1) % 100:04d}'
        }
        for i in range(1500)
    ])
    
    eway_bills = pd.DataFrame([
        {
            'DocNo': f'DOC{i:04d}',
            'Vehicle No': f'MH01AB{i:04d}',
            'Distance': 150,
            'Generated Date': '2024-01-16'
        }
        for i in range(1500)
    ])
    
    state = create_initial_state({})
    state['validated_data'] = {
        'entity_master': entity_master,
        'e_invoices': e_invoices,
        'eway_bills': eway_bills
    }
    
    # Measure execution time
    start_time = time.time()
    
    result_state = await graph_architect_node(state)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Should complete in < 30 seconds
    assert execution_time < 30, f"Graph construction took {execution_time}s, expected < 30s"
    assert result_state['graph_built'] is True
    
    # Verify all nodes were created
    with neo4j_driver.session() as session:
        result = session.run("MATCH (i:Invoice) RETURN count(i) as count")
        invoice_count = result.single()["count"]
        assert invoice_count == 1500, f"Expected 1500 invoices, got {invoice_count}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
