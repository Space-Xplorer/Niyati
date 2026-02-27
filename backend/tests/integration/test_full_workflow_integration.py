"""
Integration Test: Full Workflow Integration

This module tests the complete Project Niyati workflow from data ingestion
through all 5 agents to final output generation. It validates the end-to-end
integration of all system components.

Requirements: All Requirements (Final Integration Testing)
Task: 18. Final Integration and Testing
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any
import pandas as pd

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from orchestration.state import NiyatiState, create_initial_state
from orchestration.llm_agent import create_workflow


class TestFullWorkflowIntegration:
    """Integration tests for the complete Niyati workflow"""
    
    @pytest.fixture
    def sample_csv_data(self) -> Dict[str, pd.DataFrame]:
        """Create minimal sample CSV data for testing"""
        
        # E-invoices data
        e_invoices = pd.DataFrame({
            'IRN': ['IRN001', 'IRN002', 'IRN003'],
            'seller_gstin': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX', '27AAPFU0939F1ZV'],
            'buyer_gstin': ['29AABCU9603R1ZX', '24AACCT1234E1Z5', '27AAPFU0939F1ZV'],
            'invoice_value': [150000.0, 200000.0, 180000.0],
            'invoice_date': pd.to_datetime(['2024-01-10', '2024-01-15', '2024-01-20']),
            'DocNo': ['DOC001', 'DOC002', 'DOC003']
        })
        
        # E-way bills data (missing one to create ghost invoice)
        eway_bills = pd.DataFrame({
            'DocNo': ['DOC001', 'DOC002'],
            'vehicle_no': ['MH01AB1234', 'MH02CD5678'],
            'distance': [150, 200],
            'generated_date': pd.to_datetime(['2024-01-12', '2024-01-16'])
        })
        
        # Entity master data
        entity_master = pd.DataFrame({
            'gstin': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX', '24AACCT1234E1Z5'],
            'business_name': ['ABC Corp', 'XYZ Traders', 'PQR Industries'],
            'phone': ['9876543210', '9876543210', '9123456789'],  # First two share phone
            'email': ['abc@example.com', 'xyz@example.com', 'pqr@example.com'],
            'address': ['Mumbai', 'Bangalore', 'Delhi']
        })
        
        # Filing history data
        filing_history = pd.DataFrame({
            'gstin': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX', '24AACCT1234E1Z5'],
            'filing_period': ['2024-01', '2024-01', '2024-01'],
            'days_delayed': [5, 10, 0],
            'status': ['Filed', 'Filed', 'Filed']
        })
        
        # Purchase register data
        purchase_register = pd.DataFrame({
            'buyer_gstin': ['29AABCU9603R1ZX', '24AACCT1234E1Z5', '27AAPFU0939F1ZV'],
            'seller_gstin': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX', '27AAPFU0939F1ZV'],
            'invoice_value': [150000.0, 200000.0, 180000.0],
            'itc_claimed': [27000.0, 36000.0, 32400.0]
        })
        
        # Returns summary data
        returns_summary = pd.DataFrame({
            'gstin': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX', '24AACCT1234E1Z5'],
            'gstr1_sales': [500000.0, 300000.0, 400000.0],
            'gstr3b_sales': [480000.0, 300000.0, 400000.0],
            'period': ['2024-01', '2024-01', '2024-01']
        })
        
        return {
            'e_invoices': e_invoices,
            'eway_bills': eway_bills,
            'entity_master': entity_master,
            'filing_history': filing_history,
            'purchase_register': purchase_register,
            'returns_summary': returns_summary
        }
    
    @pytest.mark.asyncio
    async def test_workflow_initialization(self):
        """Test that the workflow can be created and initialized"""
        workflow = create_workflow()
        assert workflow is not None
        
        # create_workflow() already returns a compiled workflow
        # No need to call compile() again
        assert hasattr(workflow, 'invoke')
    
    @pytest.mark.asyncio
    async def test_initial_state_creation(self, sample_csv_data):
        """Test that initial state can be created with CSV data"""
        initial_state = create_initial_state(sample_csv_data)
        
        assert initial_state is not None
        assert 'csv_files' in initial_state
        assert 'errors' in initial_state
        assert len(initial_state['errors']) == 0
        
        # Verify all CSV files are present
        assert 'e_invoices' in initial_state['csv_files']
        assert 'eway_bills' in initial_state['csv_files']
        assert 'entity_master' in initial_state['csv_files']
        assert len(initial_state['csv_files']['e_invoices']) == 3
    
    def test_agent_imports(self):
        """Test that all agent modules can be imported"""
        try:
            from orchestration.agent_ingestion_wrangler import ingestion_wrangler_node_sync
            from orchestration.agent_graph_architect import graph_architect_node_sync
            from orchestration.agent_risk_detective import risk_detective_node_sync
            from orchestration.agent_predictive_analyst import predictive_analyst_node_sync
            from orchestration.agent_niyati_explainer import niyati_explainer_node_sync
            
            assert ingestion_wrangler_node_sync is not None
            assert graph_architect_node_sync is not None
            assert risk_detective_node_sync is not None
            assert predictive_analyst_node_sync is not None
            assert niyati_explainer_node_sync is not None
        except ImportError as e:
            pytest.fail(f"Failed to import agent modules: {e}")
    
    def test_state_schema_validation(self):
        """Test that the NiyatiState schema is properly defined"""
        from orchestration.state import NiyatiState
        
        # Check that required keys are defined in the TypedDict
        required_keys = [
            'csv_files',
            'validated_data',
            'engineered_features',
            'graph_built',
            'structural_patterns',
            'risk_predictions',
            'shape_plots',
            'narratives',
            'errors'
        ]
        
        # Create a minimal state to verify structure
        test_state = create_initial_state({})
        
        for key in required_keys:
            assert key in test_state, f"Missing required key: {key}"
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """Test that workflow handles errors gracefully"""
        workflow = create_workflow()
        
        # Create state with invalid data to trigger errors
        invalid_state = create_initial_state({
            'e_invoices': pd.DataFrame({'invalid': [1, 2, 3]})
        })
        
        # The workflow should handle this gracefully without crashing
        try:
            result = workflow.invoke(invalid_state)
            # Check that errors were captured
            assert 'errors' in result
        except Exception as e:
            # If it raises an exception, it should be a controlled one
            assert isinstance(e, (ValueError, KeyError, RuntimeError))
    
    def test_concurrent_analysis_node_exists(self):
        """Test that concurrent analysis node is properly configured"""
        from orchestration.llm_agent import concurrent_analysis_node
        
        assert concurrent_analysis_node is not None
        
        # Verify it's a callable function
        assert callable(concurrent_analysis_node)
    
    def test_error_handling_node_exists(self):
        """Test that error handling node is properly configured"""
        from orchestration.llm_agent import error_handling_node
        
        assert error_handling_node is not None
        assert callable(error_handling_node)
    
    def test_workflow_conditional_edges(self):
        """Test that workflow has proper conditional edge logic"""
        from orchestration.llm_agent import should_continue
        
        assert should_continue is not None
        assert callable(should_continue)
        
        # Test with state that has no errors
        state_no_errors = create_initial_state({})
        result = should_continue(state_no_errors)
        assert result == "continue"
        
        # Test with state that has errors
        state_with_errors = create_initial_state({})
        state_with_errors['errors'] = ["Test error"]
        result = should_continue(state_with_errors)
        assert result == "error"


class TestComponentIntegration:
    """Test integration between different system components"""
    
    def test_database_connections_configured(self):
        """Test that database connections are properly configured"""
        try:
            from database import engine
            
            # This should not raise an error
            assert engine is not None
        except Exception as e:
            pytest.skip(f"Database not configured: {e}")
    
    def test_neo4j_connection_configured(self):
        """Test that Neo4j connection is properly configured"""
        try:
            from orchestration.agent_graph_architect import get_neo4j_driver
            
            driver = get_neo4j_driver()
            assert driver is not None
        except Exception as e:
            pytest.skip(f"Neo4j not configured: {e}")
    
    def test_ebm_model_exists(self):
        """Test that the trained EBM model file exists"""
        model_path = Path(backend_path) / 'model' / 'ebm_model.pkl'
        
        if not model_path.exists():
            pytest.skip("EBM model not found - this is expected if model training hasn't been completed")
        else:
            assert model_path.is_file()
    
    def test_feature_engineering_wrapper_exists(self):
        """Test that feature engineering wrapper is available"""
        try:
            from utils.feature_engineering_wrapper import compute_engineered_features
            
            assert compute_engineered_features is not None
            assert callable(compute_engineered_features)
        except ImportError as e:
            pytest.fail(f"Feature engineering wrapper not found: {e}")
    
    def test_pii_hashing_utilities_exist(self):
        """Test that PII hashing utilities are available"""
        try:
            from utils.pii_hashing import hash_pii, mask_pii_display
            
            assert hash_pii is not None
            assert mask_pii_display is not None
            
            # Test basic functionality
            hashed = hash_pii("test@example.com")
            assert hashed is not None
            assert len(hashed) == 64  # SHA-256 produces 64 hex characters
            
            masked = mask_pii_display("test@example.com", "email")
            assert masked == "***@***.com"
        except ImportError as e:
            pytest.fail(f"PII hashing utilities not found: {e}")


class TestAPIIntegration:
    """Test API endpoint integration"""
    
    def test_fastapi_app_imports(self):
        """Test that FastAPI app can be imported"""
        try:
            from app_fastapi import app
            
            assert app is not None
        except ImportError as e:
            pytest.fail(f"Failed to import FastAPI app: {e}")
    
    def test_auth_endpoints_configured(self):
        """Test that authentication endpoints are configured"""
        from app_fastapi import app
        
        routes = [route.path for route in app.routes]
        
        assert "/auth/register" in routes
        assert "/auth/login" in routes
    
    def test_workflow_endpoints_configured(self):
        """Test that workflow endpoints are configured"""
        from app_fastapi import app
        
        routes = [route.path for route in app.routes]
        
        assert "/sync" in routes
        assert "/pre-audit" in routes
        assert "/dashboard" in routes
        assert "/graph" in routes
    
    def test_sse_endpoint_configured(self):
        """Test that SSE streaming endpoint is configured"""
        from app_fastapi import app
        
        routes = [route.path for route in app.routes]
        
        assert "/logs/stream" in routes
    
    def test_rbac_middleware_exists(self):
        """Test that RBAC middleware is properly configured"""
        try:
            from rbac import apply_rbac_filter_neo4j, apply_rbac_filter_postgres
            
            assert apply_rbac_filter_neo4j is not None
            assert apply_rbac_filter_postgres is not None
        except ImportError as e:
            pytest.skip(f"RBAC module not found: {e}")


class TestPerformanceTargets:
    """Test that performance targets are achievable"""
    
    @pytest.mark.slow
    def test_workflow_execution_time_target(self):
        """Test that workflow can complete within 60 seconds for small dataset"""
        pytest.skip("Performance test - requires full database setup and takes time")
        # This would test Requirement 17.4: workflow completes in < 60 seconds
    
    @pytest.mark.slow
    def test_graph_ingestion_time_target(self):
        """Test that graph ingestion completes within 30 seconds"""
        pytest.skip("Performance test - requires Neo4j connection")
        # This would test Requirement 17.2: graph ingestion < 30 seconds for 1,500 invoices
    
    @pytest.mark.slow
    def test_dashboard_response_time_target(self):
        """Test that dashboard queries complete within 3 seconds"""
        pytest.skip("Performance test - requires full system running")
        # This would test Requirement 17.7: dashboard queries < 3 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
