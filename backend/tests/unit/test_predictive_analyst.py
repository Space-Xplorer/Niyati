"""
Unit Tests for Agent 4: Predictive Analyst

This module tests the Predictive Analyst agent's ability to:
- Load the trained EBM model
- Run inference on engineered features
- Extract top 3 feature contributions
- Extract shape plot data for visualization
- Classify risk levels (HIGH_RISK, MEDIUM_RISK, LOW_RISK)
- Broadcast SSE messages

Requirements: 5.1-5.8, 20.1-20.3, 19.6
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pandas as pd
import numpy as np

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from orchestration.state import NiyatiState, create_initial_state
from orchestration.agent_predictive_analyst import (
    predictive_analyst_node,
    load_ebm_model,
    classify_risk_level,
    extract_top_drivers,
    extract_shape_plot_data,
    set_event_queue
)


@pytest.fixture
def mock_event_queue():
    """Create a mock event queue for SSE testing."""
    queue = asyncio.Queue()
    set_event_queue(queue)
    return queue


@pytest.fixture
def mock_engineered_features():
    """Create mock engineered features DataFrame for testing."""
    return pd.DataFrame({
        'Gstin': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX', '24AACDE1234F1Z5'],
        'payment_gap': [10.5, 5.2, 15.8],
        'payment_gap_pct': [0.105, 0.052, 0.158],
        'ghost_invoice_pct': [34.5, 12.3, 45.6],
        'shared_contact_flag': [1, 0, 1],
        'filing_gap': [50000.0, 10000.0, 75000.0],
        'excess_itc_flag': [1, 0, 1],
        'avg_invoice_value': [150000.0, 200000.0, 180000.0],
        'transaction_count': [25, 30, 20],
        'filing_delay_avg': [5.5, 2.3, 8.7],
        'circular_trade_involvement': [2, 0, 1],
        'spider_web_involvement': [1, 0, 1],
        'vendor_diversity': [0.65, 0.85, 0.55],
        'buyer_concentration': [0.45, 0.25, 0.55],
        'seasonal_anomaly_score': [0.78, 0.32, 0.89]
    })


@pytest.fixture
def state_with_features(mock_engineered_features):
    """Create a state with engineered features for testing."""
    state = create_initial_state({})
    state['engineered_features'] = mock_engineered_features
    return state


@pytest.fixture
def mock_ebm_model():
    """Create a mock EBM model for testing."""
    model = MagicMock()
    
    # Mock predict_proba to return probabilities between 0 and 1
    model.predict_proba.return_value = np.array([
        [0.1, 0.9],   # HIGH_RISK (0.9)
        [0.7, 0.3],   # LOW_RISK (0.3)
        [0.4, 0.6]    # MEDIUM_RISK (0.6)
    ])
    
    # Mock explain_local for feature contributions
    mock_local_explanation = MagicMock()
    mock_local_explanation.data.return_value = {
        'scores': [0.34, 0.28, 0.19, 0.10, 0.05, 0.03, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'names': [
            'ghost_invoice_pct', 'payment_gap_pct', 'shared_contact_flag',
            'filing_gap', 'excess_itc_flag', 'avg_invoice_value',
            'transaction_count', 'filing_delay_avg', 'circular_trade_involvement',
            'spider_web_involvement', 'vendor_diversity', 'buyer_concentration',
            'seasonal_anomaly_score', 'payment_gap'
        ]
    }
    model.explain_local.return_value = mock_local_explanation
    
    # Mock explain_global for shape plots
    mock_global_explanation = MagicMock()
    
    def mock_global_data(feature_idx):
        return {
            'names': [0, 10, 20, 30, 40, 50],  # Feature value bins
            'scores': [0, 0.05, 0.12, 0.25, 0.42, 0.65]  # Contribution scores
        }
    
    mock_global_explanation.data = mock_global_data
    model.explain_global.return_value = mock_global_explanation
    
    # Mock intercept
    model.intercept_ = np.array([0.5])
    
    return model


class TestLoadEBMModel:
    """Test EBM model loading (Requirements 5.1, 5.2)."""
    
    def test_load_ebm_model_success(self):
        """Test successful model loading."""
        with patch('orchestration.agent_predictive_analyst.joblib.load') as mock_load:
            with patch('orchestration.agent_predictive_analyst.os.path.exists', return_value=True):
                mock_model = MagicMock()
                mock_load.return_value = mock_model
                
                # Clear cache first
                import orchestration.agent_predictive_analyst as module
                module._model_cache = None
                
                model = load_ebm_model()
                
                assert model is not None
                assert mock_load.called
    
    def test_load_ebm_model_file_not_found(self):
        """Test error when model file doesn't exist."""
        with patch('orchestration.agent_predictive_analyst.os.path.exists', return_value=False):
            # Clear cache
            import orchestration.agent_predictive_analyst as module
            module._model_cache = None
            
            with pytest.raises(FileNotFoundError) as exc_info:
                load_ebm_model()
            
            assert "EBM model not found" in str(exc_info.value)
    
    def test_load_ebm_model_caching(self):
        """Test that model is cached after first load."""
        with patch('orchestration.agent_predictive_analyst.joblib.load') as mock_load:
            with patch('orchestration.agent_predictive_analyst.os.path.exists', return_value=True):
                mock_model = MagicMock()
                mock_load.return_value = mock_model
                
                # Clear cache
                import orchestration.agent_predictive_analyst as module
                module._model_cache = None
                
                # First load
                model1 = load_ebm_model()
                assert mock_load.call_count == 1
                
                # Second load should use cache
                model2 = load_ebm_model()
                assert mock_load.call_count == 1  # Not called again
                assert model1 is model2
    
    def test_load_ebm_model_loading_error(self):
        """Test error handling when model loading fails."""
        with patch('orchestration.agent_predictive_analyst.joblib.load') as mock_load:
            with patch('orchestration.agent_predictive_analyst.os.path.exists', return_value=True):
                mock_load.side_effect = Exception("Corrupted model file")
                
                # Clear cache
                import orchestration.agent_predictive_analyst as module
                module._model_cache = None
                
                with pytest.raises(Exception) as exc_info:
                    load_ebm_model()
                
                assert "Failed to load EBM model" in str(exc_info.value)


class TestClassifyRiskLevel:
    """Test risk level classification (Requirements 5.6, 5.7, 5.8)."""
    
    def test_classify_high_risk(self):
        """Test HIGH_RISK classification for probability >= 0.7."""
        assert classify_risk_level(0.7) == 'HIGH_RISK'
        assert classify_risk_level(0.85) == 'HIGH_RISK'
        assert classify_risk_level(0.99) == 'HIGH_RISK'
        assert classify_risk_level(1.0) == 'HIGH_RISK'
    
    def test_classify_medium_risk(self):
        """Test MEDIUM_RISK classification for 0.4 <= probability < 0.7."""
        assert classify_risk_level(0.4) == 'MEDIUM_RISK'
        assert classify_risk_level(0.5) == 'MEDIUM_RISK'
        assert classify_risk_level(0.65) == 'MEDIUM_RISK'
        assert classify_risk_level(0.69) == 'MEDIUM_RISK'
    
    def test_classify_low_risk(self):
        """Test LOW_RISK classification for probability < 0.4."""
        assert classify_risk_level(0.0) == 'LOW_RISK'
        assert classify_risk_level(0.1) == 'LOW_RISK'
        assert classify_risk_level(0.25) == 'LOW_RISK'
        assert classify_risk_level(0.39) == 'LOW_RISK'
    
    def test_classify_boundary_values(self):
        """Test boundary values for risk classification."""
        # Test exact boundaries
        assert classify_risk_level(0.7) == 'HIGH_RISK'
        assert classify_risk_level(0.4) == 'MEDIUM_RISK'
        
        # Test just below boundaries
        assert classify_risk_level(0.6999) == 'MEDIUM_RISK'
        assert classify_risk_level(0.3999) == 'LOW_RISK'


class TestExtractTopDrivers:
    """Test feature contribution extraction (Requirements 5.4, 5.5)."""
    
    def test_extract_top_drivers_basic(self, mock_ebm_model, mock_engineered_features):
        """Test extraction of top 3 feature contributions."""
        gstin = '27AAPFU0939F1ZV'
        
        top_drivers = extract_top_drivers(
            mock_ebm_model,
            mock_engineered_features,
            gstin,
            top_n=3
        )
        
        # Should return exactly 3 drivers
        assert len(top_drivers) == 3
        
        # Verify structure of each driver
        for driver in top_drivers:
            assert 'feature_name' in driver
            assert 'contribution_value' in driver
            assert 'direction' in driver
            assert isinstance(driver['feature_name'], str)
            assert isinstance(driver['contribution_value'], float)
            assert driver['direction'] in ['positive', 'negative']
    
    def test_extract_top_drivers_sorted_by_magnitude(self, mock_ebm_model, mock_engineered_features):
        """Test that drivers are sorted by absolute contribution value."""
        gstin = '27AAPFU0939F1ZV'
        
        top_drivers = extract_top_drivers(
            mock_ebm_model,
            mock_engineered_features,
            gstin,
            top_n=3
        )
        
        # Verify sorted by absolute value (descending)
        contributions = [abs(d['contribution_value']) for d in top_drivers]
        assert contributions == sorted(contributions, reverse=True)
    
    def test_extract_top_drivers_direction(self, mock_ebm_model, mock_engineered_features):
        """Test that direction is correctly determined (positive/negative)."""
        gstin = '27AAPFU0939F1ZV'
        
        # Mock with both positive and negative contributions
        mock_local_explanation = MagicMock()
        mock_local_explanation.data.return_value = {
            'scores': [0.34, -0.28, 0.19],
            'names': ['ghost_invoice_pct', 'payment_gap_pct', 'shared_contact_flag']
        }
        mock_ebm_model.explain_local.return_value = mock_local_explanation
        
        top_drivers = extract_top_drivers(
            mock_ebm_model,
            mock_engineered_features,
            gstin,
            top_n=3
        )
        
        # Verify directions
        assert top_drivers[0]['direction'] == 'positive'  # 0.34
        assert top_drivers[1]['direction'] == 'negative'  # -0.28
        assert top_drivers[2]['direction'] == 'positive'  # 0.19
    
    def test_extract_top_drivers_nonexistent_gstin(self, mock_ebm_model, mock_engineered_features):
        """Test handling of nonexistent GSTIN."""
        gstin = 'NONEXISTENT_GSTIN'
        
        top_drivers = extract_top_drivers(
            mock_ebm_model,
            mock_engineered_features,
            gstin,
            top_n=3
        )
        
        # Should return empty list
        assert len(top_drivers) == 0
    
    def test_extract_top_drivers_custom_top_n(self, mock_ebm_model, mock_engineered_features):
        """Test extraction with custom top_n parameter."""
        gstin = '27AAPFU0939F1ZV'
        
        # Test with top_n=5
        top_drivers = extract_top_drivers(
            mock_ebm_model,
            mock_engineered_features,
            gstin,
            top_n=5
        )
        
        assert len(top_drivers) == 5


class TestExtractShapePlotData:
    """Test shape plot data extraction (Requirements 20.1, 20.2, 20.3)."""
    
    def test_extract_shape_plot_data_basic(self, mock_ebm_model, mock_engineered_features):
        """Test extraction of shape plot data for top features."""
        gstin = '27AAPFU0939F1ZV'
        
        shape_plots = extract_shape_plot_data(
            mock_ebm_model,
            mock_engineered_features,
            gstin,
            top_n=3
        )
        
        # Should return dictionary with shape plot data
        assert isinstance(shape_plots, dict)
        assert len(shape_plots) > 0
    
    def test_extract_shape_plot_data_structure(self, mock_ebm_model, mock_engineered_features):
        """Test that shape plot data has required fields (Requirement 20.2)."""
        gstin = '27AAPFU0939F1ZV'
        
        shape_plots = extract_shape_plot_data(
            mock_ebm_model,
            mock_engineered_features,
            gstin,
            top_n=3
        )
        
        # Verify structure for each feature
        for feature_name, plot_data in shape_plots.items():
            assert 'feature_name' in plot_data
            assert 'contribution_weight' in plot_data
            assert 'feature_value' in plot_data
            assert 'baseline_value' in plot_data
            assert 'x_values' in plot_data
            assert 'y_values' in plot_data
            
            # Verify types
            assert isinstance(plot_data['feature_name'], str)
            assert isinstance(plot_data['contribution_weight'], float)
            assert isinstance(plot_data['feature_value'], float)
            assert isinstance(plot_data['baseline_value'], float)
            assert isinstance(plot_data['x_values'], list)
            assert isinstance(plot_data['y_values'], list)
    
    def test_extract_shape_plot_data_x_y_values(self, mock_ebm_model, mock_engineered_features):
        """Test that x_values and y_values are properly extracted."""
        gstin = '27AAPFU0939F1ZV'
        
        shape_plots = extract_shape_plot_data(
            mock_ebm_model,
            mock_engineered_features,
            gstin,
            top_n=3
        )
        
        # Verify x and y values are lists of numbers
        for feature_name, plot_data in shape_plots.items():
            assert len(plot_data['x_values']) > 0
            assert len(plot_data['y_values']) > 0
            assert len(plot_data['x_values']) == len(plot_data['y_values'])
    
    def test_extract_shape_plot_data_nonexistent_gstin(self, mock_ebm_model, mock_engineered_features):
        """Test handling of nonexistent GSTIN."""
        gstin = 'NONEXISTENT_GSTIN'
        
        shape_plots = extract_shape_plot_data(
            mock_ebm_model,
            mock_engineered_features,
            gstin,
            top_n=3
        )
        
        # Should return empty dictionary
        assert len(shape_plots) == 0


class TestPredictiveAnalystNode:
    """Test the complete Predictive Analyst node."""
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_success(
        self,
        state_with_features,
        mock_ebm_model,
        mock_event_queue
    ):
        """Test successful risk prediction workflow."""
        with patch('orchestration.agent_predictive_analyst.load_ebm_model', return_value=mock_ebm_model):
            result_state = await predictive_analyst_node(state_with_features)
            
            # Verify no errors
            assert len(result_state['errors']) == 0
            
            # Verify risk_predictions were added
            assert 'risk_predictions' in result_state
            assert len(result_state['risk_predictions']) == 3
            
            # Verify shape_plots were added
            assert 'shape_plots' in result_state
            
            # Verify each prediction has required fields
            for gstin, prediction in result_state['risk_predictions'].items():
                assert 'gstin' in prediction
                assert 'risk_probability' in prediction
                assert 'risk_level' in prediction
                assert 'top_drivers' in prediction
                
                # Verify risk_probability is between 0 and 1 (Requirement 5.3)
                assert 0 <= prediction['risk_probability'] <= 1
                
                # Verify risk_level is valid
                assert prediction['risk_level'] in ['HIGH_RISK', 'MEDIUM_RISK', 'LOW_RISK']
                
                # Verify top_drivers has exactly 3 items (Requirement 5.4)
                assert len(prediction['top_drivers']) == 3
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_risk_probabilities_bounds(
        self,
        state_with_features,
        mock_ebm_model,
        mock_event_queue
    ):
        """Test that risk probabilities are between 0 and 1 (Requirement 5.3)."""
        with patch('orchestration.agent_predictive_analyst.load_ebm_model', return_value=mock_ebm_model):
            result_state = await predictive_analyst_node(state_with_features)
            
            # Verify all probabilities are in valid range
            for gstin, prediction in result_state['risk_predictions'].items():
                prob = prediction['risk_probability']
                assert 0 <= prob <= 1, f"Probability {prob} out of bounds for {gstin}"
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_top_3_drivers(
        self,
        state_with_features,
        mock_ebm_model,
        mock_event_queue
    ):
        """Test that exactly 3 top drivers are extracted (Requirement 5.4)."""
        with patch('orchestration.agent_predictive_analyst.load_ebm_model', return_value=mock_ebm_model):
            result_state = await predictive_analyst_node(state_with_features)
            
            # Verify each entity has exactly 3 top drivers
            for gstin, prediction in result_state['risk_predictions'].items():
                assert len(prediction['top_drivers']) == 3
                
                # Verify driver structure (Requirement 5.5)
                for driver in prediction['top_drivers']:
                    assert 'feature_name' in driver
                    assert 'contribution_value' in driver
                    assert 'direction' in driver
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_shape_plot_data(
        self,
        state_with_features,
        mock_ebm_model,
        mock_event_queue
    ):
        """Test that shape plot data is extracted (Requirements 20.1, 20.2, 20.3)."""
        with patch('orchestration.agent_predictive_analyst.load_ebm_model', return_value=mock_ebm_model):
            result_state = await predictive_analyst_node(state_with_features)
            
            # Verify shape_plots exist
            assert 'shape_plots' in result_state
            assert len(result_state['shape_plots']) > 0
            
            # Verify shape plot structure for each entity
            for gstin, plots in result_state['shape_plots'].items():
                for feature_name, plot_data in plots.items():
                    # Verify required fields (Requirement 20.2)
                    assert 'feature_name' in plot_data
                    assert 'contribution_weight' in plot_data
                    assert 'feature_value' in plot_data
                    assert 'baseline_value' in plot_data
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_risk_classification(
        self,
        state_with_features,
        mock_ebm_model,
        mock_event_queue
    ):
        """Test risk level classification (Requirements 5.6, 5.7, 5.8)."""
        with patch('orchestration.agent_predictive_analyst.load_ebm_model', return_value=mock_ebm_model):
            result_state = await predictive_analyst_node(state_with_features)
            
            # Based on mock probabilities: [0.9, 0.3, 0.6]
            predictions = result_state['risk_predictions']
            
            # First entity should be HIGH_RISK (0.9 >= 0.7)
            first_gstin = list(predictions.keys())[0]
            assert predictions[first_gstin]['risk_level'] == 'HIGH_RISK'
            
            # Second entity should be LOW_RISK (0.3 < 0.4)
            second_gstin = list(predictions.keys())[1]
            assert predictions[second_gstin]['risk_level'] == 'LOW_RISK'
            
            # Third entity should be MEDIUM_RISK (0.4 <= 0.6 < 0.7)
            third_gstin = list(predictions.keys())[2]
            assert predictions[third_gstin]['risk_level'] == 'MEDIUM_RISK'
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_no_features(self, mock_event_queue):
        """Test error handling when no engineered features are available."""
        state = create_initial_state({})
        state['engineered_features'] = None
        
        result_state = await predictive_analyst_node(state)
        
        # Should have error
        assert len(result_state['errors']) > 0
        assert 'No engineered features' in result_state['errors'][0]
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_empty_features(self, mock_event_queue):
        """Test error handling when engineered features DataFrame is empty."""
        state = create_initial_state({})
        state['engineered_features'] = pd.DataFrame()
        
        result_state = await predictive_analyst_node(state)
        
        # Should have error
        assert len(result_state['errors']) > 0
        assert 'No engineered features' in result_state['errors'][0]
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_model_load_failure(
        self,
        state_with_features,
        mock_event_queue
    ):
        """Test error handling when model loading fails."""
        with patch('orchestration.agent_predictive_analyst.load_ebm_model') as mock_load:
            mock_load.side_effect = Exception("Model file corrupted")
            
            result_state = await predictive_analyst_node(state_with_features)
            
            # Should have error
            assert len(result_state['errors']) > 0
            assert 'failed to load model' in result_state['errors'][0]
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_probability_out_of_bounds(
        self,
        state_with_features,
        mock_ebm_model,
        mock_event_queue
    ):
        """Test error handling when probabilities are out of bounds."""
        # Mock model to return invalid probabilities
        mock_ebm_model.predict_proba.return_value = np.array([
            [0.0, 1.5],  # Invalid: > 1.0
            [0.5, 0.5],
            [0.3, 0.7]
        ])
        
        with patch('orchestration.agent_predictive_analyst.load_ebm_model', return_value=mock_ebm_model):
            result_state = await predictive_analyst_node(state_with_features)
            
            # Should have error
            assert len(result_state['errors']) > 0
            assert 'out of bounds' in result_state['errors'][0]
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_sse_broadcasting(
        self,
        state_with_features,
        mock_ebm_model,
        mock_event_queue
    ):
        """Test that SSE messages are broadcast (Requirement 19.6)."""
        with patch('orchestration.agent_predictive_analyst.load_ebm_model', return_value=mock_ebm_model):
            await predictive_analyst_node(state_with_features)
            
            # Collect all messages from queue
            messages = []
            while not mock_event_queue.empty():
                messages.append(await mock_event_queue.get())
            
            # Verify SSE messages were broadcast
            assert len(messages) >= 2
            
            # Check for specific messages
            message_text = ' '.join(messages)
            assert 'Agent 4' in message_text
            assert 'Loading EBM model' in message_text or 'Computing risk scores' in message_text
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_risk_count_summary(
        self,
        state_with_features,
        mock_ebm_model,
        mock_event_queue
    ):
        """Test that risk count summary is broadcast."""
        with patch('orchestration.agent_predictive_analyst.load_ebm_model', return_value=mock_ebm_model):
            await predictive_analyst_node(state_with_features)
            
            # Collect all messages
            messages = []
            while not mock_event_queue.empty():
                messages.append(await mock_event_queue.get())
            
            # Should have completion message with counts
            completion_messages = [m for m in messages if 'Risk scoring complete' in m]
            assert len(completion_messages) > 0
            
            # Verify counts are included
            completion_msg = completion_messages[0]
            assert 'HIGH_RISK' in completion_msg
            assert 'MEDIUM_RISK' in completion_msg
            assert 'LOW_RISK' in completion_msg
    
    @pytest.mark.asyncio
    async def test_predictive_analyst_node_general_exception(
        self,
        state_with_features,
        mock_ebm_model,
        mock_event_queue
    ):
        """Test error handling for unexpected exceptions."""
        with patch('orchestration.agent_predictive_analyst.load_ebm_model', return_value=mock_ebm_model):
            # Mock predict_proba to raise an exception
            mock_ebm_model.predict_proba.side_effect = Exception("Unexpected error")
            
            result_state = await predictive_analyst_node(state_with_features)
            
            # Should have error
            assert len(result_state['errors']) > 0
            assert 'Agent 4 failed' in result_state['errors'][0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
