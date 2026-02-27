"""
CSV Validation Module

This module provides validation functions for the 6 types of GST CSV files:
- e_invoices.csv
- eway_bills.csv
- entity_master.csv
- filing_history.csv
- purchase_register.csv
- returns_summary.csv
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional


# Define required fields for each CSV type
# Note: These match the actual column names in the data files
REQUIRED_FIELDS = {
    'e_invoices': ['Irn', 'SellerGstin', 'BuyerGstin', 'DocNo', 'DocDt', 'TotalVal'],
    'eway_bills': ['DocNo', 'VehicleNo', 'Distance'],
    'entity_master': ['Gstin', 'Status', 'KycScore'],
    'filing_history': ['Gstin', 'Month', 'DelayDays'],
    'purchase_register': ['BuyerGstin', 'SellerGstin', 'DocNo', 'TotalVal'],
    'returns_summary': ['Gstin', 'Gstr1_Liability', 'Gstr3b_Paid']
}


def validate_csv_fields(
    df: pd.DataFrame, 
    csv_type: str
) -> Tuple[bool, Optional[Dict[str, List[int]]]]:
    """
    Validate that a CSV DataFrame contains all required fields.
    
    Args:
        df: The pandas DataFrame to validate
        csv_type: The type of CSV file (e.g., 'e_invoices', 'eway_bills')
    
    Returns:
        A tuple of (is_valid, error_details):
        - is_valid: True if all required fields are present, False otherwise
        - error_details: Dict with 'missing_fields' and 'rows_affected' if validation fails
    
    Examples:
        >>> df = pd.DataFrame({'Irn': ['123'], 'SellerGstin': ['ABC']})
        >>> validate_csv_fields(df, 'e_invoices')
        (False, {'missing_fields': ['BuyerGstin', 'InvoiceValue', 'InvoiceDate', 'DocNo'], 'rows_affected': []})
    """
    if csv_type not in REQUIRED_FIELDS:
        return False, {
            'missing_fields': [],
            'rows_affected': [],
            'error': f"Unknown CSV type: {csv_type}"
        }
    
    required = REQUIRED_FIELDS[csv_type]
    missing_fields = [field for field in required if field not in df.columns]
    
    if missing_fields:
        return False, {
            'missing_fields': missing_fields,
            'rows_affected': []
        }
    
    # Check for rows with missing required values
    rows_with_missing = []
    for field in required:
        null_rows = df[df[field].isna()].index.tolist()
        if null_rows:
            rows_with_missing.extend(null_rows)
    
    rows_with_missing = sorted(list(set(rows_with_missing)))
    
    if rows_with_missing:
        return False, {
            'missing_fields': [],
            'rows_affected': rows_with_missing
        }
    
    return True, None


def validate_all_csvs(
    csv_files: Dict[str, pd.DataFrame]
) -> Tuple[bool, Dict[str, any]]:
    """
    Validate all 6 CSV files.
    
    Args:
        csv_files: Dictionary mapping CSV type names to DataFrames
    
    Returns:
        A tuple of (all_valid, validation_results):
        - all_valid: True if all CSVs are valid, False otherwise
        - validation_results: Dict with validation status for each CSV
    
    Examples:
        >>> csvs = {
        ...     'e_invoices': pd.DataFrame({'Irn': ['123'], 'SellerGstin': ['ABC']}),
        ...     'eway_bills': pd.DataFrame({'DocNo': ['D1'], 'VehicleNo': ['V1']})
        ... }
        >>> validate_all_csvs(csvs)
        (False, {...})
    """
    validation_results = {}
    all_valid = True
    
    expected_types = ['e_invoices', 'eway_bills', 'entity_master', 
                      'filing_history', 'purchase_register', 'returns_summary']
    
    for csv_type in expected_types:
        if csv_type not in csv_files:
            validation_results[csv_type] = {
                'valid': False,
                'error': f"Missing CSV file: {csv_type}"
            }
            all_valid = False
            continue
        
        df = csv_files[csv_type]
        is_valid, error_details = validate_csv_fields(df, csv_type)
        
        if is_valid:
            validation_results[csv_type] = {
                'valid': True,
                'row_count': len(df)
            }
        else:
            validation_results[csv_type] = {
                'valid': False,
                'error_details': error_details
            }
            all_valid = False
    
    return all_valid, validation_results
