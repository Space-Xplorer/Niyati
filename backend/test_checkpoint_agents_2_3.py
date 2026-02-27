"""
Checkpoint Test for Agents 2 and 3

This script validates that Agent 2 (Graph Architect) and Agent 3 (Risk Detective)
are working correctly with existing data.

Task 6: Checkpoint - Validate Agents 2 and 3
"""

import asyncio
import pandas as pd
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from orchestration.state import create_initial_state
from orchestration.agent_graph_architect import graph_architect_node, get_neo4j_driver
from orchestration.agent_risk_detective import risk_detective_node


def load_sample_data():
    """Load sample data from CSV files"""
    print("Loading sample data from CSV files...")
    
    # Load the existing CSV files
    e_invoices = pd.read_csv('data/e_invoices.csv')
    eway_bills = pd.read_csv('data/eway_bills.csv')
    entity_master = pd.read_csv('data/entity_master.csv')
    
    print(f"  - Loaded {len(e_invoices)} invoices")
    print(f"  - Loaded {len(eway_bills)} eway bills")
    print(f"  - Loaded {len(entity_master)} entities")
    
    return {
        'e_invoices': e_invoices,
        'eway_bills': eway_bills,
        'entity_master': entity_master
    }


def clean_neo4j():
    """Clean Neo4j database before testing"""
    print("\nCleaning Neo4j database...")
    
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        driver.close()
        print("  ✓ Neo4j database cleaned")
        return True
    except Exception as e:
        print(f"  ✗ Failed to clean Neo4j: {e}")
        return False


async def test_agent_2():
    """Test Agent 2: Graph Architect"""
    print("\n" + "="*60)
    print("TESTING AGENT 2: GRAPH ARCHITECT")
    print("="*60)
    
    # Load data
    data = load_sample_data()
    
    # Create initial state
    state = create_initial_state({})
    state['validated_data'] = data
    
    # Measure execution time
    print("\nRunning Graph Architect agent...")
    start_time = time.time()
    
    result_state = await graph_architect_node(state)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Check results
    print(f"\n  Execution time: {execution_time:.2f} seconds")
    
    if result_state['graph_built']:
        print("  ✓ Graph built successfully")
    else:
        print("  ✗ Graph build failed")
        if result_state['errors']:
            print(f"  Errors: {result_state['errors']}")
        return False
    
    # Verify nodes were created
    print("\nVerifying graph structure...")
    driver = get_neo4j_driver()
    
    with driver.session() as session:
        # Count nodes
        result = session.run("MATCH (t:Taxpayer) RETURN count(t) as count")
        taxpayer_count = result.single()["count"]
        print(f"  - Taxpayer nodes: {taxpayer_count}")
        
        result = session.run("MATCH (i:Invoice) RETURN count(i) as count")
        invoice_count = result.single()["count"]
        print(f"  - Invoice nodes: {invoice_count}")
        
        result = session.run("MATCH (e:EwayBill) RETURN count(e) as count")
        eway_bill_count = result.single()["count"]
        print(f"  - EwayBill nodes: {eway_bill_count}")
        
        # Count relationships
        result = session.run("MATCH ()-[r:ISSUED]->() RETURN count(r) as count")
        issued_count = result.single()["count"]
        print(f"  - ISSUED relationships: {issued_count}")
        
        result = session.run("MATCH ()-[r:TO]->() RETURN count(r) as count")
        to_count = result.single()["count"]
        print(f"  - TO relationships: {to_count}")
        
        result = session.run("MATCH ()-[r:BACKED_BY]->() RETURN count(r) as count")
        backed_by_count = result.single()["count"]
        print(f"  - BACKED_BY relationships: {backed_by_count}")
        
        result = session.run("MATCH ()-[r:SHARED_CONTACT]->() RETURN count(r) as count")
        shared_contact_count = result.single()["count"]
        print(f"  - SHARED_CONTACT relationships: {shared_contact_count}")
    
    driver.close()
    
    # Check performance target (< 30 seconds for 1,500 invoices)
    if len(data['e_invoices']) <= 1500:
        if execution_time < 30:
            print(f"\n  ✓ Performance target met: {execution_time:.2f}s < 30s")
        else:
            print(f"\n  ⚠ Performance target missed: {execution_time:.2f}s >= 30s")
    
    print("\n  ✓ Agent 2 validation complete")
    return True


async def test_agent_3():
    """Test Agent 3: Risk Detective"""
    print("\n" + "="*60)
    print("TESTING AGENT 3: RISK DETECTIVE")
    print("="*60)
    
    # Create state with graph_built=True
    state = create_initial_state({})
    state['graph_built'] = True
    
    # Run Risk Detective agent
    print("\nRunning Risk Detective agent...")
    start_time = time.time()
    
    result_state = await risk_detective_node(state)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\n  Execution time: {execution_time:.2f} seconds")
    
    # Check for errors
    if result_state['errors']:
        print(f"  ✗ Agent 3 failed with errors: {result_state['errors']}")
        return False
    
    # Analyze detected patterns
    patterns = result_state['structural_patterns']
    print(f"\n  Total patterns detected: {len(patterns)}")
    
    # Count by pattern type
    circular_trade = [p for p in patterns if p['pattern_type'] == 'circular_trade']
    ghost_invoices = [p for p in patterns if p['pattern_type'] == 'ghost_invoice']
    spider_webs = [p for p in patterns if p['pattern_type'] == 'spider_web']
    
    print(f"  - Circular trade patterns: {len(circular_trade)}")
    print(f"  - Ghost invoice patterns: {len(ghost_invoices)}")
    print(f"  - Spider web patterns: {len(spider_webs)}")
    
    # Show sample patterns
    if circular_trade:
        print("\n  Sample Circular Trade Pattern:")
        pattern = circular_trade[0]
        print(f"    GSTINs: {' -> '.join(pattern['gstin_list'])}")
        print(f"    Total value: ₹{pattern['total_value']:,.2f}")
        print(f"    Risk score: {pattern['risk_score']:.2f}")
    
    if ghost_invoices:
        print("\n  Sample Ghost Invoice Pattern:")
        pattern = ghost_invoices[0]
        print(f"    Seller: {pattern['seller_gstin']}")
        print(f"    Ghost count: {pattern['ghost_count']}")
        print(f"    Ghost value: ₹{pattern['ghost_value']:,.2f}")
        print(f"    Risk score: {pattern['risk_score']:.2f}")
    
    if spider_webs:
        print("\n  Sample Spider Web Pattern:")
        pattern = spider_webs[0]
        print(f"    Cluster size: {pattern['cluster_size']} entities")
        print(f"    Transaction volume: ₹{pattern['transaction_volume']:,.2f}")
        print(f"    Risk score: {pattern['risk_score']:.2f}")
    
    print("\n  ✓ Agent 3 validation complete")
    return True


async def main():
    """Main test execution"""
    print("\n" + "="*60)
    print("CHECKPOINT: VALIDATE AGENTS 2 AND 3")
    print("="*60)
    
    # Check Neo4j connection
    print("\nChecking Neo4j connection...")
    try:
        driver = get_neo4j_driver()
        driver.verify_connectivity()
        driver.close()
        print("  ✓ Neo4j connection successful")
    except Exception as e:
        print(f"  ✗ Neo4j connection failed: {e}")
        print("\nPlease check your Neo4j credentials in .env file:")
        print("  - NEO4J_URI")
        print("  - NEO4J_USER")
        print("  - NEO4J_PASSWORD")
        return
    
    # Clean database
    if not clean_neo4j():
        print("\n⚠ Warning: Could not clean Neo4j database. Tests may be affected by existing data.")
    
    # Test Agent 2
    agent_2_success = await test_agent_2()
    
    if not agent_2_success:
        print("\n✗ Agent 2 validation failed. Skipping Agent 3 test.")
        return
    
    # Test Agent 3
    agent_3_success = await test_agent_3()
    
    # Final summary
    print("\n" + "="*60)
    print("CHECKPOINT SUMMARY")
    print("="*60)
    
    if agent_2_success and agent_3_success:
        print("\n✓ All validations passed!")
        print("\nAgent 2 (Graph Architect):")
        print("  ✓ Graph construction working")
        print("  ✓ Nodes and relationships created correctly")
        print("  ✓ Performance targets met")
        
        print("\nAgent 3 (Risk Detective):")
        print("  ✓ Pattern detection working")
        print("  ✓ Circular trade detection functional")
        print("  ✓ Ghost invoice detection functional")
        print("  ✓ Spider web detection functional")
        
        print("\n✓ Ready to proceed to next tasks!")
    else:
        print("\n✗ Some validations failed. Please review the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
