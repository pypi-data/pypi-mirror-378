"""
Wayne Speak Fiasto - Clean interface to fiasto-py parsing functionality

This module provides a clean interface to fiasto-py's parsing functionality
without requiring users to directly import fiasto-py and deal with its
maturin/pyo3 complexity.
"""

import fiasto_py
from typing import Dict, Any


def speak_fiasto(formula: str) -> Dict[str, Any]:
    """
    Parse a statistical formula using fiasto-py and return the raw results.
    
    This function provides a clean interface to fiasto-py's parsing functionality
    without requiring users to directly import fiasto-py and deal with its
    maturin/pyo3 complexity.
    
    Args:
        formula: Statistical formula string (e.g., "mpg ~ cyl + wt*hp + poly(disp, 4) - 1")
        
    Returns:
        Dictionary containing the parsed formula structure with:
        - columns: Dictionary of variables and their metadata
        - metadata: Formula metadata (intercept, response variables, etc.)
        - all_generated_columns: List of all generated column names
        - all_generated_columns_formula_order: Ordered mapping of column positions
        
    Examples:
        >>> import wayne
        >>> result = wayne.speak_fiasto("mpg ~ cyl + wt*hp")
        >>> print(result['columns'].keys())
        >>> print(result['metadata']['has_intercept'])
        
    Raises:
        Exception: If fiasto-py fails to parse the formula
    """
    try:
        return fiasto_py.parse_formula(formula)
    except Exception as e:
        raise Exception(f"Failed to parse formula '{formula}': {str(e)}")
