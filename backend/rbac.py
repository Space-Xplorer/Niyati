"""
RBAC (Role-Based Access Control) filtering utilities for Project Niyati.

This module provides functions to automatically wrap Neo4j and PostgreSQL queries
with tenant filtering based on user role (Admin or Business_Owner).
"""

from flask import jsonify


def apply_neo4j_tenant_filter(cypher_query, user_role, user_gstin, params=None):
    """
    Wrap Neo4j Cypher query with tenant filtering for Business_Owner role.
    
    Args:
        cypher_query (str): The base Cypher query to wrap
        user_role (str): User role ('Admin' or 'Business_Owner')
        user_gstin (str): User's GSTIN (required for Business_Owner)
        params (dict): Query parameters
    
    Returns:
        tuple: (modified_query, modified_params)
    
    Raises:
        403: If Business_Owner attempts to access data without GSTIN
    """
    if params is None:
        params = {}
    
    # Admin users see all data - no filtering
    if user_role == 'Admin':
        return cypher_query, params
    
    # Business_Owner must have GSTIN
    if user_role == 'Business_Owner':
        if not user_gstin:
            raise PermissionError("Business_Owner must have GSTIN associated")
        
        # Add GSTIN filter to query
        # This wraps the query to filter Taxpayer nodes by GSTIN
        # Pattern: Match taxpayer nodes and filter by session GSTIN
        if 'MATCH' in cypher_query.upper():
            # Find where to inject the WHERE clause
            # Look for patterns like: MATCH (t:Taxpayer)
            if '(t:Taxpayer)' in cypher_query or '(taxpayer:Taxpayer)' in cypher_query:
                # Determine the variable name used
                var_name = 't' if '(t:Taxpayer)' in cypher_query else 'taxpayer'
                
                # Check if WHERE clause already exists
                if 'WHERE' in cypher_query.upper():
                    # Append to existing WHERE clause
                    modified_query = cypher_query.replace(
                        'WHERE', 
                        f'WHERE {var_name}.gstin = $SESSION_GSTIN AND',
                        1  # Only replace first occurrence
                    )
                else:
                    # Add new WHERE clause after MATCH
                    # Find the position after the first MATCH clause
                    match_end = cypher_query.upper().find('RETURN')
                    if match_end == -1:
                        match_end = cypher_query.upper().find('WITH')
                    if match_end == -1:
                        # No RETURN or WITH, add at end
                        modified_query = f"{cypher_query}\nWHERE {var_name}.gstin = $SESSION_GSTIN"
                    else:
                        modified_query = (
                            cypher_query[:match_end] + 
                            f"\nWHERE {var_name}.gstin = $SESSION_GSTIN\n" + 
                            cypher_query[match_end:]
                        )
                
                params['SESSION_GSTIN'] = user_gstin
                return modified_query, params
        
        # If no Taxpayer pattern found, return original (might be a different query type)
        # In production, you might want to be more strict here
        return cypher_query, params
    
    # Unknown role - deny access
    raise PermissionError(f"Unknown role: {user_role}")


def apply_postgres_tenant_filter(base_query, user_role, user_gstin, table_alias='t'):
    """
    Wrap PostgreSQL query with tenant filtering for Business_Owner role.
    
    Args:
        base_query (SQLAlchemy query): The base SQLAlchemy query object
        user_role (str): User role ('Admin' or 'Business_Owner')
        user_gstin (str): User's GSTIN (required for Business_Owner)
        table_alias (str): The table alias or column name containing GSTIN
    
    Returns:
        SQLAlchemy query: Modified query with tenant filter applied
    
    Raises:
        403: If Business_Owner attempts to access data without GSTIN
    """
    # Admin users see all data - no filtering
    if user_role == 'Admin':
        return base_query
    
    # Business_Owner must have GSTIN
    if user_role == 'Business_Owner':
        if not user_gstin:
            raise PermissionError("Business_Owner must have GSTIN associated")
        
        # Apply GSTIN filter to the query
        # This assumes the table has a 'gstin' column
        # For more complex queries, you might need to pass the model class
        return base_query.filter_by(gstin=user_gstin)
    
    # Unknown role - deny access
    raise PermissionError(f"Unknown role: {user_role}")


def check_access_permission(user_role, user_gstin, requested_gstin):
    """
    Check if user has permission to access data for the requested GSTIN.
    
    Args:
        user_role (str): User role ('Admin' or 'Business_Owner')
        user_gstin (str): User's GSTIN
        requested_gstin (str): GSTIN being requested
    
    Returns:
        bool: True if access is allowed
    
    Raises:
        403: If access is denied
    """
    # Admin can access all GSTINs
    if user_role == 'Admin':
        return True
    
    # Business_Owner can only access their own GSTIN
    if user_role == 'Business_Owner':
        if user_gstin != requested_gstin:
            raise PermissionError(
                f"Access denied: Business_Owner can only access their own GSTIN"
            )
        return True
    
    # Unknown role - deny access
    raise PermissionError(f"Unknown role: {user_role}")


def rbac_error_handler(error):
    """
    Convert RBAC permission errors to Flask JSON responses.
    
    Args:
        error (Exception): The permission error
    
    Returns:
        tuple: (JSON response, status code)
    """
    if isinstance(error, PermissionError):
        return jsonify({'message': str(error)}), 403
    return jsonify({'message': 'Access denied'}), 403
