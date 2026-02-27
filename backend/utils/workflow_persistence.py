"""
Workflow Persistence Module

This module provides functions to persist workflow results to the SQLite database.
It saves data from the NiyatiState to the appropriate database tables.

Requirements: Database persistence for workflow results
"""

from typing import Dict, Any
import pandas as pd
from datetime import datetime

from database import db
from models import (
    RawInvoice, RawEwayBill, EntityMaster,
    EngineeredFeatures, RiskPrediction, FraudPattern,
    AuditNarrative, ShapePlot
)


def persist_raw_data(csv_files: Dict[str, pd.DataFrame], flask_app) -> None:
    """
    Persist raw CSV data to database tables.
    
    Args:
        csv_files: Dictionary mapping CSV type names to DataFrames
        flask_app: Flask application context
    """
    with flask_app.app_context():
        # Persist e-invoices
        if 'e_invoices' in csv_files:
            for _, row in csv_files['e_invoices'].iterrows():
                invoice = RawInvoice(
                    irn=str(row['Irn']),
                    seller_gstin=str(row['SellerGstin']),
                    buyer_gstin=str(row['BuyerGstin']),
                    doc_no=str(row['DocNo']),
                    invoice_date=str(row['DocDt']),  # Note: model uses invoice_date
                    invoice_value=float(row['TotalVal'])  # Note: model uses invoice_value
                )
                db.session.merge(invoice)
        
        # Persist e-way bills
        if 'eway_bills' in csv_files:
            for _, row in csv_files['eway_bills'].iterrows():
                # RawEwayBill requires generated_date, use current date if not available
                from datetime import date
                eway_bill = RawEwayBill(
                    doc_no=str(row['DocNo']),
                    vehicle_no=str(row.get('VehicleNo', '')),
                    distance=int(row.get('Distance', 0)) if pd.notna(row.get('Distance')) else 0,
                    generated_date=date.today()  # Use today's date as placeholder
                )
                db.session.merge(eway_bill)
        
        # Persist entity master
        if 'entity_master' in csv_files:
            for _, row in csv_files['entity_master'].iterrows():
                entity = EntityMaster(
                    gstin=str(row['Gstin']),
                    business_name=str(row.get('Status', 'Unknown')),  # Map Status to business_name
                    phone=str(row.get('SharedContact', '')) if pd.notna(row.get('SharedContact')) else None,
                    email='',  # Not available in test data
                    address=str(row.get('Sector', '')) if pd.notna(row.get('Sector')) else None
                )
                db.session.merge(entity)
        
        # Note: filing_history, purchase_register, and returns_summary tables
        # are not defined in models.py, so we skip persisting them for now.
        # They are used for feature engineering but not stored separately.
        
        db.session.commit()


def persist_engineered_features(engineered_features: pd.DataFrame, flask_app) -> None:
    """
    Persist engineered features to database.
    
    Args:
        engineered_features: DataFrame with engineered features
        flask_app: Flask application context
    """
    if engineered_features is None or engineered_features.empty:
        return
    
    with flask_app.app_context():
        for _, row in engineered_features.iterrows():
            features = EngineeredFeatures(
                gstin=str(row['Gstin']),
                # Add all feature columns dynamically
                **{col: float(row[col]) if pd.notna(row[col]) else 0.0 
                   for col in engineered_features.columns if col != 'Gstin'}
            )
            db.session.merge(features)
        
        db.session.commit()


def persist_risk_predictions(risk_predictions: Dict[str, Any], flask_app) -> None:
    """
    Persist risk predictions to database.
    
    Args:
        risk_predictions: Dictionary mapping GSTINs to risk prediction data
        flask_app: Flask application context
    """
    if not risk_predictions:
        return
    
    with flask_app.app_context():
        for gstin, prediction in risk_predictions.items():
            top_drivers = prediction.get('top_drivers', [])
            
            risk_pred = RiskPrediction(
                gstin=gstin,
                risk_probability=float(prediction.get('risk_probability', 0.0)),
                risk_level=str(prediction.get('risk_level', 'LOW_RISK')),
                top_driver_1=top_drivers[0].get('feature_name', '') if len(top_drivers) > 0 else None,
                top_driver_1_contribution=float(top_drivers[0].get('contribution_value', 0)) if len(top_drivers) > 0 else None,
                top_driver_2=top_drivers[1].get('feature_name', '') if len(top_drivers) > 1 else None,
                top_driver_2_contribution=float(top_drivers[1].get('contribution_value', 0)) if len(top_drivers) > 1 else None,
                top_driver_3=top_drivers[2].get('feature_name', '') if len(top_drivers) > 2 else None,
                top_driver_3_contribution=float(top_drivers[2].get('contribution_value', 0)) if len(top_drivers) > 2 else None
            )
            db.session.merge(risk_pred)
        
        db.session.commit()


def persist_fraud_patterns(structural_patterns: list, flask_app) -> None:
    """
    Persist fraud patterns to database.
    
    Args:
        structural_patterns: List of detected fraud patterns
        flask_app: Flask application context
    """
    if not structural_patterns:
        return
    
    with flask_app.app_context():
        for pattern in structural_patterns:
            pattern_type = pattern.get('pattern_type', '')
            gstin_list = pattern.get('gstin_list', [])
            
            # Create a pattern record for each GSTIN involved
            for gstin in gstin_list:
                # Build pattern metadata
                pattern_metadata = {
                    'all_gstins': gstin_list,
                    'risk_score': float(pattern.get('risk_score', 0.0))
                }
                
                # Add pattern-specific fields to metadata
                if pattern_type == 'circular_trade':
                    pattern_metadata['loop_length'] = pattern.get('loop_length')
                    pattern_metadata['total_value'] = float(pattern.get('total_value', 0))
                elif pattern_type == 'ghost_invoice':
                    pattern_metadata['ghost_count'] = pattern.get('ghost_count')
                    pattern_metadata['ghost_value'] = float(pattern.get('ghost_value', 0))
                elif pattern_type == 'spider_web':
                    pattern_metadata['cluster_size'] = pattern.get('cluster_size')
                    pattern_metadata['transaction_volume'] = float(pattern.get('transaction_volume', 0))
                
                fraud_pattern = FraudPattern(
                    gstin=gstin,
                    pattern_type=pattern_type,
                    risk_score=float(pattern.get('risk_score', 0.0)),
                    gstin_list=gstin_list,  # Store as JSON array
                    pattern_metadata=pattern_metadata
                )
                db.session.merge(fraud_pattern)
        
        db.session.commit()


def persist_narratives(narratives: Dict[str, str], flask_app) -> None:
    """
    Persist audit narratives to database.
    
    Args:
        narratives: Dictionary mapping GSTINs to narrative text
        flask_app: Flask application context
    """
    if not narratives:
        return
    
    with flask_app.app_context():
        for gstin, narrative_text in narratives.items():
            narrative = AuditNarrative(
                gstin=gstin,
                narrative_text=narrative_text
            )
            db.session.merge(narrative)
        
        db.session.commit()


def persist_shape_plots(shape_plots: Dict[str, Any], flask_app) -> None:
    """
    Persist shape plot data to database.
    
    Args:
        shape_plots: Dictionary mapping GSTINs to shape plot data
        flask_app: Flask application context
    """
    if not shape_plots:
        return
    
    with flask_app.app_context():
        for gstin, plots in shape_plots.items():
            for feature_name, plot_data in plots.items():
                shape_plot = ShapePlot(
                    gstin=gstin,
                    feature_name=feature_name,
                    contribution_weight=float(plot_data.get('contribution_weight', 0.0)),
                    feature_value=float(plot_data.get('feature_value', 0.0)),
                    baseline_value=float(plot_data.get('baseline_value', 0.0)),
                    x_values=str(plot_data.get('x_values', [])),
                    y_values=str(plot_data.get('y_values', []))
                )
                db.session.merge(shape_plot)
        
        db.session.commit()


def persist_workflow_results(workflow_result: Dict[str, Any], flask_app) -> None:
    """
    Persist all workflow results to database.
    
    This is the main function that orchestrates persistence of all workflow outputs.
    
    Args:
        workflow_result: Complete workflow result dictionary
        flask_app: Flask application context
    """
    if workflow_result.get('status') != 'success':
        return
    
    state = workflow_result.get('state', {})
    
    # Persist raw data
    csv_files = state.get('validated_data', {})
    if csv_files:
        persist_raw_data(csv_files, flask_app)
    
    # Persist engineered features
    engineered_features = state.get('engineered_features')
    if engineered_features is not None:
        persist_engineered_features(engineered_features, flask_app)
    
    # Persist risk predictions
    risk_predictions = state.get('risk_predictions', {})
    if risk_predictions:
        persist_risk_predictions(risk_predictions, flask_app)
    
    # Persist fraud patterns
    structural_patterns = state.get('structural_patterns', [])
    if structural_patterns:
        persist_fraud_patterns(structural_patterns, flask_app)
    
    # Persist narratives
    narratives = state.get('narratives', {})
    if narratives:
        persist_narratives(narratives, flask_app)
    
    # Persist shape plots
    shape_plots = state.get('shape_plots', {})
    if shape_plots:
        persist_shape_plots(shape_plots, flask_app)
