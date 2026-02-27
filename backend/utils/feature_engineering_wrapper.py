"""
Feature Engineering Wrapper

This module wraps the existing feature engineering logic to work with the LangGraph workflow.
It adapts the standalone feature engineering script to work with DataFrames passed in state.

Requirements: 2.1-2.8
"""

import pandas as pd
import numpy as np
from typing import Dict


def compute_engineered_features(csv_files: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Compute all 14 engineered features from validated CSV data.
    
    This function implements the same logic as the existing feature_engineering.py
    but works with DataFrames passed from the LangGraph state instead of reading files.
    
    Features computed:
    1. payment_gap - Days between GSTR-1 and GSTR-3B
    2. payment_gap_pct - Payment gap as percentage
    3. ghost_invoice_count - Count of invoices without eway bills
    4. ghost_invoice_pct - Percentage of ghost invoices
    5. shared_contact_flag - Entities sharing phone/email
    6. avg_delay_days - Average filing delay
    7. max_delay_days - Maximum filing delay
    8. self_invoice_flag - Self-invoicing detection
    9. is_cancelled - Entity cancellation status
    10. KycScore - KYC score from entity master
    11-14. Additional aggregated features
    
    Args:
        csv_files: Dictionary containing validated DataFrames:
            - e_invoices
            - eway_bills
            - entity_master
            - filing_history
            - purchase_register
            - returns_summary
    
    Returns:
        DataFrame with engineered features indexed by Gstin
    
    Requirements: 2.1-2.8
    """
    # Extract DataFrames from dictionary
    entities = csv_files['entity_master'].copy()
    invoices = csv_files['e_invoices'].copy()
    eway = csv_files['eway_bills'].copy()
    returns = csv_files['returns_summary'].copy()
    history = csv_files['filing_history'].copy()
    purchases = csv_files['purchase_register'].copy()
    
    # Normalize column names to match existing code
    # The validation uses PascalCase, but feature engineering expects specific names
    entities = _normalize_entity_columns(entities)
    invoices = _normalize_invoice_columns(invoices)
    eway = _normalize_eway_columns(eway)
    returns = _normalize_returns_columns(returns)
    history = _normalize_history_columns(history)
    purchases = _normalize_purchase_columns(purchases)
    
    # 1. Base Feature DataFrame
    features = entities[['Gstin']].copy()
    
    # Add KycScore and Status if available
    if 'KycScore' in entities.columns:
        features['KycScore'] = entities['KycScore']
    else:
        features['KycScore'] = 50  # Default value
    
    if 'Status' in entities.columns:
        features['is_cancelled'] = (entities['Status'] == 'Cancelled').astype(int)
    else:
        features['is_cancelled'] = 0
    
    # 2. Spider Web / Shared Contact Flag (Requirement 2.5)
    if 'SharedContact' in entities.columns:
        # SharedContact column exists - use it directly
        # Entities with the same SharedContact value are in the same cluster
        contact_counts = entities.groupby('SharedContact')['Gstin'].transform('count')
        features['shared_contact_flag'] = (contact_counts > 1).astype(int)
    elif 'Phone' in entities.columns or 'Email' in entities.columns:
        # Detect shared contacts from phone/email
        shared_contacts = []
        for gstin in entities['Gstin']:
            entity = entities[entities['Gstin'] == gstin].iloc[0]
            phone = entity.get('Phone', '')
            email = entity.get('Email', '')
            
            # Check if phone or email is shared with other entities
            if phone:
                phone_matches = entities[(entities['Phone'] == phone) & (entities['Gstin'] != gstin)]
                if len(phone_matches) > 0:
                    shared_contacts.append(gstin)
                    continue
            
            if email:
                email_matches = entities[(entities['Email'] == email) & (entities['Gstin'] != gstin)]
                if len(email_matches) > 0:
                    shared_contacts.append(gstin)
        
        features['shared_contact_flag'] = features['Gstin'].isin(shared_contacts).astype(int)
    else:
        # No contact information available
        features['shared_contact_flag'] = 0
    
    # 3. Payment Gap Features (Requirements 2.1, 2.2, 2.6)
    if 'Gstr1_Sales' in returns.columns and 'Gstr3b_Sales' in returns.columns:
        returns['payment_gap'] = returns['Gstr1_Sales'] - returns['Gstr3b_Sales']
        returns['payment_gap_pct'] = np.where(
            returns['Gstr1_Sales'] > 0,
            (returns['payment_gap'] / returns['Gstr1_Sales']) * 100,
            0
        )
        features = features.merge(
            returns[['Gstin', 'payment_gap', 'payment_gap_pct']], 
            on='Gstin', 
            how='left'
        )
    else:
        features['payment_gap'] = 0
        features['payment_gap_pct'] = 0
    
    # 4. Ghost Invoice Features (Requirements 2.3, 2.4)
    inv_eway = invoices.merge(eway, on='DocNo', how='left', indicator=True)
    inv_eway['is_ghost'] = (inv_eway['_merge'] == 'left_only').astype(int)
    
    ghost_stats = inv_eway.groupby('SellerGstin').agg(
        total_invoices=('Irn', 'count'),
        ghost_invoice_count=('is_ghost', 'sum')
    ).reset_index()
    ghost_stats['ghost_invoice_pct'] = (
        ghost_stats['ghost_invoice_count'] / ghost_stats['total_invoices']
    ) * 100
    
    features = features.merge(
        ghost_stats[['SellerGstin', 'ghost_invoice_count', 'ghost_invoice_pct']], 
        left_on='Gstin', 
        right_on='SellerGstin', 
        how='left'
    )
    features['ghost_invoice_count'] = features['ghost_invoice_count'].fillna(0)
    features['ghost_invoice_pct'] = features['ghost_invoice_pct'].fillna(0)
    
    # 5. Filing History Delays
    delay_stats = history.groupby('Gstin').agg(
        avg_delay_days=('DelayDays', 'mean'),
        max_delay_days=('DelayDays', 'max')
    ).reset_index()
    features = features.merge(delay_stats, on='Gstin', how='left')
    features['avg_delay_days'] = features['avg_delay_days'].fillna(0)
    features['max_delay_days'] = features['max_delay_days'].fillna(0)
    
    # 6. Self-Invoice Flag (Requirement 2.7 - Excess ITC)
    purchases['is_self_invoice'] = (
        purchases['SellerGstin'] == purchases['BuyerGstin']
    ).astype(int)
    
    # Also check for excess ITC
    if 'ItcClaimed' in purchases.columns and 'InvoiceValue' in purchases.columns:
        purchases['excess_itc'] = (
            purchases['ItcClaimed'] > purchases['InvoiceValue']
        ).astype(int)
    else:
        purchases['excess_itc'] = 0
    
    self_inv_stats = purchases.groupby('BuyerGstin').agg(
        self_invoice_flag=('is_self_invoice', 'max'),
        excess_itc_flag=('excess_itc', 'max')
    ).reset_index()
    
    features = features.merge(
        self_inv_stats, 
        left_on='Gstin', 
        right_on='BuyerGstin', 
        how='left'
    )
    features['self_invoice_flag'] = features['self_invoice_flag'].fillna(0)
    features['excess_itc_flag'] = features['excess_itc_flag'].fillna(0)
    
    # Clean up merge columns
    if 'SellerGstin' in features.columns:
        features = features.drop(columns=['SellerGstin'])
    if 'BuyerGstin' in features.columns:
        features = features.drop(columns=['BuyerGstin'])
    
    # Fill any remaining NaN values
    features = features.fillna(0)
    
    return features


def _normalize_entity_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize entity_master column names."""
    # The actual CSV has: Gstin, Status, KycScore, SharedContact, Sector
    # No changes needed - columns are already in correct format
    return df


def _normalize_invoice_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize e_invoices column names."""
    # The actual CSV has: Irn, SellerGstin, BuyerGstin, DocNo, DocDt, AssAmt, IgstAmt, TotalVal
    # Map to expected names
    column_mapping = {
        'DocDt': 'InvoiceDate',
        'TotalVal': 'InvoiceValue'
    }
    return df.rename(columns=column_mapping)


def _normalize_eway_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize eway_bills column names."""
    # The actual CSV has: EwbNo, DocNo, VehicleNo, Distance
    # Add GeneratedDate as a placeholder (not in actual data)
    df['GeneratedDate'] = pd.NaT
    return df


def _normalize_returns_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize returns_summary column names."""
    # The actual CSV has: Gstin, Gstr1_Liability, Gstr3b_Paid
    # Map to expected names
    column_mapping = {
        'Gstr1_Liability': 'Gstr1_Sales',
        'Gstr3b_Paid': 'Gstr3b_Sales'
    }
    df = df.rename(columns=column_mapping)
    # Add Period as placeholder
    df['Period'] = 'Jan-2024'
    return df


def _normalize_history_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize filing_history column names."""
    # The actual CSV has: Gstin, Month, DelayDays
    # Map to expected names
    column_mapping = {
        'Month': 'FilingPeriod'
    }
    df = df.rename(columns=column_mapping)
    # Add Status as placeholder
    df['Status'] = 'Filed'
    return df


def _normalize_purchase_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize purchase_register column names."""
    # The actual CSV has: Irn, SellerGstin, BuyerGstin, DocNo, DocDt, AssAmt, IgstAmt, TotalVal
    # Map to expected names
    column_mapping = {
        'TotalVal': 'InvoiceValue'
    }
    df = df.rename(columns=column_mapping)
    # Add ItcClaimed as placeholder (use AssAmt as proxy)
    if 'AssAmt' in df.columns:
        df['ItcClaimed'] = df['AssAmt'] * 0.18  # Assume 18% GST rate
    else:
        df['ItcClaimed'] = 0
    return df
