"""
LangGraph State Schema

This module defines the state schema for the Project Niyati multi-agent workflow.
The state is passed between agents and tracks the progress of data through the pipeline.

Requirements: 7.1
"""

from typing import TypedDict, Dict, List, Any, Optional
import pandas as pd


class NiyatiState(TypedDict):
    """
    State schema for the Project Niyati LangGraph workflow.
    
    This state is passed between all 5 agents:
    1. Ingestion Wrangler
    2. Graph Architect
    3. Risk Detective
    4. Predictive Analyst
    5. Niyati Explainer
    
    Attributes:
        csv_files: Dictionary mapping CSV type names to pandas DataFrames
        validated_data: Dictionary of validated DataFrames after cleaning
        engineered_features: DataFrame containing computed fraud detection features
        change_summary: Dictionary containing change detection results (new, updated, unchanged counts)
        graph_built: Boolean flag indicating if Neo4j graph construction is complete
        structural_patterns: List of detected fraud patterns (circular trade, ghost invoices, spider webs)
        risk_predictions: Dictionary containing ML risk scores and feature contributions
        shape_plots: Dictionary containing EBM shape plot data for visualization
        narratives: Dictionary mapping GSTINs to generated audit narratives
        errors: List of error messages encountered during workflow execution
    """
    csv_files: Dict[str, pd.DataFrame]
    validated_data: Dict[str, pd.DataFrame]
    engineered_features: Optional[pd.DataFrame]
    change_summary: Optional[Dict[str, Any]]
    graph_built: bool
    structural_patterns: List[Dict[str, Any]]
    risk_predictions: Dict[str, Any]
    shape_plots: Dict[str, Any]
    narratives: Dict[str, str]
    errors: List[str]


def create_initial_state(csv_files: Dict[str, pd.DataFrame]) -> NiyatiState:
    """
    Create an initial state for the workflow with uploaded CSV files.
    
    Args:
        csv_files: Dictionary mapping CSV type names to DataFrames
    
    Returns:
        A NiyatiState dictionary with initial values
    """
    return NiyatiState(
        csv_files=csv_files,
        validated_data={},
        engineered_features=None,
        change_summary=None,
        graph_built=False,
        structural_patterns=[],
        risk_predictions={},
        shape_plots={},
        narratives={},
        errors=[]
    )
