"""
Trade Formula for Matrix - Convert statistical formulas to model matrices using fiasto-py
"""

import polars as pl
import fiasto_py
from typing import Dict, Any, List


def trade_formula_for_matrix(df: pl.DataFrame, formula: str) -> pl.DataFrame:
    """
    Convert a statistical formula to a model matrix using fiasto-py.
    
    Args:
        df: Polars DataFrame containing the data
        formula: Statistical formula string (e.g., "mpg ~ cyl + wt*hp + poly(disp, 4) - 1")
        
    Returns:
        Polars DataFrame containing the model matrix
        
    Examples:
        >>> import polars as pl
        >>> df = pl.read_csv("data/mtcars.csv")
        >>> model_matrix = trade_formula_for_matrix(df, "mpg ~ cyl + wt*hp + poly(disp, 4) - 1")
        >>> print(model_matrix)
    """
    # Parse the formula using fiasto-py
    parsed = fiasto_py.parse_formula(formula)
    
    # Get the response variable
    response_var = None
    for var_name, var_info in parsed["columns"].items():
        if "Response" in var_info["roles"]:
            response_var = var_name
            break
    
    # Start building the model matrix
    result_df = pl.DataFrame()
    
    # First, add all main effect variables
    for var_name, var_info in parsed["columns"].items():
        if ("FixedEffect" in var_info["roles"] or "Identity" in var_info["roles"]) and var_name != response_var:
            if var_name in df.columns:
                if result_df.is_empty():
                    result_df = df.select([var_name]).clone()
                else:
                    result_df = result_df.with_columns(df[var_name].alias(var_name))
    
    # Then, add interaction terms - fiasto-py 0.1.4 creates them as separate variables
    for var_name, var_info in parsed["columns"].items():
        if "InteractionTerm" in var_info["roles"] and var_name != response_var:
            # For interaction terms, we need to create them from the component variables
            # The variable name like "wt_hp" tells us which variables to multiply
            if "_" in var_name:
                # Split the interaction term name to get component variables
                component_vars = var_name.split("_")
                if all(var in df.columns for var in component_vars):
                    # Create the interaction expression
                    interaction_expr = pl.col(component_vars[0])
                    for var in component_vars[1:]:
                        interaction_expr = interaction_expr * pl.col(var)
                    
                    result_df = result_df.with_columns(interaction_expr.alias(var_name))
    
    # Add transformations (polynomials, etc.)
    for var_name, var_info in parsed["columns"].items():
        if ("FixedEffect" in var_info["roles"] or "Identity" in var_info["roles"]) and var_name != response_var and var_info.get("transformations"):
            for transformation in var_info["transformations"]:
                if transformation.get("function") == "poly":
                    degree = transformation.get("parameters", {}).get("degree", 2)
                    generated_columns = transformation.get("generates_columns", [])
                    
                    # Generate orthogonal polynomial terms using R's exact three-term recurrence relation
                    # Get the original data for orthogonalization
                    x_data = df[var_name].to_numpy()
                    import numpy as np
                    
                    n = len(x_data)
                    P = np.zeros((n, degree + 1))
                    
                    # Initialize: P_0 = 1 (constant term)
                    P[:, 0] = 1.0
                    
                    # First polynomial: P_1 = x - mean(x)
                    if degree > 0:
                        P[:, 1] = x_data - np.mean(x_data)
                    
                    # Three-term recurrence relation for higher order polynomials
                    for k in range(1, degree):
                        # Compute alpha_k = sum(x * P_k^2) / sum(P_k^2)
                        alpha_k = np.dot(x_data, P[:, k]**2) / np.dot(P[:, k], P[:, k])
                        
                        # Compute beta_k = sum(P_k^2) / sum(P_{k-1}^2)
                        beta_k = np.dot(P[:, k], P[:, k]) / np.dot(P[:, k-1], P[:, k-1])
                        
                        # Three-term recurrence: P_{k+1} = (x - alpha_k) * P_k - beta_k * P_{k-1}
                        P[:, k + 1] = (x_data - alpha_k) * P[:, k] - beta_k * P[:, k - 1]
                    
                    # Normalize each polynomial to have unit variance
                    for k in range(1, degree + 1):
                        norm = np.sqrt(np.dot(P[:, k], P[:, k]))
                        if norm > 0:
                            P[:, k] = P[:, k] / norm
                    
                    # Add the orthogonal polynomial columns (skip the constant term)
                    for i, col_name in enumerate(generated_columns):
                        poly_values = P[:, i + 1]  # Skip P[:, 0] which is the constant term
                        result_df = result_df.with_columns(
                            pl.Series(poly_values).alias(col_name)
                        )
    
    # Add intercept if needed (unless formula has "- 1")
    has_intercept = parsed["metadata"].get("has_intercept", True)
    if has_intercept:
        result_df = result_df.with_columns(pl.lit(1.0).alias("intercept"))
    
    # Reorder columns to match fiasto's expected order
    if "all_generated_columns_formula_order" in parsed:
        # Get the order from fiasto-py
        formula_order = parsed["all_generated_columns_formula_order"]
        # Sort by the order keys and extract column names
        ordered_columns = [col for _, col in sorted(formula_order.items(), key=lambda x: int(x[0]))]
        # Filter to only include columns that exist in our result and are not response variable
        desired_columns = [col for col in ordered_columns if col in result_df.columns and col != response_var]
        # Reorder the DataFrame
        if desired_columns:
            result_df = result_df.select(desired_columns)
    
    return result_df