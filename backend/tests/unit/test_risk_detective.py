"""
Unit Tests for Agent 3: Risk Detective

This module tests the Risk Detective agent's ability to detect fraud patterns
in the Neo4j knowledge graph, including circular trade, ghost invoices, and spider webs.

Requirements: 4.1-4.7
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import asyncio

from orchestration.state import NiyatiState, create_initial_state
from orchestration.agent_risk_detective import (
    risk_detective_node,
    _detect_circular_trade,
    _detect_ghost_invoices,
    _detect_spider_webs,
    _compute_circular_trade_risk_score,
    _compute_ghost_invoice_risk_score,
    _compute_spider_web_risk_score
)


@pytest.fixture
def graph_built_state():
    """Create a state with graph_built=True for testing."""
    state = create_initial_state({})
    state['graph_built'] = True
    return state


@pytest.fixture
def mock_neo4j_session():
    """Create a mock Neo4j session."""
    session = MagicMock()
    return session


class TestCircularTradeDetection:
    """Test circular trade pattern detection (Requirements 4.1, 4.2)."""
    
    def test_detect_circular_trade_basic(self, mock_neo4j_session):
        """Test detection of a basic 3-hop circular trade pattern."""
        # Mock Neo4j query result for circular trade
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([
            {
                'gstin_a': '27AAPFU0939F1ZV',
                'name_a': 'ABC Corp',
                'gstin_b': '29AABCU9603R1ZX',
                'name_b': 'XYZ Ltd',
                'gstin_c': '24AACDE1234F1Z5',
                'name_c': 'DEF Inc',
                'total_value': 450000.0,
                'loop_length': 3,
                'invoice_irns': ['IRN001', 'IRN002', 'IRN003']
            }
        ]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        # Run detection
        patterns = _detect_circular_trade(mock_neo4j_session)
        
        # Verify results
        assert len(patterns) == 1
        pattern = patterns[0]
        
        assert pattern['pattern_type'] == 'circular_trade'
        assert len(pattern['gstin_list']) == 3
        assert '27AAPFU0939F1ZV' in pattern['gstin_list']
        assert '29AABCU9603R1ZX' in pattern['gstin_list']
        assert '24AACDE1234F1Z5' in pattern['gstin_list']
        assert pattern['loop_length'] == 3
        assert pattern['total_value'] == 450000.0
        assert len(pattern['invoice_irns']) == 3
    
    def test_detect_circular_trade_multiple_loops(self, mock_neo4j_session):
        """Test detection of multiple circular trade patterns."""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([
            {
                'gstin_a': '27AAPFU0939F1ZV',
                'name_a': 'ABC Corp',
                'gstin_b': '29AABCU9603R1ZX',
                'name_b': 'XYZ Ltd',
                'gstin_c': '24AACDE1234F1Z5',
                'name_c': 'DEF Inc',
                'total_value': 450000.0,
                'loop_length': 3,
                'invoice_irns': ['IRN001', 'IRN002', 'IRN003']
            },
            {
                'gstin_a': '11AAAAA1111A1AA',
                'name_a': 'Company A',
                'gstin_b': '22BBBBB2222B2BB',
                'name_b': 'Company B',
                'gstin_c': '33CCCCC3333C3CC',
                'name_c': 'Company C',
                'total_value': 600000.0,
                'loop_length': 3,
                'invoice_irns': ['IRN004', 'IRN005', 'IRN006']
            }
        ]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        patterns = _detect_circular_trade(mock_neo4j_session)
        
        assert len(patterns) == 2
        assert patterns[0]['total_value'] == 450000.0
        assert patterns[1]['total_value'] == 600000.0
    
    def test_detect_circular_trade_no_patterns(self, mock_neo4j_session):
        """Test when no circular trade patterns exist."""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        patterns = _detect_circular_trade(mock_neo4j_session)
        
        assert len(patterns) == 0
    
    def test_detect_circular_trade_entity_names(self, mock_neo4j_session):
        """Test that entity names are included in pattern (Requirement 6.2)."""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([
            {
                'gstin_a': '27AAPFU0939F1ZV',
                'name_a': 'ABC Corp',
                'gstin_b': '29AABCU9603R1ZX',
                'name_b': 'XYZ Ltd',
                'gstin_c': '24AACDE1234F1Z5',
                'name_c': 'DEF Inc',
                'total_value': 450000.0,
                'loop_length': 3,
                'invoice_irns': ['IRN001', 'IRN002', 'IRN003']
            }
        ]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        patterns = _detect_circular_trade(mock_neo4j_session)
        
        assert 'entity_names' in patterns[0]
        assert len(patterns[0]['entity_names']) == 3
        assert 'ABC Corp' in patterns[0]['entity_names']
        assert 'XYZ Ltd' in patterns[0]['entity_names']
        assert 'DEF Inc' in patterns[0]['entity_names']


class TestGhostInvoiceDetection:
    """Test ghost invoice pattern detection (Requirements 4.3, 4.4)."""
    
    def test_detect_ghost_invoices_basic(self, mock_neo4j_session):
        """Test detection of ghost invoices (high-value without eway bills)."""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([
            {
                'seller_gstin': '27AAPFU0939F1ZV',
                'seller_name': 'ABC Corp',
                'ghost_count': 5,
                'ghost_value': 750000.0,
                'ghost_irns': ['IRN001', 'IRN002', 'IRN003', 'IRN004', 'IRN005']
            }
        ]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        patterns = _detect_ghost_invoices(mock_neo4j_session)
        
        assert len(patterns) == 1
        pattern = patterns[0]
        
        assert pattern['pattern_type'] == 'ghost_invoice'
        assert pattern['seller_gstin'] == '27AAPFU0939F1ZV'
        assert pattern['seller_name'] == 'ABC Corp'
        assert pattern['ghost_count'] == 5
        assert pattern['ghost_value'] == 750000.0
        assert len(pattern['ghost_irns']) == 5
    
    def test_detect_ghost_invoices_threshold(self, mock_neo4j_session):
        """Test that threshold parameter is used correctly."""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        # Call with custom threshold
        patterns = _detect_ghost_invoices(mock_neo4j_session, threshold=200000.0)
        
        # Verify the function was called (threshold is used in the query)
        assert mock_neo4j_session.run.called
        # Verify empty result is handled correctly
        assert len(patterns) == 0
    
    def test_detect_ghost_invoices_multiple_sellers(self, mock_neo4j_session):
        """Test detection across multiple sellers."""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([
            {
                'seller_gstin': '27AAPFU0939F1ZV',
                'seller_name': 'ABC Corp',
                'ghost_count': 5,
                'ghost_value': 750000.0,
                'ghost_irns': ['IRN001', 'IRN002', 'IRN003', 'IRN004', 'IRN005']
            },
            {
                'seller_gstin': '29AABCU9603R1ZX',
                'seller_name': 'XYZ Ltd',
                'ghost_count': 3,
                'ghost_value': 450000.0,
                'ghost_irns': ['IRN006', 'IRN007', 'IRN008']
            }
        ]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        patterns = _detect_ghost_invoices(mock_neo4j_session)
        
        assert len(patterns) == 2
        assert patterns[0]['ghost_count'] == 5
        assert patterns[1]['ghost_count'] == 3
    
    def test_detect_ghost_invoices_aggregation(self, mock_neo4j_session):
        """Test that ghost invoices are aggregated by seller_gstin (Requirement 4.4)."""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([
            {
                'seller_gstin': '27AAPFU0939F1ZV',
                'seller_name': 'ABC Corp',
                'ghost_count': 12,
                'ghost_value': 1500000.0,
                'ghost_irns': [f'IRN{i:03d}' for i in range(12)]
            }
        ]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        patterns = _detect_ghost_invoices(mock_neo4j_session)
        
        # Verify aggregation
        assert patterns[0]['gstin_list'] == ['27AAPFU0939F1ZV']
        assert patterns[0]['ghost_count'] == 12
        assert patterns[0]['ghost_value'] == 1500000.0


class TestSpiderWebDetection:
    """Test spider web network detection (Requirements 4.5, 4.6)."""
    
    def test_detect_spider_webs_basic(self, mock_neo4j_session):
        """Test detection of spider web networks via shared contacts."""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([
            {
                'anchor_gstin': '27AAPFU0939F1ZV',
                'anchor_name': 'ABC Corp',
                'cluster_gstins': ['29AABCU9603R1ZX', '24AACDE1234F1Z5'],
                'cluster_names': ['XYZ Ltd', 'DEF Inc'],
                'cluster_size': 3,
                'transaction_volume': 2500000.0
            }
        ]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        patterns = _detect_spider_webs(mock_neo4j_session)
        
        assert len(patterns) == 1
        pattern = patterns[0]
        
        assert pattern['pattern_type'] == 'spider_web'
        assert len(pattern['gstin_list']) == 3
        assert '27AAPFU0939F1ZV' in pattern['gstin_list']
        assert '29AABCU9603R1ZX' in pattern['gstin_list']
        assert '24AACDE1234F1Z5' in pattern['gstin_list']
        assert pattern['cluster_size'] == 3
        assert pattern['transaction_volume'] == 2500000.0
    
    def test_detect_spider_webs_min_cluster_size(self, mock_neo4j_session):
        """Test that min_cluster_size parameter is used correctly."""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        # Call with custom min_cluster_size
        patterns = _detect_spider_webs(mock_neo4j_session, min_cluster_size=5)
        
        # Verify the function was called (min_cluster_size is used in the query)
        assert mock_neo4j_session.run.called
        # Verify empty result is handled correctly
        assert len(patterns) == 0
    
    def test_detect_spider_webs_deduplication(self, mock_neo4j_session):
        """Test that duplicate clusters are removed."""
        # Simulate Neo4j returning the same cluster from different anchor points
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([
            {
                'anchor_gstin': '27AAPFU0939F1ZV',
                'anchor_name': 'ABC Corp',
                'cluster_gstins': ['29AABCU9603R1ZX', '24AACDE1234F1Z5'],
                'cluster_names': ['XYZ Ltd', 'DEF Inc'],
                'cluster_size': 3,
                'transaction_volume': 2500000.0
            },
            {
                'anchor_gstin': '29AABCU9603R1ZX',
                'anchor_name': 'XYZ Ltd',
                'cluster_gstins': ['27AAPFU0939F1ZV', '24AACDE1234F1Z5'],
                'cluster_names': ['ABC Corp', 'DEF Inc'],
                'cluster_size': 3,
                'transaction_volume': 2500000.0
            }
        ]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        patterns = _detect_spider_webs(mock_neo4j_session)
        
        # Should only return 1 pattern (duplicates removed)
        assert len(patterns) == 1
    
    def test_detect_spider_webs_entity_names(self, mock_neo4j_session):
        """Test that entity names are included (Requirement 6.4)."""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([
            {
                'anchor_gstin': '27AAPFU0939F1ZV',
                'anchor_name': 'ABC Corp',
                'cluster_gstins': ['29AABCU9603R1ZX', '24AACDE1234F1Z5'],
                'cluster_names': ['XYZ Ltd', 'DEF Inc'],
                'cluster_size': 3,
                'transaction_volume': 2500000.0
            }
        ]))
        
        mock_neo4j_session.run.return_value = mock_result
        
        patterns = _detect_spider_webs(mock_neo4j_session)
        
        assert 'entity_names' in patterns[0]
        assert len(patterns[0]['entity_names']) == 3
        assert 'ABC Corp' in patterns[0]['entity_names']
        assert 'XYZ Ltd' in patterns[0]['entity_names']
        assert 'DEF Inc' in patterns[0]['entity_names']


class TestRiskScoreComputation:
    """Test risk score computation functions."""
    
    def test_compute_circular_trade_risk_score_baseline(self):
        """Test circular trade risk score computation with baseline values."""
        # 3-hop loop with 100k value (baseline)
        score = _compute_circular_trade_risk_score(3, 100000.0)
        
        # Should be 1.0 (loop_factor=1.0, value_factor=1.0)
        assert score == 1.0
    
    def test_compute_circular_trade_risk_score_high_value(self):
        """Test circular trade risk score with high transaction value."""
        # 3-hop loop with 500k value (5x baseline)
        score = _compute_circular_trade_risk_score(3, 500000.0)
        
        # Should be higher due to high value
        assert score > 0.8
    
    def test_compute_circular_trade_risk_score_bounds(self):
        """Test that risk score is bounded between 0 and 1."""
        # Very high values
        score = _compute_circular_trade_risk_score(10, 10000000.0)
        assert 0.0 <= score <= 1.0
    
    def test_compute_ghost_invoice_risk_score_baseline(self):
        """Test ghost invoice risk score computation with baseline values."""
        # 10 invoices with 1M value (baseline)
        score = _compute_ghost_invoice_risk_score(10, 1000000.0)
        
        # Should be 1.0 (count_factor=1.0, value_factor=1.0)
        assert score == 1.0
    
    def test_compute_ghost_invoice_risk_score_high_count(self):
        """Test ghost invoice risk score with high count."""
        # 50 invoices with 5M value
        score = _compute_ghost_invoice_risk_score(50, 5000000.0)
        
        # Should be very high
        assert score >= 0.9
    
    def test_compute_ghost_invoice_risk_score_bounds(self):
        """Test that risk score is bounded between 0 and 1."""
        score = _compute_ghost_invoice_risk_score(100, 10000000.0)
        assert 0.0 <= score <= 1.0
    
    def test_compute_spider_web_risk_score_baseline(self):
        """Test spider web risk score computation with baseline values."""
        # 5 entities with 5M volume (baseline)
        score = _compute_spider_web_risk_score(5, 5000000.0)
        
        # Should be 1.0 (size_factor=1.0, volume_factor=1.0)
        assert score == 1.0
    
    def test_compute_spider_web_risk_score_large_cluster(self):
        """Test spider web risk score with large cluster."""
        # 20 entities with 20M volume
        score = _compute_spider_web_risk_score(20, 20000000.0)
        
        # Should be very high
        assert score >= 0.9
    
    def test_compute_spider_web_risk_score_bounds(self):
        """Test that risk score is bounded between 0 and 1."""
        score = _compute_spider_web_risk_score(100, 100000000.0)
        assert 0.0 <= score <= 1.0


class TestRiskDetectiveNode:
    """Test the complete Risk Detective node."""
    
    @pytest.mark.asyncio
    async def test_risk_detective_node_success(self, graph_built_state):
        """Test successful pattern detection."""
        with patch('orchestration.agent_risk_detective.get_neo4j_driver') as mock_driver:
            # Mock Neo4j driver and session
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
            
            # Mock circular trade results
            circular_result = MagicMock()
            circular_result.__iter__ = Mock(return_value=iter([
                {
                    'gstin_a': '27AAPFU0939F1ZV',
                    'name_a': 'ABC Corp',
                    'gstin_b': '29AABCU9603R1ZX',
                    'name_b': 'XYZ Ltd',
                    'gstin_c': '24AACDE1234F1Z5',
                    'name_c': 'DEF Inc',
                    'total_value': 450000.0,
                    'loop_length': 3,
                    'invoice_irns': ['IRN001', 'IRN002', 'IRN003']
                }
            ]))
            
            # Mock ghost invoice results
            ghost_result = MagicMock()
            ghost_result.__iter__ = Mock(return_value=iter([
                {
                    'seller_gstin': '27AAPFU0939F1ZV',
                    'seller_name': 'ABC Corp',
                    'ghost_count': 5,
                    'ghost_value': 750000.0,
                    'ghost_irns': ['IRN004', 'IRN005', 'IRN006', 'IRN007', 'IRN008']
                }
            ]))
            
            # Mock spider web results
            spider_result = MagicMock()
            spider_result.__iter__ = Mock(return_value=iter([
                {
                    'anchor_gstin': '27AAPFU0939F1ZV',
                    'anchor_name': 'ABC Corp',
                    'cluster_gstins': ['29AABCU9603R1ZX'],
                    'cluster_names': ['XYZ Ltd'],
                    'cluster_size': 2,
                    'transaction_volume': 1000000.0
                }
            ]))
            
            # Configure mock to return different results for different queries
            mock_session.run.side_effect = [circular_result, ghost_result, spider_result]
            
            # Run the agent
            result_state = await risk_detective_node(graph_built_state)
            
            # Verify state was updated
            assert len(result_state['structural_patterns']) == 3
            assert len(result_state['errors']) == 0
            
            # Verify pattern types
            pattern_types = [p['pattern_type'] for p in result_state['structural_patterns']]
            assert 'circular_trade' in pattern_types
            assert 'ghost_invoice' in pattern_types
            assert 'spider_web' in pattern_types
    
    @pytest.mark.asyncio
    async def test_risk_detective_node_requires_graph_built(self):
        """Test that node requires graph_built=True."""
        state = create_initial_state({})
        state['graph_built'] = False
        
        result_state = await risk_detective_node(state)
        
        # Should have error
        assert len(result_state['errors']) > 0
        assert 'graph_built=True' in result_state['errors'][0]
        assert len(result_state['structural_patterns']) == 0
    
    @pytest.mark.asyncio
    async def test_risk_detective_node_error_handling(self, graph_built_state):
        """Test error handling when Neo4j connection fails."""
        with patch('orchestration.agent_risk_detective.get_neo4j_driver') as mock_driver:
            # Simulate connection failure
            mock_driver.side_effect = Exception("Connection failed")
            
            result_state = await risk_detective_node(graph_built_state)
            
            # Verify error was captured
            assert len(result_state['errors']) > 0
            assert "Agent 3 failed" in result_state['errors'][0]
    
    @pytest.mark.asyncio
    async def test_risk_detective_node_sse_broadcasting(self, graph_built_state):
        """Test that SSE messages are broadcast (Requirement 19.5)."""
        with patch('orchestration.agent_risk_detective.get_neo4j_driver') as mock_driver:
            with patch('orchestration.agent_risk_detective.broadcast_event') as mock_broadcast:
                # Mock Neo4j
                mock_session = MagicMock()
                mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
                
                # Mock empty results
                empty_result = MagicMock()
                empty_result.__iter__ = Mock(return_value=iter([]))
                mock_session.run.return_value = empty_result
                
                # Run the agent
                await risk_detective_node(graph_built_state)
                
                # Verify SSE messages were broadcast
                assert mock_broadcast.call_count >= 4
                
                # Check for specific messages
                broadcast_messages = [call[0][0] for call in mock_broadcast.call_args_list]
                assert any('Connecting to Neo4j' in msg for msg in broadcast_messages)
                assert any('circular trading paths' in msg for msg in broadcast_messages)
                assert any('ghost invoices' in msg for msg in broadcast_messages)
                assert any('spider web' in msg for msg in broadcast_messages)
    
    @pytest.mark.asyncio
    async def test_risk_detective_node_no_patterns(self, graph_built_state):
        """Test when no patterns are detected."""
        with patch('orchestration.agent_risk_detective.get_neo4j_driver') as mock_driver:
            # Mock Neo4j with empty results
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
            
            empty_result = MagicMock()
            empty_result.__iter__ = Mock(return_value=iter([]))
            mock_session.run.return_value = empty_result
            
            result_state = await risk_detective_node(graph_built_state)
            
            # Should complete successfully with no patterns
            assert len(result_state['structural_patterns']) == 0
            assert len(result_state['errors']) == 0
    
    @pytest.mark.asyncio
    async def test_risk_detective_node_pattern_persistence(self, graph_built_state):
        """Test that patterns include all required fields for persistence (Requirement 4.7)."""
        with patch('orchestration.agent_risk_detective.get_neo4j_driver') as mock_driver:
            mock_session = MagicMock()
            mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
            
            # Mock circular trade result
            circular_result = MagicMock()
            circular_result.__iter__ = Mock(return_value=iter([
                {
                    'gstin_a': '27AAPFU0939F1ZV',
                    'name_a': 'ABC Corp',
                    'gstin_b': '29AABCU9603R1ZX',
                    'name_b': 'XYZ Ltd',
                    'gstin_c': '24AACDE1234F1Z5',
                    'name_c': 'DEF Inc',
                    'total_value': 450000.0,
                    'loop_length': 3,
                    'invoice_irns': ['IRN001', 'IRN002', 'IRN003']
                }
            ]))
            
            empty_result = MagicMock()
            empty_result.__iter__ = Mock(return_value=iter([]))
            
            mock_session.run.side_effect = [circular_result, empty_result, empty_result]
            
            result_state = await risk_detective_node(graph_built_state)
            
            # Verify pattern has required fields for persistence
            pattern = result_state['structural_patterns'][0]
            assert 'pattern_type' in pattern
            assert 'gstin_list' in pattern
            assert 'risk_score' in pattern
            assert isinstance(pattern['gstin_list'], list)
            assert isinstance(pattern['risk_score'], float)
            assert 0.0 <= pattern['risk_score'] <= 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
