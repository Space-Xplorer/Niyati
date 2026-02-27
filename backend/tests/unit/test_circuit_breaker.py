"""
Unit tests for circuit breaker utility
"""

import pytest
import time
from utils.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    generate_template_narrative
)


class TestCircuitBreaker:
    """Test suite for CircuitBreaker class"""
    
    def test_initial_state_is_closed(self):
        """Circuit breaker should start in CLOSED state"""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.get_state() == "closed"
    
    def test_successful_call_keeps_circuit_closed(self):
        """Successful calls should keep circuit CLOSED"""
        cb = CircuitBreaker()
        
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    def test_single_failure_keeps_circuit_closed(self):
        """Single failure should not open circuit (threshold=3)"""
        cb = CircuitBreaker(failure_threshold=3)
        
        def failing_func():
            raise ValueError("API error")
        
        with pytest.raises(ValueError):
            cb.call(failing_func)
        
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 1
    
    def test_circuit_opens_after_threshold_failures(self):
        """Circuit should open after reaching failure threshold"""
        cb = CircuitBreaker(failure_threshold=3)
        
        def failing_func():
            raise ValueError("API error")
        
        # First 3 failures
        for i in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3
    
    def test_open_circuit_rejects_calls(self):
        """OPEN circuit should reject calls without executing function"""
        cb = CircuitBreaker(failure_threshold=2)
        
        call_count = 0
        
        def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("API error")
        
        # Trigger 2 failures to open circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        assert call_count == 2
        
        # Next call should be rejected without executing function
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            cb.call(failing_func)
        
        assert call_count == 2  # Function was not called
    
    def test_circuit_transitions_to_half_open_after_timeout(self):
        """Circuit should transition to HALF_OPEN after recovery timeout"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        
        def failing_func():
            raise ValueError("API error")
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        # Next call should transition to HALF_OPEN and execute
        with pytest.raises(ValueError):
            cb.call(failing_func)
        
        # Circuit should be OPEN again after failure in HALF_OPEN
        assert cb.state == CircuitState.OPEN
    
    def test_successful_call_in_half_open_closes_circuit(self):
        """Successful call in HALF_OPEN state should close circuit"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        
        def failing_func():
            raise ValueError("API error")
        
        def success_func():
            return "recovered"
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        # Successful call should close circuit
        result = cb.call(success_func)
        assert result == "recovered"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    def test_reset_closes_circuit_and_clears_failures(self):
        """Manual reset should close circuit and clear failure count"""
        cb = CircuitBreaker(failure_threshold=2)
        
        def failing_func():
            raise ValueError("API error")
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 2
        
        # Reset circuit
        cb.reset()
        
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.last_failure_time is None
    
    def test_custom_failure_threshold(self):
        """Circuit breaker should respect custom failure threshold"""
        cb = CircuitBreaker(failure_threshold=5)
        
        def failing_func():
            raise ValueError("API error")
        
        # 4 failures should not open circuit
        for i in range(4):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 4
        
        # 5th failure should open circuit
        with pytest.raises(ValueError):
            cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 5
    
    def test_success_resets_failure_count(self):
        """Successful call should reset failure count"""
        cb = CircuitBreaker(failure_threshold=3)
        
        def failing_func():
            raise ValueError("API error")
        
        def success_func():
            return "success"
        
        # 2 failures
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.failure_count == 2
        
        # Success should reset count
        cb.call(success_func)
        assert cb.failure_count == 0
        assert cb.state == CircuitState.CLOSED


class TestTemplateNarrative:
    """Test suite for generate_template_narrative function"""
    
    def test_high_risk_narrative_format(self):
        """HIGH_RISK narrative should have correct prefix and format"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "HIGH_RISK"
        risk_probability = 0.8923
        top_drivers = [
            {"feature": "ghost_invoice_pct", "contribution": 0.34, "direction": "positive"},
            {"feature": "payment_gap_pct", "contribution": 0.28, "direction": "positive"},
            {"feature": "shared_contact_flag", "contribution": 0.19, "direction": "positive"}
        ]
        
        narrative = generate_template_narrative(
            gstin, risk_level, risk_probability, top_drivers
        )
        
        assert narrative.startswith("HIGH RISK —")
        assert gstin in narrative
        assert "89.2%" in narrative
        assert "Ghost Invoice Pct" in narrative
        assert "Payment Gap Pct" in narrative
        assert "Shared Contact Flag" in narrative
        assert "Immediate audit recommended" in narrative
    
    def test_medium_risk_narrative_format(self):
        """MEDIUM_RISK narrative should have correct format"""
        gstin = "29AABCU9603R1ZX"
        risk_level = "MEDIUM_RISK"
        risk_probability = 0.55
        top_drivers = [
            {"feature": "filing_gap", "contribution": 0.25, "direction": "positive"},
            {"feature": "payment_gap", "contribution": 0.18, "direction": "positive"},
            {"feature": "transaction_count", "contribution": -0.12, "direction": "negative"}
        ]
        
        narrative = generate_template_narrative(
            gstin, risk_level, risk_probability, top_drivers
        )
        
        assert narrative.startswith("MEDIUM RISK —")
        assert gstin in narrative
        assert "55.0%" in narrative
        assert "Filing Gap" in narrative
        assert "Enhanced monitoring recommended" in narrative
    
    def test_low_risk_narrative_format(self):
        """LOW_RISK narrative should have correct format"""
        gstin = "24AABCU1234A1Z5"
        risk_level = "LOW_RISK"
        risk_probability = 0.15
        top_drivers = [
            {"feature": "avg_invoice_value", "contribution": 0.08, "direction": "positive"},
            {"feature": "vendor_diversity", "contribution": -0.05, "direction": "negative"},
            {"feature": "filing_delay_avg", "contribution": 0.03, "direction": "positive"}
        ]
        
        narrative = generate_template_narrative(
            gstin, risk_level, risk_probability, top_drivers
        )
        
        assert narrative.startswith("LOW RISK —")
        assert gstin in narrative
        assert "15.0%" in narrative
        assert "Standard compliance monitoring sufficient" in narrative
    
    def test_narrative_with_structural_patterns(self):
        """Narrative should include structural pattern information"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "HIGH_RISK"
        risk_probability = 0.85
        top_drivers = [
            {"feature": "ghost_invoice_pct", "contribution": 0.34, "direction": "positive"}
        ]
        structural_patterns = {
            "circular_trade_count": 2,
            "ghost_invoice_count": 12,
            "spider_web_involvement": True
        }
        
        narrative = generate_template_narrative(
            gstin, risk_level, risk_probability, top_drivers, structural_patterns
        )
        
        assert "2 circular trade pattern(s)" in narrative
        assert "12 ghost invoice(s)" in narrative
        assert "spider web network involvement" in narrative
    
    def test_narrative_without_structural_patterns(self):
        """Narrative should work without structural patterns"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "MEDIUM_RISK"
        risk_probability = 0.50
        top_drivers = [
            {"feature": "filing_gap", "contribution": 0.25, "direction": "positive"}
        ]
        
        narrative = generate_template_narrative(
            gstin, risk_level, risk_probability, top_drivers
        )
        
        assert gstin in narrative
        assert "50.0%" in narrative
        assert "Filing Gap" in narrative
        # Should not contain structural pattern text
        assert "circular trade" not in narrative.lower()
    
    def test_narrative_handles_empty_structural_patterns(self):
        """Narrative should handle structural patterns with zero counts"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "LOW_RISK"
        risk_probability = 0.20
        top_drivers = [
            {"feature": "payment_gap", "contribution": 0.10, "direction": "positive"}
        ]
        structural_patterns = {
            "circular_trade_count": 0,
            "ghost_invoice_count": 0,
            "spider_web_involvement": False
        }
        
        narrative = generate_template_narrative(
            gstin, risk_level, risk_probability, top_drivers, structural_patterns
        )
        
        assert gstin in narrative
        # Should not mention patterns with zero counts
        assert "circular trade" not in narrative.lower()
        assert "ghost invoice" not in narrative.lower()
        assert "spider web" not in narrative.lower()
    
    def test_narrative_handles_top_3_drivers_only(self):
        """Narrative should use only top 3 drivers even if more provided"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "HIGH_RISK"
        risk_probability = 0.75
        top_drivers = [
            {"feature": "driver_1", "contribution": 0.30, "direction": "positive"},
            {"feature": "driver_2", "contribution": 0.25, "direction": "positive"},
            {"feature": "driver_3", "contribution": 0.20, "direction": "positive"},
            {"feature": "driver_4", "contribution": 0.15, "direction": "positive"},
            {"feature": "driver_5", "contribution": 0.10, "direction": "positive"}
        ]
        
        narrative = generate_template_narrative(
            gstin, risk_level, risk_probability, top_drivers
        )
        
        # Should contain first 3 drivers
        assert "Driver 1" in narrative
        assert "Driver 2" in narrative
        assert "Driver 3" in narrative
        # Should not contain 4th and 5th drivers
        assert "Driver 4" not in narrative
        assert "Driver 5" not in narrative
    
    def test_narrative_formats_feature_names_readable(self):
        """Feature names should be converted to readable format"""
        gstin = "27AAPFU0939F1ZV"
        risk_level = "MEDIUM_RISK"
        risk_probability = 0.60
        top_drivers = [
            {"feature": "ghost_invoice_pct", "contribution": 0.30, "direction": "positive"},
            {"feature": "payment_gap_pct", "contribution": 0.25, "direction": "positive"},
            {"feature": "shared_contact_flag", "contribution": 0.20, "direction": "positive"}
        ]
        
        narrative = generate_template_narrative(
            gstin, risk_level, risk_probability, top_drivers
        )
        
        # Underscores should be replaced with spaces and title-cased
        assert "Ghost Invoice Pct" in narrative
        assert "Payment Gap Pct" in narrative
        assert "Shared Contact Flag" in narrative
        # Original underscore format should not appear
        assert "ghost_invoice_pct" not in narrative
