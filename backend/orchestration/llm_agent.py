"""
LangGraph Multi-Agent Workflow

This module implements the Project Niyati multi-agent orchestration workflow using LangGraph.
The workflow coordinates 5 specialized agents in a sequential pipeline with concurrent execution
for Agent 3 (Risk Detective) and Agent 4 (Predictive Analyst).

Workflow Flow:
1. Agent 1: Ingestion Wrangler (data validation and feature engineering)
2. Agent 2: Graph Architect (Neo4j knowledge graph construction)
3. Concurrent execution:
   - Agent 3: Risk Detective (structural pattern detection)
   - Agent 4: Predictive Analyst (ML risk scoring)
4. Agent 5: Niyati Explainer (narrative generation)
"""

import asyncio
import time
from typing import Dict, Any
from langgraph.graph import StateGraph, END

from orchestration.state import NiyatiState, create_initial_state
from orchestration.agent_ingestion_wrangler import (
    ingestion_wrangler_node_sync,
    set_event_queue as set_ingestion_event_queue
)
from orchestration.agent_graph_architect import (
    graph_architect_node_sync,
    set_event_queue as set_graph_event_queue
)
from orchestration.agent_risk_detective import (
    risk_detective_node_sync,
    set_event_queue as set_risk_event_queue
)
from orchestration.agent_predictive_analyst import (
    predictive_analyst_node_sync,
    set_event_queue as set_analyst_event_queue
)
from orchestration.agent_niyati_explainer import (
    niyati_explainer_node_sync,
    set_event_queue as set_explainer_event_queue
)


# Global event queue for SSE broadcasting
event_queue = None


def set_event_queue(queue):
    """
    Set the global event queue for SSE broadcasting.
    
    This queue is shared across all agents to broadcast progress messages.
    
    Args:
        queue: asyncio.Queue for SSE events
    """
    global event_queue
    event_queue = queue
    
    # Set event queue for all agents
    set_ingestion_event_queue(queue)
    set_graph_event_queue(queue)
    set_risk_event_queue(queue)
    set_analyst_event_queue(queue)
    set_explainer_event_queue(queue)


async def broadcast_event(message: str):
    """Broadcast an SSE event message."""
    if event_queue is not None:
        await event_queue.put(message)


def concurrent_analysis_node(state: NiyatiState) -> NiyatiState:
    """
    Concurrent Analysis Node
    
    This node runs Agent 3 (Risk Detective) and Agent 4 (Predictive Analyst)
    in parallel using asyncio.gather() for improved performance.
    
    Both agents can run independently since:
    - Agent 3 analyzes the Neo4j graph structure
    - Agent 4 analyzes the engineered features DataFrame
    
    Args:
        state: Current NiyatiState with graph_built=True and engineered_features
    
    Returns:
        Updated NiyatiState with structural_patterns and risk_predictions
    """
    async def run_concurrent():
        """Run both agents concurrently"""
        # Create tasks for both agents
        risk_detective_task = asyncio.create_task(
            asyncio.to_thread(risk_detective_node_sync, state)
        )
        
        predictive_analyst_task = asyncio.create_task(
            asyncio.to_thread(predictive_analyst_node_sync, state)
        )
        
        # Wait for both to complete
        results = await asyncio.gather(
            risk_detective_task,
            predictive_analyst_task,
            return_exceptions=True
        )
        
        # Check for exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_name = "Agent 3" if i == 0 else "Agent 4"
                error_msg = f"{agent_name} failed during concurrent execution: {str(result)}"
                state['errors'].append(error_msg)
                await broadcast_event(f"ERROR - {error_msg}")
        
        # Merge results from both agents
        # Agent 3 updates structural_patterns
        # Agent 4 updates risk_predictions and shape_plots
        if not isinstance(results[0], Exception):
            state['structural_patterns'] = results[0].get('structural_patterns', [])
        
        if not isinstance(results[1], Exception):
            state['risk_predictions'] = results[1].get('risk_predictions', {})
            state['shape_plots'] = results[1].get('shape_plots', {})
        
        return state
    
    # Run the concurrent execution
    return asyncio.run(run_concurrent())


def error_handling_node(state: NiyatiState) -> NiyatiState:
    """
    Error Handling Node
    
    This node is triggered when any agent fails. It performs cleanup operations
    including database rollback if necessary.
    
    Args:
        state: Current NiyatiState with errors
    
    Returns:
        Updated NiyatiState with error handling complete
    """
    errors = state.get('errors', [])
    
    if errors:
        # Log all errors
        for error in errors:
            print(f"ERROR: {error}")
        
        # TODO: Implement database rollback logic here
        # This would involve:
        # 1. Rolling back PostgreSQL transactions
        # 2. Optionally removing Neo4j nodes created in this workflow
        # 3. Cleaning up any partial state
        
        # For now, we just mark the workflow as failed
        asyncio.run(broadcast_event(f"Workflow failed with {len(errors)} error(s)"))
    
    return state


def should_continue(state: NiyatiState) -> str:
    """
    Conditional edge function to determine if workflow should continue or halt.
    
    Args:
        state: Current NiyatiState
    
    Returns:
        "error" if errors exist, "continue" otherwise
    """
    if state.get('errors'):
        return "error"
    return "continue"


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow with all 5 agents.
    
    The workflow follows this structure:
    1. Agent 1: Ingestion Wrangler
    2. Agent 2: Graph Architect
    3. Concurrent Node (Agent 3 + Agent 4 in parallel)
    4. Agent 5: Niyati Explainer
    5. Error Handling Node (if errors occur)
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create StateGraph with NiyatiState schema
    workflow = StateGraph(NiyatiState)
    
    # Add all agent nodes
    workflow.add_node("agent_1_ingestion_wrangler", ingestion_wrangler_node_sync)
    workflow.add_node("agent_2_graph_architect", graph_architect_node_sync)
    workflow.add_node("concurrent_analysis", concurrent_analysis_node)
    workflow.add_node("agent_5_niyati_explainer", niyati_explainer_node_sync)
    workflow.add_node("error_handler", error_handling_node)
    
    # Set entry point
    workflow.set_entry_point("agent_1_ingestion_wrangler")
    
    # Define sequential flow with error checking
    # Agent 1 -> Agent 2 (with error check)
    workflow.add_conditional_edges(
        "agent_1_ingestion_wrangler",
        should_continue,
        {
            "continue": "agent_2_graph_architect",
            "error": "error_handler"
        }
    )
    
    # Agent 2 -> Concurrent Analysis (with error check)
    workflow.add_conditional_edges(
        "agent_2_graph_architect",
        should_continue,
        {
            "continue": "concurrent_analysis",
            "error": "error_handler"
        }
    )
    
    # Concurrent Analysis -> Agent 5 (with error check)
    workflow.add_conditional_edges(
        "concurrent_analysis",
        should_continue,
        {
            "continue": "agent_5_niyati_explainer",
            "error": "error_handler"
        }
    )
    
    # Agent 5 -> END (with error check)
    workflow.add_conditional_edges(
        "agent_5_niyati_explainer",
        should_continue,
        {
            "continue": END,
            "error": "error_handler"
        }
    )
    
    # Error handler -> END
    workflow.add_edge("error_handler", END)
    
    # Compile the workflow
    return workflow.compile()


async def execute_workflow(csv_files: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the complete Project Niyati workflow.
    
    This function:
    1. Creates initial state from uploaded CSV files
    2. Broadcasts workflow start event
    3. Executes the LangGraph workflow
    4. Tracks execution time
    5. Broadcasts workflow completion event
    6. Returns workflow results
    
    Args:
        csv_files: Dictionary mapping CSV type names to pandas DataFrames
    
    Returns:
        Dictionary containing workflow results and summary
    """
    # Track execution time
    start_time = time.time()
    
    # Broadcast workflow start (Requirement 19.8)
    await broadcast_event("Workflow started")
    
    # Create initial state
    initial_state = create_initial_state(csv_files)
    
    # Create and execute workflow
    workflow = create_workflow()
    
    try:
        # Execute workflow (synchronous execution required by LangGraph)
        final_state = await asyncio.to_thread(workflow.invoke, initial_state)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Broadcast workflow completion (Requirement 19.9)
        await broadcast_event(f"Workflow completed in {execution_time:.1f}s")
        
        # Check for errors
        if final_state.get('errors'):
            return {
                'status': 'failed',
                'errors': final_state['errors'],
                'execution_time_seconds': execution_time
            }
        
        # Build summary response
        summary = {
            'status': 'success',
            'message': 'Workflow completed successfully',
            'summary': {
                'entities_processed': len(final_state.get('engineered_features', [])),
                'circular_trade_patterns': len([
                    p for p in final_state.get('structural_patterns', [])
                    if p.get('pattern_type') == 'circular_trade'
                ]),
                'ghost_invoice_entities': len([
                    p for p in final_state.get('structural_patterns', [])
                    if p.get('pattern_type') == 'ghost_invoice'
                ]),
                'spider_web_clusters': len([
                    p for p in final_state.get('structural_patterns', [])
                    if p.get('pattern_type') == 'spider_web'
                ]),
                'high_risk_entities': len([
                    pred for pred in final_state.get('risk_predictions', {}).values()
                    if pred.get('risk_level') == 'HIGH_RISK'
                ])
            },
            'execution_time_seconds': execution_time,
            'state': final_state
        }
        
        return summary
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Workflow execution failed: {str(e)}"
        
        await broadcast_event(f"ERROR - {error_msg}")
        
        return {
            'status': 'failed',
            'errors': [error_msg],
            'execution_time_seconds': execution_time
        }


def execute_workflow_sync(csv_files: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for execute_workflow.
    
    This allows the workflow to be called from synchronous contexts.
    
    Args:
        csv_files: Dictionary mapping CSV type names to pandas DataFrames
    
    Returns:
        Dictionary containing workflow results and summary
    """
    return asyncio.run(execute_workflow(csv_files))
