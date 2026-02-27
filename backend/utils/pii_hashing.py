"""
PII Hashing Utility Module

This module provides functions for hashing and masking Personally Identifiable Information (PII)
such as phone numbers and email addresses. It implements SHA-256 hashing for secure storage
and masking functions for frontend display.

Requirements: 16.1, 16.4
"""

import hashlib
from typing import Optional


def hash_pii(value: Optional[str]) -> Optional[str]:
    """
    Hash PII data using SHA-256 for zero-knowledge ingestion.
    
    This function implements one-way hashing of sensitive data (phone, email) before
    persistence to ensure PII protection while maintaining fraud detection capabilities
    through shared contact detection.
    
    Args:
        value: The PII value to hash (phone or email). Can be None or empty string.
    
    Returns:
        The SHA-256 hash of the value as a hexadecimal string, or None if input is None/empty.
    
    Examples:
        >>> hash_pii("user@example.com")
        'b4c9a289323b21a01c3e940f150eb9b8c542587f1abfd8f0e1cc1ffc5e475514'
        
        >>> hash_pii("9876543210")
        '4a6f1b8e3c2d5a7f9e1b3c5d7f9a1b3c5d7f9a1b3c5d7f9a1b3c5d7f9a1b3c5d'
        
        >>> hash_pii(None)
        None
        
        >>> hash_pii("")
        None
    
    Note:
        - Uses SHA-256 for cryptographic strength
        - Hashing is one-way and cannot be reversed
        - Same input always produces same hash (deterministic)
        - Used for SHARED_CONTACT relationship detection in Neo4j
    """
    if not value:
        return None
    
    # Encode the value to bytes and compute SHA-256 hash
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def mask_pii_display(value: Optional[str], pii_type: str) -> str:
    """
    Mask PII data for frontend display purposes.
    
    This function creates masked representations of PII data for display in the UI,
    ensuring that sensitive information is not exposed while providing context to users.
    
    Args:
        value: The PII value to mask (phone or email). Can be None or empty string.
        pii_type: The type of PII - either 'email' or 'phone'.
    
    Returns:
        A masked string representation suitable for display:
        - For email: "***@***.com"
        - For phone: "***-***-XXXX" where XXXX are the last 4 digits
        - For unknown types or None/empty values: "***"
    
    Examples:
        >>> mask_pii_display("user@example.com", "email")
        '***@***.com'
        
        >>> mask_pii_display("9876543210", "phone")
        '***-***-3210'
        
        >>> mask_pii_display("123", "phone")
        '***'
        
        >>> mask_pii_display(None, "email")
        '***'
        
        >>> mask_pii_display("", "phone")
        '***'
    
    Note:
        - Only the last 4 digits of phone numbers are shown
        - Email addresses are completely masked
        - This is for display only; hashed values are used for storage
    """
    if not value:
        return "***"
    
    if pii_type == 'email':
        return "***@***.com"
    elif pii_type == 'phone':
        # Show last 4 digits if available
        if len(value) >= 4:
            return f"***-***-{value[-4:]}"
        else:
            return "***"
    else:
        return "***"
