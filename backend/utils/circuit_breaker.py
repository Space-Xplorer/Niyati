"""
Circuit Breaker Utility for LLM API Resilience

Implements circuit breaker pattern to handle LLM API failures gracefully.
When the circuit breaker opens (after failure_threshold failures), it falls back
to template-based narrative generation.
"""

import time
from typing import Callable, Any, Dict, List, Optional
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failures exceeded threshold, using fallback
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker for LLM API calls with automatic fallback.
    
    Attributes:
        failure_threshold: Number of consecutive failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery (half-open state)
    """
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before circuit opens (default: 3)
            recovery_timeout: Seconds before attempting recovery (default: 60)
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time: Optional[float] = None
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func if successful
            
        Raises:
            Exception: If circuit is OPEN or func fails in CLOSED/HALF_OPEN state
        """
        # Check if we should attempt recovery
        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception(f"Circuit breaker is OPEN. Failures: {self.failure_count}")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return False
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def reset(self):
        """Manually reset circuit breaker to CLOSED state"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    
    def get_state(self) -> str:
        """Get current circuit state as string"""
        return self.state.value


def generate_template_narrative(
    gstin: str,
    risk_level: str,
    risk_probability: float,
    top_drivers: List[Dict[str, Any]],
    structural_patterns: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate template-based narrative when LLM is unavailable.
    
    This is the fallback function used when the circuit breaker is OPEN.
    
    Args:
        gstin: Taxpayer GSTIN
        risk_level: HIGH_RISK, MEDIUM_RISK, or LOW_RISK
        risk_probability: Risk probability (0-1)
        top_drivers: List of top 3 feature contributions, each with keys:
                     - feature: feature name
                     - contribution: contribution value
                     - direction: 'positive' or 'negative'
        structural_patterns: Optional dict with pattern counts:
                            - circular_trade_count
                            - ghost_invoice_count
                            - spider_web_involvement
    
    Returns:
        Template-based narrative string
    """
    # Format risk probability as percentage
    risk_pct = f"{risk_probability * 100:.1f}%"
    
    # Build driver descriptions
    driver_descriptions = []
    for i, driver in enumerate(top_drivers[:3], 1):
        feature = driver.get('feature', 'unknown')
        contribution = driver.get('contribution', 0)
        direction = driver.get('direction', 'positive')
        
        # Format contribution as percentage
        contrib_pct = f"{abs(contribution) * 100:.1f}%"
        
        # Create human-readable feature name
        feature_readable = feature.replace('_', ' ').title()
        
        driver_descriptions.append(
            f"{feature_readable} ({contrib_pct} {direction} impact)"
        )
    
    drivers_text = ", ".join(driver_descriptions)
    
    # Build structural patterns summary
    patterns_text = ""
    if structural_patterns:
        pattern_parts = []
        
        circular_count = structural_patterns.get('circular_trade_count', 0)
        if circular_count > 0:
            pattern_parts.append(f"{circular_count} circular trade pattern(s)")
        
        ghost_count = structural_patterns.get('ghost_invoice_count', 0)
        if ghost_count > 0:
            pattern_parts.append(f"{ghost_count} ghost invoice(s)")
        
        spider_web = structural_patterns.get('spider_web_involvement', False)
        if spider_web:
            pattern_parts.append("spider web network involvement")
        
        if pattern_parts:
            patterns_text = f" Structural anomalies detected: {', '.join(pattern_parts)}."
    
    # Build narrative with risk level prefix
    if risk_level == "HIGH_RISK":
        narrative = (
            f"HIGH RISK — Entity {gstin} shows {risk_pct} fraud probability. "
            f"Key concerns: {drivers_text}.{patterns_text} "
            f"Immediate audit recommended."
        )
    elif risk_level == "MEDIUM_RISK":
        narrative = (
            f"MEDIUM RISK — Entity {gstin} shows {risk_pct} fraud probability. "
            f"Key concerns: {drivers_text}.{patterns_text} "
            f"Enhanced monitoring recommended."
        )
    else:  # LOW_RISK
        narrative = (
            f"LOW RISK — Entity {gstin} shows {risk_pct} fraud probability. "
            f"Primary factors: {drivers_text}.{patterns_text} "
            f"Standard compliance monitoring sufficient."
        )
    
    return narrative
