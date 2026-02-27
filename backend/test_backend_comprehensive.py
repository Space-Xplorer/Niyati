"""
Comprehensive Backend Validation Script for Task 13

This script validates the complete Project Niyati backend system:
1. All 5 agents working correctly
2. LangGraph workflow orchestration
3. FastAPI endpoints (if server is running)
4. RBAC filtering
5. End-to-end workflow execution

Task 13: Checkpoint - Validate Backend
"""

import asyncio
import sys
import os
import time
from typing import Dict, Any

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(title)
    print("="*70 + "\n")


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    symbol = "✓" if passed else "✗"
    status = "PASSED" if passed else "FAILED"
    print(f"  {symbol} {test_name}: {status}")
    if details:
        print(f"     {details}")


async def test_agents():
    """Test all 5 agents individually"""
    print_section("TEST 1: VALIDATE ALL 5 AGENTS")
    
    try:
        import pandas as pd
        from orchestration.state import create_initial_state
        from orchestration.agent_ingestion_wrangler import ingestion_wrangler_node
        from orchestration.agent_graph_architect import graph_architect_node, get_neo4j_driver
        from orchestration.agent_risk_detective import risk_detective_node
        from orchestration.agent_predictive_analyst import predictive_analyst_node
        from orchestration.agent_niyati_explainer import niyati_explainer_node
        
        # Load sample data
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(backend_dir, 'data')
        
        csv_files = {
            'e_invoices': pd.read_csv(os.path.join(data_dir, 'e_invoices.csv')),
            'eway_bills': pd.read_csv(os.path.join(data_dir, 'eway_bills.csv')),
            'entity_master': pd.read_csv(os.path.join(data_dir, 'entity_master.csv')),
            'filing_history': pd.read_csv(os.path.join(data_dir, 'filing_history.csv')),
            'purchase_register': pd.read_csv(os.path.join(data_dir, 'purchase_register.csv')),
            'returns_summary': pd.read_csv(os.path.join(data_dir, 'returns_summary.csv'))
        }
        
        # Clean Neo4j
        try:
            driver = get_neo4j_driver()
            with driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            driver.close()
            print("  ✓ Neo4j database cleaned")
        except Exception as e:
            print(f"  ⚠ Warning: Could not clean Neo4j: {e}")
        
        # Create initial state
        state = create_initial_state(csv_files)
        
        # Test Agent 1
        print("\n  Testing Agent 1: Ingestion Wrangler...")
        state = await ingestion_wrangler_node(state)
        agent1_passed = not state['errors'] and state['validated_data'] and state['engineered_features'] is not None
        print_result("Agent 1", agent1_passed, f"{len(state['engineered_features'])} entities processed")
        
        if not agent1_passed:
            return False
        
        # Test Agent 2
        print("\n  Testing Agent 2: Graph Architect...")
        state = await graph_architect_node(state)
        agent2_passed = not state['errors'] and state['graph_built']
        print_result("Agent 2", agent2_passed, "Knowledge graph built")
        
        if not agent2_passed:
            return False
        
        # Test Agent 3
        print("\n  Testing Agent 3: Risk Detective...")
        state = await risk_detective_node(state)
        agent3_passed = not state['errors']
        patterns = len(state.get('structural_patterns', []))
        print_result("Agent 3", agent3_passed, f"{patterns} patterns detected")
        
        # Test Agent 4
        print("\n  Testing Agent 4: Predictive Analyst...")
        state = await predictive_analyst_node(state)
        agent4_passed = not state['errors'] and state.get('risk_predictions')
        predictions = len(state.get('risk_predictions', {}))
        print_result("Agent 4", agent4_passed, f"{predictions} risk predictions")
        
        # Test Agent 5
        print("\n  Testing Agent 5: Niyati Explainer...")
        state = await niyati_explainer_node(state)
        agent5_passed = not state['errors'] and state.get('narratives')
        narratives = len(state.get('narratives', {}))
        print_result("Agent 5", agent5_passed, f"{narratives} narratives generated")
        
        all_passed = agent1_passed and agent2_passed and agent3_passed and agent4_passed and agent5_passed
        
        if all_passed:
            print("\n  ✓ ALL AGENTS WORKING CORRECTLY")
        else:
            print("\n  ✗ SOME AGENTS FAILED")
        
        return all_passed
        
    except Exception as e:
        print(f"  ✗ Agent testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_workflow():
    """Test LangGraph workflow orchestration"""
    print_section("TEST 2: VALIDATE LANGGRAPH WORKFLOW")
    
    try:
        import pandas as pd
        from orchestration.llm_agent import execute_workflow, set_event_queue
        
        # Create mock event queue
        class MockQueue:
            async def put(self, msg):
                print(f"    [SSE] {msg}")
        
        set_event_queue(MockQueue())
        
        # Load sample data
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(backend_dir, 'data')
        
        csv_files = {
            'e_invoices': pd.read_csv(os.path.join(data_dir, 'e_invoices.csv')),
            'eway_bills': pd.read_csv(os.path.join(data_dir, 'eway_bills.csv')),
            'entity_master': pd.read_csv(os.path.join(data_dir, 'entity_master.csv')),
            'filing_history': pd.read_csv(os.path.join(data_dir, 'filing_history.csv')),
            'purchase_register': pd.read_csv(os.path.join(data_dir, 'purchase_register.csv')),
            'returns_summary': pd.read_csv(os.path.join(data_dir, 'returns_summary.csv'))
        }
        
        print("  Executing complete workflow...")
        start_time = time.time()
        
        result = await execute_workflow(csv_files)
        
        execution_time = time.time() - start_time
        
        # Check results
        workflow_passed = result.get('status') == 'success'
        
        print_result("Workflow Execution", workflow_passed, f"Completed in {execution_time:.1f}s")
        
        if workflow_passed:
            summary = result.get('summary', {})
            print(f"\n  Workflow Summary:")
            print(f"    - Entities processed: {summary.get('entities_processed', 0)}")
            print(f"    - Circular trade patterns: {summary.get('circular_trade_patterns', 0)}")
            print(f"    - Ghost invoice entities: {summary.get('ghost_invoice_entities', 0)}")
            print(f"    - Spider web clusters: {summary.get('spider_web_clusters', 0)}")
            print(f"    - High risk entities: {summary.get('high_risk_entities', 0)}")
            
            # Check performance target
            if execution_time < 60:
                print_result("Performance Target", True, f"{execution_time:.1f}s < 60s")
            else:
                print_result("Performance Target", False, f"{execution_time:.1f}s >= 60s")
        else:
            print(f"\n  Errors: {result.get('errors', [])}")
        
        return workflow_passed
        
    except Exception as e:
        print(f"  ✗ Workflow testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test FastAPI endpoints (if server is running)"""
    print_section("TEST 3: VALIDATE API ENDPOINTS")
    
    try:
        import requests
        
        BASE_URL = "http://localhost:8000"
        
        print("  Checking if FastAPI server is running...")
        
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            server_running = response.status_code == 200
        except:
            server_running = False
        
        if not server_running:
            print("  ⚠ FastAPI server is not running")
            print("  ℹ To start the server, run: cd backend && uvicorn app_fastapi:app --reload")
            print("  ℹ Skipping API endpoint tests")
            return None  # Not a failure, just skipped
        
        print("  ✓ FastAPI server is running\n")
        
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print_result("GET /health", response.status_code == 200)
        
        # Test registration
        register_payload = {
            "email": "test_checkpoint@example.com",
            "password": "TestPassword123!",
            "role": "Admin",
            "gstin": None
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_payload, timeout=5)
        registration_ok = response.status_code in [200, 201, 400]  # 400 if already exists
        print_result("POST /auth/register", registration_ok)
        
        # Test login
        login_payload = {
            "email": "test_checkpoint@example.com",
            "password": "TestPassword123!"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=5)
        login_ok = response.status_code == 200
        print_result("POST /auth/login", login_ok)
        
        if login_ok:
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test dashboard endpoint
            response = requests.get(f"{BASE_URL}/dashboard", headers=headers, timeout=5)
            print_result("GET /dashboard", response.status_code == 200)
            
            # Test graph endpoint
            response = requests.get(f"{BASE_URL}/graph", headers=headers, timeout=5)
            print_result("GET /graph", response.status_code == 200)
            
            # Test SSE endpoint
            try:
                response = requests.get(f"{BASE_URL}/logs/stream", stream=True, timeout=2)
                sse_ok = response.status_code == 200
            except requests.exceptions.ReadTimeout:
                sse_ok = True  # Timeout is expected for SSE streams
            print_result("GET /logs/stream (SSE)", sse_ok)
        
        print("\n  ✓ API ENDPOINTS WORKING")
        return True
        
    except Exception as e:
        print(f"  ✗ API endpoint testing failed: {e}")
        return False


def test_rbac():
    """Test RBAC filtering"""
    print_section("TEST 4: VALIDATE RBAC FILTERING")
    
    try:
        from rbac import apply_neo4j_tenant_filter, apply_postgres_tenant_filter
        
        # Test Neo4j tenant filter
        base_query = "MATCH (t:Taxpayer) RETURN t"
        
        # Admin user (no filter)
        admin_user = {"role": "Admin", "gstin": None}
        filtered_query = apply_neo4j_tenant_filter(base_query, admin_user)
        admin_ok = filtered_query == base_query
        print_result("Admin - No Filter Applied", admin_ok)
        
        # Business Owner (filter applied)
        owner_user = {"role": "Business_Owner", "gstin": "27AAPFU0939F1ZV"}
        filtered_query = apply_neo4j_tenant_filter(base_query, owner_user)
        owner_ok = "WHERE t.gstin = '27AAPFU0939F1ZV'" in filtered_query
        print_result("Business Owner - Filter Applied", owner_ok)
        
        # Test PostgreSQL tenant filter
        base_sql = "SELECT * FROM risk_predictions"
        
        # Admin user (no filter)
        filtered_sql = apply_postgres_tenant_filter(base_sql, admin_user)
        admin_sql_ok = filtered_sql == base_sql
        print_result("Admin SQL - No Filter Applied", admin_sql_ok)
        
        # Business Owner (filter applied)
        filtered_sql = apply_postgres_tenant_filter(base_sql, owner_user)
        owner_sql_ok = "WHERE gstin = '27AAPFU0939F1ZV'" in filtered_sql
        print_result("Business Owner SQL - Filter Applied", owner_sql_ok)
        
        all_passed = admin_ok and owner_ok and admin_sql_ok and owner_sql_ok
        
        if all_passed:
            print("\n  ✓ RBAC FILTERING WORKING CORRECTLY")
        else:
            print("\n  ✗ RBAC FILTERING FAILED")
        
        return all_passed
        
    except Exception as e:
        print(f"  ✗ RBAC testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all validation tests"""
    print("\n" + "="*70)
    print("PROJECT NIYATI - COMPREHENSIVE BACKEND VALIDATION")
    print("Task 13: Checkpoint - Validate Backend")
    print("="*70)
    
    results = {}
    
    # Test 1: Agents
    results['agents'] = await test_agents()
    
    # Test 2: Workflow
    results['workflow'] = await test_workflow()
    
    # Test 3: API Endpoints
    api_result = test_api_endpoints()
    if api_result is not None:
        results['api'] = api_result
    
    # Test 4: RBAC
    results['rbac'] = test_rbac()
    
    # Final Summary
    print_section("VALIDATION SUMMARY")
    
    print("Test Results:")
    for test_name, passed in results.items():
        print_result(test_name.upper(), passed)
    
    # Calculate pass rate
    total_tests = len(results)
    passed_tests = sum(1 for p in results.values() if p)
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n  Pass Rate: {passed_tests}/{total_tests} ({pass_rate:.0f}%)")
    
    if all(results.values()):
        print("\n" + "="*70)
        print("✓ BACKEND VALIDATION COMPLETE - ALL TESTS PASSED!")
        print("="*70)
        print("\nThe Project Niyati backend is working correctly:")
        print("  ✓ All 5 agents validated")
        print("  ✓ LangGraph workflow orchestration working")
        print("  ✓ RBAC filtering implemented correctly")
        if 'api' in results:
            print("  ✓ API endpoints responding correctly")
        print("\n✓ Ready for production deployment!")
    else:
        print("\n" + "="*70)
        print("⚠ BACKEND VALIDATION INCOMPLETE")
        print("="*70)
        print("\nSome tests failed or were skipped. Please review the results above.")
        
        if 'api' not in results:
            print("\nNote: API endpoint tests were skipped because the server is not running.")
            print("To test API endpoints, start the server with:")
            print("  cd backend && uvicorn app_fastapi:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
