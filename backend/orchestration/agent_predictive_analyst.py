"""
Agent 4: Predictive Analyst

This module implements the Predictive Analyst agent as a LangGraph node.
The agent loads the trained EBM model, runs inference on engineered features,
extracts feature contributions, and classifies risk levels.
"""

import asyncio
import os
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
import joblib
from interpret.glassbox import ExplainableBoostingClassifier

from orchestration.state import NiyatiState


# Global event queue for SSE broadcasting (will be set by main app)
event_queue = None

# Cache for loaded model
_model_cache = None


def set_event_queue(queue):
    """Set the global event queue for SSE broadcasting."""
    global event_queue
    event_queue = queue


async def broadcast_event(message: str):
    """Broadcast an SSE event message."""
    if event_queue is not None:
        await event_queue.put(message)


def load_ebm_model() -> ExplainableBoostingClassifier:
    """
    Load the trained EBM model from disk.
    
    Uses caching to avoid reloading the model on every request.
    
    Returns:
        Loaded ExplainableBoostingClassifier model
    
    Raises:
        FileNotFoundError: If model file doesn't exist
        Exception: If model loading fails
    """
    global _model_cache
    
    if _model_cache is not None:
        return _model_cache
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    model_path = os.path.join(backend_dir, 'model', 'daksha_ebm.pkl')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"EBM model not found at {model_path}")
    
    try:
        _model_cache = joblib.load(model_path)
        return _model_cache
    except Exception as e:
        raise Exception(f"Failed to load EBM model: {str(e)}")


def classify_risk_level(probability: float) -> str:
    """
    Classify risk level based on probability threshold.
    
    Args:
        probability: Risk probability between 0 and 1
    
    Returns:
        Risk level: 'HIGH_RISK', 'MEDIUM_RISK', or 'LOW_RISK'
    """
    if probability >= 0.7:
        return 'HIGH_RISK'
    elif probability >= 0.4:
        return 'MEDIUM_RISK'
    else:
        return 'LOW_RISK'


def extract_top_drivers(
    ebm_model: ExplainableBoostingClassifier,
    features_df: pd.DataFrame,
    gstin: str,
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Extract top N feature contributions for a specific GSTIN using EBM's explain_local.
    
    Args:
        ebm_model: Trained EBM model
        features_df: DataFrame with engineered features
        gstin: GSTIN to explain
        top_n: Number of top drivers to extract (default: 3)
    
    Returns:
        List of dictionaries with feature_name, contribution_value, direction
    """
    # Get the row for this GSTIN
    entity_row = features_df[features_df['Gstin'] == gstin]
    
    if entity_row.empty:
        return []
    
    # Prepare features (exclude Gstin and fraud_label if present)
    feature_cols = [col for col in features_df.columns if col not in ['Gstin', 'fraud_label']]
    X = entity_row[feature_cols]
    
    # Get local explanation
    local_explanation = ebm_model.explain_local(X)
    
    # Extract feature contributions
    # local_explanation.data() returns a dict with 'scores' containing contribution values
    contributions = []
    
    if hasattr(local_explanation, 'data'):
        explanation_data = local_explanation.data(0)  # Get first (and only) instance
        
        if 'scores' in explanation_data:
            scores = explanation_data['scores']
            feature_names = explanation_data.get('names', feature_cols)
            
            # Create list of (feature_name, contribution_value) tuples
            for i, (name, score) in enumerate(zip(feature_names, scores)):
                contributions.append({
                    'feature_name': name,
                    'contribution_value': float(score),
                    'direction': 'positive' if score > 0 else 'negative'
                })
    
    # Sort by absolute contribution value and take top N
    contributions.sort(key=lambda x: abs(x['contribution_value']), reverse=True)
    
    return contributions[:top_n]


def extract_shape_plot_data(
    ebm_model: ExplainableBoostingClassifier,
    features_df: pd.DataFrame,
    gstin: str,
    top_n: int = 3
) -> Dict[str, Any]:
    """
    Extract shape plot data for visualization of top feature contributions.
    
    Shape plots show how each feature value contributes to the risk score
    compared to the baseline.
    
    Args:
        ebm_model: Trained EBM model
        features_df: DataFrame with engineered features
        gstin: GSTIN to explain
        top_n: Number of top features to extract shape plots for
    
    Returns:
        Dictionary mapping feature names to shape plot data
    """
    shape_plots = {}
    
    # Get the row for this GSTIN
    entity_row = features_df[features_df['Gstin'] == gstin]
    
    if entity_row.empty:
        return shape_plots
    
    # Prepare features
    feature_cols = [col for col in features_df.columns if col not in ['Gstin', 'fraud_label']]
    X = entity_row[feature_cols]
    
    # Get local explanation
    local_explanation = ebm_model.explain_local(X)
    
    # Get top drivers to know which features to extract shape plots for
    top_drivers = extract_top_drivers(ebm_model, features_df, gstin, top_n)
    
    if not top_drivers:
        return shape_plots
    
    # Extract shape plot data for each top driver
    for driver in top_drivers:
        feature_name = driver['feature_name']
        
        try:
            # Get feature index
            feature_idx = feature_cols.index(feature_name)
            
            # Get the feature value for this entity
            feature_value = float(X.iloc[0, feature_idx])
            
            # Get global explanation for this feature
            global_explanation = ebm_model.explain_global()
            
            if hasattr(global_explanation, 'data'):
                global_data = global_explanation.data(feature_idx)
                
                # Extract shape function data
                x_values = global_data.get('names', [])  # Feature value bins
                y_values = global_data.get('scores', [])  # Contribution scores
                
                # Get baseline (intercept)
                baseline_value = 0.0
                if hasattr(ebm_model, 'intercept_'):
                    baseline_value = float(ebm_model.intercept_[0] if isinstance(ebm_model.intercept_, np.ndarray) else ebm_model.intercept_)
                
                shape_plots[feature_name] = {
                    'feature_name': feature_name,
                    'contribution_weight': driver['contribution_value'],
                    'feature_value': feature_value,
                    'baseline_value': baseline_value,
                    'x_values': [float(x) if isinstance(x, (int, float, np.number)) else str(x) for x in x_values],
                    'y_values': [float(y) for y in y_values]
                }
        
        except Exception as e:
            # If shape plot extraction fails for this feature, skip it
            print(f"Warning: Could not extract shape plot for {feature_name}: {str(e)}")
            continue
    
    return shape_plots


async def predictive_analyst_node(state: NiyatiState) -> NiyatiState:
    """
    Predictive Analyst LangGraph Node
    
    This agent performs the following tasks:
    1. Loads the trained EBM model from disk
    2. Runs inference on engineered features
    3. Extracts top 3 feature contributions for each entity
    4. Extracts shape plot data for visualization
    5. Classifies risk levels (HIGH_RISK, MEDIUM_RISK, LOW_RISK)
    6. Broadcasts SSE progress messages
    7. Updates state with risk predictions and shape plots
    
    Args:
        state: Current NiyatiState containing engineered_features
    
    Returns:
        Updated NiyatiState with risk_predictions and shape_plots
    """
    try:
        engineered_features = state.get('engineered_features')
        
        if engineered_features is None or engineered_features.empty:
            error_msg = "Agent 4 failed: No engineered features available"
            await broadcast_event(f"Agent 4: ERROR - {error_msg}")
            state['errors'].append(error_msg)
            return state
        
        gstin_count = len(engineered_features)
        
        # Step 1: Load EBM model (Requirements 5.1, 5.2)
        await broadcast_event(f"Agent 4: Loading EBM model...")
        
        try:
            ebm_model = load_ebm_model()
        except Exception as e:
            error_msg = f"Agent 4 failed to load model: {str(e)}"
            await broadcast_event(f"Agent 4: ERROR - {error_msg}")
            state['errors'].append(error_msg)
            return state
        
        # Step 2: Prepare features for inference
        await broadcast_event(f"Agent 4: Computing risk scores for {gstin_count} entities")
        
        # Get feature columns (exclude Gstin and fraud_label if present)
        feature_cols = [col for col in engineered_features.columns if col not in ['Gstin', 'fraud_label']]
        X = engineered_features[feature_cols]
        
        # Step 3: Run EBM inference (Requirement 5.3)
        risk_probabilities = ebm_model.predict_proba(X)[:, 1]
        
        # Validate probabilities are between 0 and 1 (Requirement 5.3)
        if not all(0 <= p <= 1 for p in risk_probabilities):
            error_msg = "Agent 4 failed: Risk probabilities out of bounds [0, 1]"
            await broadcast_event(f"Agent 4: ERROR - {error_msg}")
            state['errors'].append(error_msg)
            return state
        
        # Step 4: Process each entity
        risk_predictions = {}
        shape_plots = {}
        
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        
        for idx, row in engineered_features.iterrows():
            gstin = row['Gstin']
            risk_prob = float(risk_probabilities[idx])
            
            # Classify risk level (Requirements 5.6, 5.7, 5.8)
            risk_level = classify_risk_level(risk_prob)
            
            # Count risk levels
            if risk_level == 'HIGH_RISK':
                high_risk_count += 1
            elif risk_level == 'MEDIUM_RISK':
                medium_risk_count += 1
            else:
                low_risk_count += 1
            
            # Extract top 3 drivers (Requirements 5.4, 5.5)
            top_drivers = extract_top_drivers(ebm_model, engineered_features, gstin, top_n=3)
            
            # Extract shape plot data (Requirements 20.1, 20.2, 20.3)
            entity_shape_plots = extract_shape_plot_data(ebm_model, engineered_features, gstin, top_n=3)
            
            # Store predictions
            risk_predictions[gstin] = {
                'gstin': gstin,
                'risk_probability': risk_prob,
                'risk_level': risk_level,
                'top_drivers': top_drivers
            }
            
            # Store shape plots
            if entity_shape_plots:
                shape_plots[gstin] = entity_shape_plots
        
        # Step 5: Update state
        state['risk_predictions'] = risk_predictions
        state['shape_plots'] = shape_plots
        
        # Step 6: Broadcast completion
        await broadcast_event(
            f"Agent 4: Risk scoring complete - {high_risk_count} HIGH_RISK, "
            f"{medium_risk_count} MEDIUM_RISK, {low_risk_count} LOW_RISK"
        )
        
        return state
        
    except Exception as e:
        error_msg = f"Agent 4 failed: {str(e)}"
        await broadcast_event(f"Agent 4: ERROR - {error_msg}")
        state['errors'].append(error_msg)
        return state


def predictive_analyst_node_sync(state: NiyatiState) -> NiyatiState:
    """
    Synchronous wrapper for the Predictive Analyst node.
    
    LangGraph requires synchronous node functions, so this wrapper
    runs the async implementation using asyncio.run().
    
    Args:
        state: Current NiyatiState
    
    Returns:
        Updated NiyatiState
    """
    return asyncio.run(predictive_analyst_node(state))
