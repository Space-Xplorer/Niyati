"""
Agent 5: Niyati Explainer

This module implements the Niyati Explainer agent as a LangGraph node.
The agent generates plain-language audit narratives using LLM (Groq or OpenAI)
with circuit breaker protection and template-based fallback.

Requirements: 6.1-6.7, 13.1-13.7, 18.1-18.4, 19.7, 20.7
"""

import asyncio
import os
from typing import Dict, Any, List, Optional

from orchestration.state import NiyatiState
from utils.circuit_breaker import CircuitBreaker, generate_template_narrative


# Global event queue for SSE broadcasting (will be set by main app)
event_queue = None

# Global circuit breaker instance
circuit_breaker = CircuitBreaker(
    failure_threshold=int(os.getenv('CIRCUIT_BREAKER_THRESHOLD', 3)),
    recovery_timeout=60
)


def set_event_queue(queue):
    """Set the global event queue for SSE broadcasting."""
    global event_queue
    event_queue = queue


async def broadcast_event(message: str):
    """Broadcast an SSE event message."""
    if event_queue is not None:
        await event_queue.put(message)


def get_llm_client():
    """
    Get LLM client based on environment configuration.
    
    Returns:
        Tuple of (client, provider_name)
    
    Raises:
        ValueError: If LLM_PROVIDER is not supported or API key is missing
    
    Requirements: 13.1, 13.2, 13.3
    """
    llm_provider = os.getenv('LLM_PROVIDER', 'groq').lower()
    llm_api_key = os.getenv('LLM_API_KEY')
    
    if not llm_api_key or llm_api_key == 'your_groq_api_key_here':
        raise ValueError("LLM_API_KEY not configured in environment variables")
    
    if llm_provider == 'groq':
        try:
            from langchain_groq import ChatGroq
            client = ChatGroq(
                api_key=llm_api_key,
                model_name="llama-3-8b-8192",
                temperature=0.3,
                max_tokens=200
            )
            return client, 'Groq (Llama-3-8b)'
        except ImportError:
            raise ValueError("langchain-groq not installed. Run: pip install langchain-groq")
    
    elif llm_provider == 'openai':
        try:
            from langchain_openai import ChatOpenAI
            client = ChatOpenAI(
                api_key=llm_api_key,
                model_name="gpt-4o",
                temperature=0.3,
                max_tokens=200
            )
            return client, 'OpenAI (GPT-4o)'
        except ImportError:
            raise ValueError("langchain-openai not installed. Run: pip install langchain-openai")
    
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {llm_provider}. Use 'groq' or 'openai'")


def format_structured_prompt(
    gstin: str,
    risk_level: str,
    risk_probability: float,
    top_drivers: List[Dict[str, Any]],
    structural_patterns: Optional[Dict[str, Any]] = None
) -> str:
    """
    Format structured prompt for LLM narrative generation.
    
    Args:
        gstin: Taxpayer GSTIN
        risk_level: HIGH_RISK, MEDIUM_RISK, or LOW_RISK
        risk_probability: Risk probability (0-1)
        top_drivers: List of top 3 feature contributions
        structural_patterns: Optional dict with pattern counts
    
    Returns:
        Formatted prompt string
    
    Requirements: 13.4
    """
    # Format risk probability as percentage
    risk_pct = f"{risk_probability * 100:.1f}%"
    
    # Format top drivers with quantitative values
    drivers_text = ""
    for i, driver in enumerate(top_drivers[:3], 1):
        feature = driver.get('feature_name', 'unknown')
        contribution = driver.get('contribution_value', 0)
        direction = driver.get('direction', 'positive')
        
        # Format contribution as percentage
        contrib_pct = f"{abs(contribution) * 100:.1f}%"
        
        # Create human-readable feature name
        feature_readable = feature.replace('_', ' ').title()
        
        drivers_text += f"{i}. {feature_readable}: {contrib_pct} contribution ({direction} impact)\n"
    
    # Format structural patterns
    patterns_text = "None detected"
    if structural_patterns:
        pattern_parts = []
        
        circular_count = structural_patterns.get('circular_trade_count', 0)
        if circular_count > 0:
            pattern_parts.append(f"- {circular_count} circular trade pattern(s)")
        
        ghost_count = structural_patterns.get('ghost_invoice_count', 0)
        if ghost_count > 0:
            pattern_parts.append(f"- {ghost_count} ghost invoice(s)")
        
        spider_web = structural_patterns.get('spider_web_involvement', False)
        if spider_web:
            pattern_parts.append(f"- Spider web network involvement detected")
        
        if pattern_parts:
            patterns_text = "\n".join(pattern_parts)
    
    # Build prompt
    prompt = f"""You are an expert GST auditor. Generate a concise audit narrative for the following entity:

GSTIN: {gstin}
Risk Level: {risk_level}
Risk Probability: {risk_pct}

Top Risk Drivers:
{drivers_text}

Structural Patterns Detected:
{patterns_text}

Generate a 2-3 sentence narrative explaining the risk in plain language suitable for non-technical auditors. 
If the risk level is HIGH_RISK, start with "HIGH RISK —". 
Include quantitative values from the top drivers to support your assessment.
Be specific and actionable."""
    
    return prompt


def call_llm_with_circuit_breaker(
    llm_client,
    prompt: str
) -> str:
    """
    Call LLM API with circuit breaker protection.
    
    Args:
        llm_client: LangChain LLM client
        prompt: Formatted prompt string
    
    Returns:
        Generated narrative text
    
    Raises:
        Exception: If LLM call fails or circuit breaker is open
    
    Requirements: 18.1, 18.2
    """
    def _call_llm():
        """Inner function for circuit breaker to wrap"""
        response = llm_client.invoke(prompt)
        
        # Extract text from response
        if hasattr(response, 'content'):
            return response.content
        elif isinstance(response, str):
            return response
        else:
            return str(response)
    
    # Call with circuit breaker protection
    return circuit_breaker.call(_call_llm)


def validate_narrative(narrative: str) -> bool:
    """
    Validate LLM-generated narrative meets minimum requirements.
    
    Args:
        narrative: Generated narrative text
    
    Returns:
        True if valid, False otherwise
    
    Requirements: 13.5
    """
    if not narrative or not isinstance(narrative, str):
        return False
    
    # Must be at least 50 characters
    if len(narrative.strip()) < 50:
        return False
    
    return True


def ensure_high_risk_prefix(narrative: str, risk_level: str) -> str:
    """
    Ensure HIGH_RISK narratives start with "HIGH RISK —" prefix.
    
    Args:
        narrative: Generated narrative text
        risk_level: Risk level classification
    
    Returns:
        Narrative with correct prefix
    
    Requirements: 6.6
    """
    if risk_level == 'HIGH_RISK':
        # Check if it already starts with the prefix
        if not narrative.strip().startswith('HIGH RISK'):
            # Add the prefix
            narrative = f"HIGH RISK — {narrative.strip()}"
    
    return narrative


async def generate_narrative_for_entity(
    gstin: str,
    risk_prediction: Dict[str, Any],
    structural_patterns: Optional[Dict[str, Any]],
    llm_client,
    llm_provider_name: str
) -> str:
    """
    Generate audit narrative for a single entity.
    
    Args:
        gstin: Taxpayer GSTIN
        risk_prediction: Risk prediction data from Agent 4
        structural_patterns: Structural pattern data from Agent 3
        llm_client: LangChain LLM client
        llm_provider_name: Name of LLM provider for logging
    
    Returns:
        Generated narrative text
    
    Requirements: 6.1-6.7, 13.4-13.6, 18.1-18.4
    """
    risk_level = risk_prediction.get('risk_level', 'LOW_RISK')
    risk_probability = risk_prediction.get('risk_probability', 0.0)
    top_drivers = risk_prediction.get('top_drivers', [])
    
    # Format structured prompt (Requirement 13.4)
    prompt = format_structured_prompt(
        gstin=gstin,
        risk_level=risk_level,
        risk_probability=risk_probability,
        top_drivers=top_drivers,
        structural_patterns=structural_patterns
    )
    
    narrative = None
    used_fallback = False
    
    try:
        # Try to call LLM with circuit breaker (Requirements 18.1, 18.2)
        narrative = call_llm_with_circuit_breaker(llm_client, prompt)
        
        # Validate response (Requirement 13.5)
        if not validate_narrative(narrative):
            raise ValueError("LLM response validation failed (< 50 characters)")
        
    except Exception as e:
        # Fall back to template (Requirements 13.6, 18.3)
        used_fallback = True
        
        # Convert top_drivers format for template function
        template_drivers = [
            {
                'feature': driver.get('feature_name', 'unknown'),
                'contribution': driver.get('contribution_value', 0),
                'direction': driver.get('direction', 'positive')
            }
            for driver in top_drivers
        ]
        
        narrative = generate_template_narrative(
            gstin=gstin,
            risk_level=risk_level,
            risk_probability=risk_probability,
            top_drivers=template_drivers,
            structural_patterns=structural_patterns
        )
    
    # Ensure HIGH_RISK prefix (Requirement 6.6)
    narrative = ensure_high_risk_prefix(narrative, risk_level)
    
    return narrative


async def niyati_explainer_node(state: NiyatiState) -> NiyatiState:
    """
    Niyati Explainer LangGraph Node
    
    This agent performs the following tasks:
    1. Initializes LLM client (Groq or OpenAI) based on environment
    2. For each entity with risk predictions:
       - Formats structured prompt with risk data and patterns
       - Calls LLM API with circuit breaker protection
       - Validates response (>= 50 characters)
       - Falls back to template if LLM fails
       - Ensures HIGH_RISK narratives have correct prefix
       - Includes quantitative values for top drivers
    3. Broadcasts SSE progress messages
    4. Updates state with generated narratives
    
    Args:
        state: Current NiyatiState containing risk_predictions and structural_patterns
    
    Returns:
        Updated NiyatiState with narratives
    
    Requirements: 6.1-6.7, 13.1-13.7, 18.1-18.4, 19.7, 20.7
    """
    try:
        risk_predictions = state.get('risk_predictions', {})
        structural_patterns = state.get('structural_patterns', [])
        
        if not risk_predictions:
            error_msg = "Agent 5 failed: No risk predictions available"
            await broadcast_event(f"Agent 5: ERROR - {error_msg}")
            state['errors'].append(error_msg)
            return state
        
        entity_count = len(risk_predictions)
        
        # Step 1: Initialize LLM client (Requirements 13.1, 13.2, 13.3)
        try:
            llm_client, llm_provider_name = get_llm_client()
            await broadcast_event(f"Agent 5: Generating audit narratives using {llm_provider_name}")
        except ValueError as e:
            # If LLM not configured, use template fallback for all
            await broadcast_event(f"Agent 5: LLM not configured, using template fallback - {str(e)}")
            llm_client = None
            llm_provider_name = "Template Fallback"
        
        # Step 2: Aggregate structural patterns by GSTIN
        patterns_by_gstin = {}
        
        for pattern in structural_patterns:
            pattern_type = pattern.get('pattern_type', '')
            gstin_list = pattern.get('gstin_list', [])
            
            for gstin in gstin_list:
                if gstin not in patterns_by_gstin:
                    patterns_by_gstin[gstin] = {
                        'circular_trade_count': 0,
                        'ghost_invoice_count': 0,
                        'spider_web_involvement': False
                    }
                
                if pattern_type == 'circular_trade':
                    patterns_by_gstin[gstin]['circular_trade_count'] += 1
                elif pattern_type == 'ghost_invoice':
                    patterns_by_gstin[gstin]['ghost_invoice_count'] += pattern.get('count', 1)
                elif pattern_type == 'spider_web':
                    patterns_by_gstin[gstin]['spider_web_involvement'] = True
        
        # Step 3: Generate narratives for each entity
        narratives = {}
        high_risk_count = 0
        
        for gstin, risk_prediction in risk_predictions.items():
            risk_level = risk_prediction.get('risk_level', 'LOW_RISK')
            
            if risk_level == 'HIGH_RISK':
                high_risk_count += 1
            
            # Get structural patterns for this GSTIN
            entity_patterns = patterns_by_gstin.get(gstin, None)
            
            # Generate narrative
            if llm_client is not None:
                narrative = await generate_narrative_for_entity(
                    gstin=gstin,
                    risk_prediction=risk_prediction,
                    structural_patterns=entity_patterns,
                    llm_client=llm_client,
                    llm_provider_name=llm_provider_name
                )
            else:
                # Use template fallback if no LLM client
                template_drivers = [
                    {
                        'feature': driver.get('feature_name', 'unknown'),
                        'contribution': driver.get('contribution_value', 0),
                        'direction': driver.get('direction', 'positive')
                    }
                    for driver in risk_prediction.get('top_drivers', [])
                ]
                
                narrative = generate_template_narrative(
                    gstin=gstin,
                    risk_level=risk_level,
                    risk_probability=risk_prediction.get('risk_probability', 0.0),
                    top_drivers=template_drivers,
                    structural_patterns=entity_patterns
                )
            
            narratives[gstin] = narrative
        
        # Step 4: Update state (Requirement 6.7)
        state['narratives'] = narratives
        
        # Step 5: Broadcast completion (Requirement 19.7)
        await broadcast_event(
            f"Agent 5: Generated {entity_count} audit narratives "
            f"({high_risk_count} HIGH_RISK entities)"
        )
        
        return state
        
    except Exception as e:
        error_msg = f"Agent 5 failed: {str(e)}"
        await broadcast_event(f"Agent 5: ERROR - {error_msg}")
        state['errors'].append(error_msg)
        return state


def niyati_explainer_node_sync(state: NiyatiState) -> NiyatiState:
    """
    Synchronous wrapper for the Niyati Explainer node.
    
    LangGraph requires synchronous node functions, so this wrapper
    runs the async implementation using asyncio.run().
    
    Args:
        state: Current NiyatiState
    
    Returns:
        Updated NiyatiState
    """
    return asyncio.run(niyati_explainer_node(state))
