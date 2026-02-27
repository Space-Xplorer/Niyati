"""
Unit Tests for Agent 5: Niyati Explainer

Tests the Niyati Explainer agent functionality including:
- LLM client initialization
- Prompt formatting
- Narrative generation with circuit breaker
- Template fallback
- HIGH_RISK prefix enforcement
- Response validation
- SSE message broadcasting
- Integration with existing risk predictions
"""

import pytest
import os
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from orchestration.agent_niyati_explainer import (
    format_structured_prompt,
    validate_narrative,
    ensure_high_risk_prefix,
    get_llm_client,
    call_llm_with_circuit_breaker,
    generate_narrative_for_entity,
    niyati_explainer_node,
    set_event_queue,
    circuit_breaker
)
from orchestration.state import NiyatiState, create_initial_state
from utils.circuit_breaker import generate_template_narrative, CircuitState


class TestPromptFormatting:
    """Test structured prompt formatting"""
    
    def test_format_structured_prompt_basic(self):
        """Test basic prompt formatting with required fields"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "HIGH_RISK"
        risk_probability = 0.8923
        top_drivers = [
            {'feature_name': 'ghost_invoice_pct', 'contribution_value': 0.34, 'direction': 'positive'},
            {'feature_name': 'payment_gap_pct', 'contribution_value': 0.28, 'direction': 'positive'},
            {'feature_name': 'shared_contact_flag', 'contribution_value': 0.19, 'direction': 'positive'}
        ]
        
        prompt = format_structured_prompt(gstin, risk_level, risk_probability, top_drivers)
        
        assert gstin in prompt
        assert "HIGH_RISK" in prompt
        assert "89.2%" in prompt
        assert "Ghost Invoice Pct" in prompt
        assert "34.0%" in prompt
    
    def test_format_structured_prompt_with_patterns(self):
        """Test prompt formatting with structural patterns"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "HIGH_RISK"
        risk_probability = 0.8923
        top_drivers = [
            {'feature_name': 'ghost_invoice_pct', 'contribution_value': 0.34, 'direction': 'positive'}
        ]
        structural_patterns = {
            'circular_trade_count': 2,
            'ghost_invoice_count': 12,
            'spider_web_involvement': True
        }
        
        prompt = format_structured_prompt(
            gstin, risk_level, risk_probability, top_drivers, structural_patterns
        )
        
        assert "2 circular trade pattern(s)" in prompt
        assert "12 ghost invoice(s)" in prompt
        assert "Spider web network involvement" in prompt


class TestNarrativeValidation:
    """Test narrative validation logic"""
    
    def test_validate_narrative_valid(self):
        """Test validation passes for valid narrative"""
        narrative = "HIGH RISK — Entity shows significant fraud indicators with multiple red flags detected."
        assert validate_narrative(narrative) is True
    
    def test_validate_narrative_too_short(self):
        """Test validation fails for short narrative"""
        narrative = "Short text"
        assert validate_narrative(narrative) is False
    
    def test_validate_narrative_empty(self):
        """Test validation fails for empty narrative"""
        assert validate_narrative("") is False
        assert validate_narrative(None) is False
    
    def test_validate_narrative_exactly_50_chars(self):
        """Test validation passes for exactly 50 characters"""
        narrative = "A" * 50
        assert validate_narrative(narrative) is True


class TestHighRiskPrefix:
    """Test HIGH_RISK prefix enforcement"""
    
    def test_ensure_high_risk_prefix_adds_prefix(self):
        """Test prefix is added when missing for HIGH_RISK"""
        narrative = "Entity shows significant fraud indicators."
        result = ensure_high_risk_prefix(narrative, "HIGH_RISK")
        assert result.startswith("HIGH RISK —")
    
    def test_ensure_high_risk_prefix_preserves_existing(self):
        """Test prefix is not duplicated if already present"""
        narrative = "HIGH RISK — Entity shows significant fraud indicators."
        result = ensure_high_risk_prefix(narrative, "HIGH_RISK")
        assert result.count("HIGH RISK") == 1
    
    def test_ensure_high_risk_prefix_not_added_for_medium(self):
        """Test prefix is not added for MEDIUM_RISK"""
        narrative = "Entity shows moderate fraud indicators."
        result = ensure_high_risk_prefix(narrative, "MEDIUM_RISK")
        assert not result.startswith("HIGH RISK")
    
    def test_ensure_high_risk_prefix_not_added_for_low(self):
        """Test prefix is not added for LOW_RISK"""
        narrative = "Entity shows minimal fraud indicators."
        result = ensure_high_risk_prefix(narrative, "LOW_RISK")
        assert not result.startswith("HIGH RISK")


class TestTemplateFallback:
    """Test template-based narrative generation"""
    
    def test_template_narrative_high_risk(self):
        """Test template generation for HIGH_RISK entity"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "HIGH_RISK"
        risk_probability = 0.8923
        top_drivers = [
            {'feature': 'ghost_invoice_pct', 'contribution': 0.34, 'direction': 'positive'},
            {'feature': 'payment_gap_pct', 'contribution': 0.28, 'direction': 'positive'}
        ]
        
        narrative = generate_template_narrative(gstin, risk_level, risk_probability, top_drivers)
        
        assert narrative.startswith("HIGH RISK —")
        assert gstin in narrative
        assert "89.2%" in narrative
        assert "Ghost Invoice Pct" in narrative
        assert "Immediate audit recommended" in narrative
    
    def test_template_narrative_medium_risk(self):
        """Test template generation for MEDIUM_RISK entity"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "MEDIUM_RISK"
        risk_probability = 0.55
        top_drivers = [
            {'feature': 'filing_gap', 'contribution': 0.25, 'direction': 'positive'}
        ]
        
        narrative = generate_template_narrative(gstin, risk_level, risk_probability, top_drivers)
        
        assert narrative.startswith("MEDIUM RISK —")
        assert "Enhanced monitoring recommended" in narrative
    
    def test_template_narrative_low_risk(self):
        """Test template generation for LOW_RISK entity"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "LOW_RISK"
        risk_probability = 0.25
        top_drivers = [
            {'feature': 'transaction_count', 'contribution': 0.15, 'direction': 'negative'}
        ]
        
        narrative = generate_template_narrative(gstin, risk_level, risk_probability, top_drivers)
        
        assert narrative.startswith("LOW RISK —")
        assert "Standard compliance monitoring sufficient" in narrative
    
    def test_template_narrative_with_patterns(self):
        """Test template includes structural patterns"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "HIGH_RISK"
        risk_probability = 0.85
        top_drivers = [
            {'feature': 'ghost_invoice_pct', 'contribution': 0.34, 'direction': 'positive'}
        ]
        structural_patterns = {
            'circular_trade_count': 2,
            'ghost_invoice_count': 12,
            'spider_web_involvement': True
        }
        
        narrative = generate_template_narrative(
            gstin, risk_level, risk_probability, top_drivers, structural_patterns
        )
        
        assert "2 circular trade pattern(s)" in narrative
        assert "12 ghost invoice(s)" in narrative
        assert "spider web network involvement" in narrative


class TestLLMClientInitialization:
    """Test LLM client initialization"""
    
    @patch.dict(os.environ, {'LLM_PROVIDER': 'groq', 'LLM_API_KEY': 'test_key'})
    @patch('langchain_groq.ChatGroq')
    def test_get_llm_client_groq(self, mock_groq):
        """Test Groq client initialization"""
        mock_client = Mock()
        mock_groq.return_value = mock_client
        
        client, provider_name = get_llm_client()
        
        assert provider_name == 'Groq (Llama-3-8b)'
        mock_groq.assert_called_once()
        call_kwargs = mock_groq.call_args[1]
        assert call_kwargs['api_key'] == 'test_key'
        assert call_kwargs['model_name'] == 'llama-3-8b-8192'
        assert call_kwargs['temperature'] == 0.3
        assert call_kwargs['max_tokens'] == 200
    
    @patch.dict(os.environ, {'LLM_PROVIDER': 'groq', 'LLM_API_KEY': 'your_groq_api_key_here'})
    def test_get_llm_client_missing_api_key(self):
        """Test error when API key is not configured"""
        with pytest.raises(ValueError, match="LLM_API_KEY not configured"):
            get_llm_client()
    
    @patch.dict(os.environ, {'LLM_PROVIDER': 'unsupported', 'LLM_API_KEY': 'test_key'})
    def test_get_llm_client_unsupported_provider(self):
        """Test error for unsupported provider"""
        with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER"):
            get_llm_client()


class TestCircuitBreakerBehavior:
    """Test circuit breaker behavior with LLM API failures"""
    
    def setup_method(self):
        """Reset circuit breaker before each test"""
        circuit_breaker.reset()
    
    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures"""
        # Create a function that always fails
        def failing_function():
            raise Exception("LLM API error")
        
        # First 3 calls should raise exceptions
        for i in range(3):
            with pytest.raises(Exception):
                circuit_breaker.call(failing_function)
        
        # Circuit should now be OPEN
        assert circuit_breaker.get_state() == CircuitState.OPEN.value
        
        # Next call should fail immediately without calling function
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            circuit_breaker.call(failing_function)
    
    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovers after timeout"""
        # Create a function that fails then succeeds
        call_count = [0]
        
        def flaky_function():
            call_count[0] += 1
            if call_count[0] <= 3:
                raise Exception("LLM API error")
            return "Success"
        
        # Open the circuit
        for i in range(3):
            with pytest.raises(Exception):
                circuit_breaker.call(flaky_function)
        
        assert circuit_breaker.get_state() == CircuitState.OPEN.value
        
        # Simulate recovery timeout by manipulating last_failure_time
        circuit_breaker.last_failure_time = 0  # Set to past
        
        # Next call should attempt recovery (HALF_OPEN)
        result = circuit_breaker.call(flaky_function)
        assert result == "Success"
        assert circuit_breaker.get_state() == CircuitState.CLOSED.value
    
    @patch.dict(os.environ, {'LLM_PROVIDER': 'groq', 'LLM_API_KEY': 'test_key'})
    @patch('langchain_groq.ChatGroq')
    def test_llm_call_with_circuit_breaker_success(self, mock_groq):
        """Test successful LLM call with circuit breaker"""
        # Setup mock LLM client
        mock_response = Mock()
        mock_response.content = "This is a valid narrative with more than fifty characters to pass validation."
        mock_client = Mock()
        mock_client.invoke.return_value = mock_response
        
        prompt = "Test prompt"
        result = call_llm_with_circuit_breaker(mock_client, prompt)
        
        assert len(result) > 50
        assert circuit_breaker.get_state() == CircuitState.CLOSED.value
    
    @patch.dict(os.environ, {'LLM_PROVIDER': 'groq', 'LLM_API_KEY': 'test_key'})
    @patch('langchain_groq.ChatGroq')
    def test_llm_call_with_circuit_breaker_failure(self, mock_groq):
        """Test LLM call failure triggers circuit breaker"""
        # Setup mock LLM client that fails
        mock_client = Mock()
        mock_client.invoke.side_effect = Exception("API timeout")
        
        prompt = "Test prompt"
        
        # First failure
        with pytest.raises(Exception, match="API timeout"):
            call_llm_with_circuit_breaker(mock_client, prompt)
        
        assert circuit_breaker.failure_count == 1


class TestNarrativeGeneration:
    """Test narrative generation with LLM and fallback"""
    
    def setup_method(self):
        """Reset circuit breaker before each test"""
        circuit_breaker.reset()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {'LLM_PROVIDER': 'groq', 'LLM_API_KEY': 'test_key'})
    @patch('langchain_groq.ChatGroq')
    async def test_generate_narrative_with_llm_success(self, mock_groq):
        """Test narrative generation with successful LLM call"""
        # Setup mock LLM client
        mock_response = Mock()
        mock_response.content = "HIGH RISK — Entity 27AAPFU0939F1ZV shows significant fraud indicators with ghost invoices and payment gaps."
        mock_client = Mock()
        mock_client.invoke.return_value = mock_response
        mock_groq.return_value = mock_client
        
        gstin = "27AAPFU0939F1ZV"
        risk_prediction = {
            'risk_level': 'HIGH_RISK',
            'risk_probability': 0.8923,
            'top_drivers': [
                {'feature_name': 'ghost_invoice_pct', 'contribution_value': 0.34, 'direction': 'positive'},
                {'feature_name': 'payment_gap_pct', 'contribution_value': 0.28, 'direction': 'positive'}
            ]
        }
        structural_patterns = {
            'circular_trade_count': 2,
            'ghost_invoice_count': 12,
            'spider_web_involvement': True
        }
        
        llm_client, provider_name = get_llm_client()
        narrative = await generate_narrative_for_entity(
            gstin, risk_prediction, structural_patterns, llm_client, provider_name
        )
        
        assert narrative.startswith("HIGH RISK —")
        assert len(narrative) > 50
        assert gstin in narrative
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {'LLM_PROVIDER': 'groq', 'LLM_API_KEY': 'test_key'})
    @patch('langchain_groq.ChatGroq')
    async def test_generate_narrative_with_llm_failure_fallback(self, mock_groq):
        """Test narrative generation falls back to template on LLM failure"""
        # Setup mock LLM client that fails
        mock_client = Mock()
        mock_client.invoke.side_effect = Exception("API timeout")
        mock_groq.return_value = mock_client
        
        gstin = "27AAPFU0939F1ZV"
        risk_prediction = {
            'risk_level': 'HIGH_RISK',
            'risk_probability': 0.8923,
            'top_drivers': [
                {'feature_name': 'ghost_invoice_pct', 'contribution_value': 0.34, 'direction': 'positive'},
                {'feature_name': 'payment_gap_pct', 'contribution_value': 0.28, 'direction': 'positive'}
            ]
        }
        
        llm_client, provider_name = get_llm_client()
        narrative = await generate_narrative_for_entity(
            gstin, risk_prediction, None, llm_client, provider_name
        )
        
        # Should use template fallback
        assert narrative.startswith("HIGH RISK —")
        assert gstin in narrative
        assert "89.2%" in narrative
        assert "Immediate audit recommended" in narrative
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {'LLM_PROVIDER': 'groq', 'LLM_API_KEY': 'test_key'})
    @patch('langchain_groq.ChatGroq')
    async def test_generate_narrative_invalid_response_fallback(self, mock_groq):
        """Test narrative generation falls back when LLM response is too short"""
        # Setup mock LLM client with invalid response
        mock_response = Mock()
        mock_response.content = "Too short"  # Less than 50 characters
        mock_client = Mock()
        mock_client.invoke.return_value = mock_response
        mock_groq.return_value = mock_client
        
        gstin = "27AAPFU0939F1ZV"
        risk_prediction = {
            'risk_level': 'MEDIUM_RISK',
            'risk_probability': 0.55,
            'top_drivers': [
                {'feature_name': 'filing_gap', 'contribution_value': 0.25, 'direction': 'positive'}
            ]
        }
        
        llm_client, provider_name = get_llm_client()
        narrative = await generate_narrative_for_entity(
            gstin, risk_prediction, None, llm_client, provider_name
        )
        
        # Should use template fallback
        assert narrative.startswith("MEDIUM RISK —")
        assert len(narrative) > 50


class TestNiyatiExplainerNode:
    """Test the complete Niyati Explainer LangGraph node"""
    
    def setup_method(self):
        """Reset circuit breaker and setup event queue before each test"""
        circuit_breaker.reset()
        # Setup mock event queue
        self.event_queue = asyncio.Queue()
        set_event_queue(self.event_queue)
    
    @pytest.mark.asyncio
    async def test_niyati_explainer_node_with_risk_predictions(self):
        """Test node processes risk predictions and generates narratives"""
        # Create state with risk predictions
        state = NiyatiState(
            csv_files={},
            validated_data={},
            engineered_features=None,
            change_summary=None,
            graph_built=True,
            structural_patterns=[
                {
                    'pattern_type': 'circular_trade',
                    'gstin_list': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX'],
                    'risk_score': 0.85
                },
                {
                    'pattern_type': 'ghost_invoice',
                    'gstin_list': ['27AAPFU0939F1ZV'],
                    'count': 12
                }
            ],
            risk_predictions={
                '27AAPFU0939F1ZV': {
                    'risk_level': 'HIGH_RISK',
                    'risk_probability': 0.8923,
                    'top_drivers': [
                        {'feature_name': 'ghost_invoice_pct', 'contribution_value': 0.34, 'direction': 'positive'},
                        {'feature_name': 'payment_gap_pct', 'contribution_value': 0.28, 'direction': 'positive'},
                        {'feature_name': 'shared_contact_flag', 'contribution_value': 0.19, 'direction': 'positive'}
                    ]
                },
                '29AABCU9603R1ZX': {
                    'risk_level': 'LOW_RISK',
                    'risk_probability': 0.25,
                    'top_drivers': [
                        {'feature_name': 'transaction_count', 'contribution_value': 0.15, 'direction': 'negative'}
                    ]
                }
            },
            shape_plots={},
            narratives={},
            errors=[]
        )
        
        # Mock LLM to use template fallback (no API key configured)
        with patch.dict(os.environ, {'LLM_PROVIDER': 'groq', 'LLM_API_KEY': 'your_groq_api_key_here'}):
            result_state = await niyati_explainer_node(state)
        
        # Verify narratives were generated
        assert len(result_state['narratives']) == 2
        assert '27AAPFU0939F1ZV' in result_state['narratives']
        assert '29AABCU9603R1ZX' in result_state['narratives']
        
        # Verify HIGH_RISK narrative has correct prefix
        high_risk_narrative = result_state['narratives']['27AAPFU0939F1ZV']
        assert high_risk_narrative.startswith("HIGH RISK —")
        assert "89.2%" in high_risk_narrative
        
        # Verify LOW_RISK narrative
        low_risk_narrative = result_state['narratives']['29AABCU9603R1ZX']
        assert low_risk_narrative.startswith("LOW RISK —")
        
        # Verify no errors
        assert len(result_state['errors']) == 0
    
    @pytest.mark.asyncio
    async def test_niyati_explainer_node_sse_broadcasting(self):
        """Test node broadcasts SSE messages"""
        state = NiyatiState(
            csv_files={},
            validated_data={},
            engineered_features=None,
            change_summary=None,
            graph_built=True,
            structural_patterns=[],
            risk_predictions={
                '27AAPFU0939F1ZV': {
                    'risk_level': 'HIGH_RISK',
                    'risk_probability': 0.85,
                    'top_drivers': [
                        {'feature_name': 'ghost_invoice_pct', 'contribution_value': 0.34, 'direction': 'positive'}
                    ]
                }
            },
            shape_plots={},
            narratives={},
            errors=[]
        )
        
        with patch.dict(os.environ, {'LLM_PROVIDER': 'groq', 'LLM_API_KEY': 'your_groq_api_key_here'}):
            result_state = await niyati_explainer_node(state)
        
        # Collect SSE messages
        messages = []
        while not self.event_queue.empty():
            messages.append(await self.event_queue.get())
        
        # Verify SSE messages were broadcast
        assert len(messages) >= 2, f"Expected at least 2 messages, got {len(messages)}: {messages}"
        assert any("Agent 5:" in msg for msg in messages), f"No 'Agent 5:' message found in: {messages}"
        # Check for provider or fallback message
        has_provider_msg = any(
            "Template Fallback" in msg or "Groq" in msg or "OpenAI" in msg or "LLM not configured" in msg 
            for msg in messages
        )
        assert has_provider_msg, f"No provider/fallback message found in: {messages}"
        assert any("Generated" in msg and "audit narratives" in msg for msg in messages)
    
    @pytest.mark.asyncio
    async def test_niyati_explainer_node_no_risk_predictions(self):
        """Test node handles missing risk predictions gracefully"""
        state = NiyatiState(
            csv_files={},
            validated_data={},
            engineered_features=None,
            change_summary=None,
            graph_built=True,
            structural_patterns=[],
            risk_predictions={},  # Empty
            shape_plots={},
            narratives={},
            errors=[]
        )
        
        result_state = await niyati_explainer_node(state)
        
        # Verify error was recorded
        assert len(result_state['errors']) == 1
        assert "No risk predictions available" in result_state['errors'][0]
        
        # Verify no narratives generated
        assert len(result_state['narratives']) == 0
    
    @pytest.mark.asyncio
    async def test_niyati_explainer_node_includes_quantitative_values(self):
        """Test narratives include quantitative values from top drivers"""
        state = NiyatiState(
            csv_files={},
            validated_data={},
            engineered_features=None,
            change_summary=None,
            graph_built=True,
            structural_patterns=[],
            risk_predictions={
                '27AAPFU0939F1ZV': {
                    'risk_level': 'HIGH_RISK',
                    'risk_probability': 0.8923,
                    'top_drivers': [
                        {'feature_name': 'ghost_invoice_pct', 'contribution_value': 0.34, 'direction': 'positive'},
                        {'feature_name': 'payment_gap_pct', 'contribution_value': 0.28, 'direction': 'positive'}
                    ]
                }
            },
            shape_plots={},
            narratives={},
            errors=[]
        )
        
        with patch.dict(os.environ, {'LLM_PROVIDER': 'groq', 'LLM_API_KEY': 'your_groq_api_key_here'}):
            result_state = await niyati_explainer_node(state)
        
        narrative = result_state['narratives']['27AAPFU0939F1ZV']
        
        # Verify quantitative values are included
        assert "89.2%" in narrative or "0.8923" in narrative  # Risk probability
        # Template includes feature names and contributions
        assert any(term in narrative.lower() for term in ['ghost', 'invoice', 'payment', 'gap'])
    
    @pytest.mark.asyncio
    async def test_niyati_explainer_node_with_structural_patterns(self):
        """Test narratives include structural pattern information"""
        state = NiyatiState(
            csv_files={},
            validated_data={},
            engineered_features=None,
            change_summary=None,
            graph_built=True,
            structural_patterns=[
                {
                    'pattern_type': 'circular_trade',
                    'gstin_list': ['27AAPFU0939F1ZV'],
                    'risk_score': 0.85
                },
                {
                    'pattern_type': 'ghost_invoice',
                    'gstin_list': ['27AAPFU0939F1ZV'],
                    'count': 12
                },
                {
                    'pattern_type': 'spider_web',
                    'gstin_list': ['27AAPFU0939F1ZV', '29AABCU9603R1ZX'],
                    'cluster_size': 5
                }
            ],
            risk_predictions={
                '27AAPFU0939F1ZV': {
                    'risk_level': 'HIGH_RISK',
                    'risk_probability': 0.85,
                    'top_drivers': [
                        {'feature_name': 'ghost_invoice_pct', 'contribution_value': 0.34, 'direction': 'positive'}
                    ]
                }
            },
            shape_plots={},
            narratives={},
            errors=[]
        )
        
        with patch.dict(os.environ, {'LLM_PROVIDER': 'groq', 'LLM_API_KEY': 'your_groq_api_key_here'}):
            result_state = await niyati_explainer_node(state)
        
        narrative = result_state['narratives']['27AAPFU0939F1ZV']
        
        # Verify structural patterns are mentioned
        # Template includes pattern counts
        assert "circular trade" in narrative.lower() or "1 circular" in narrative.lower()
        assert "ghost invoice" in narrative.lower() or "12 ghost" in narrative.lower()
        assert "spider web" in narrative.lower() or "network" in narrative.lower()


class TestNarrativeContentRequirements:
    """Test that narratives meet all content requirements from Requirements 6.2-6.5"""
    
    def test_narrative_includes_all_required_information(self):
        """Test narrative includes risk level, probability, and top drivers"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "HIGH_RISK"
        risk_probability = 0.8923
        top_drivers = [
            {'feature': 'ghost_invoice_pct', 'contribution': 0.34, 'direction': 'positive'},
            {'feature': 'payment_gap_pct', 'contribution': 0.28, 'direction': 'positive'},
            {'feature': 'shared_contact_flag', 'contribution': 0.19, 'direction': 'positive'}
        ]
        structural_patterns = {
            'circular_trade_count': 2,
            'ghost_invoice_count': 12,
            'spider_web_involvement': True
        }
        
        narrative = generate_template_narrative(
            gstin, risk_level, risk_probability, top_drivers, structural_patterns
        )
        
        # Requirement 6.5: ML prediction narrative content
        assert "HIGH RISK" in narrative  # Risk level
        assert "89.2%" in narrative  # Risk probability as percentage
        assert "Ghost Invoice Pct" in narrative  # Top driver 1
        assert "Payment Gap Pct" in narrative  # Top driver 2
        assert "Shared Contact Flag" in narrative  # Top driver 3
        
        # Requirement 6.2: Circular trade narrative content
        assert "2 circular trade pattern(s)" in narrative
        
        # Requirement 6.3: Ghost invoice narrative content
        assert "12 ghost invoice(s)" in narrative
        
        # Requirement 6.4: Spider web narrative content
        assert "spider web network involvement" in narrative
        
        # Requirement 6.6: HIGH_RISK prefix
        assert narrative.startswith("HIGH RISK —")
        
        # Requirement 6.1: Narrative in English
        assert len(narrative) > 0
        assert isinstance(narrative, str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
