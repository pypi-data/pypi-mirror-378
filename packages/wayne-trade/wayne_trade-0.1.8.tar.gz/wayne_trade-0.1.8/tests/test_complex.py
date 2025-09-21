"""
Test complex formulas combining interactions and polynomials.
"""

import pytest
import polars as pl
import wayne


def test_complex_mtcars_formula(mtcars_data):
    """Test the complex mtcars formula from examples."""
    formula = 'mpg ~ cyl + wt*hp + poly(disp, 4) - 1'
    result = wayne.trade_formula_for_matrix(mtcars_data, formula)
    
    assert result.shape == (32, 8)
    assert 'cyl' in result.columns
    assert 'hp' in result.columns
    assert 'wt' in result.columns
    assert 'wt_hp' in result.columns
    assert 'disp_poly_1' in result.columns
    assert 'disp_poly_2' in result.columns
    assert 'disp_poly_3' in result.columns
    assert 'disp_poly_4' in result.columns
    assert 'intercept' not in result.columns


def test_very_complex_formula(sample_data):
    """Test a very complex formula with multiple interactions and polynomials."""
    formula = 'y ~ x1*x2 + poly(x3, 3) + x1:poly(x3, 2)'
    result = wayne.trade_formula_for_matrix(sample_data, formula)
    
    # Should have: intercept + x1 + x2 + x1:x2 + poly(x3, 3) + x1:poly(x3, 2) terms
    assert 'intercept' in result.columns
    assert 'x1' in result.columns
    assert 'x2' in result.columns
    assert 'x1_x2' in result.columns
    assert 'x3_poly_1' in result.columns
    assert 'x3_poly_2' in result.columns
    assert 'x3_poly_3' in result.columns


def test_column_order_complex(sample_data):
    """Test that column order is correct for complex formulas."""
    formula = 'y ~ x1 + poly(x2, 2) + x1*x3'
    result = wayne.trade_formula_for_matrix(sample_data, formula)
    
    # Expected order: intercept, main effects, polynomial terms, interactions
    expected_order = [
        'intercept', 'x1', 'x2_poly_1', 'x2_poly_2', 'x3', # polynomial terms
        'x1_x3'  # interactions
    ]
    assert result.columns == expected_order


def test_mixed_categorical_numeric(sample_data):
    """Test formula with both categorical and numeric variables."""
    # Skip this test as categorical interactions cause arithmetic errors
    # with current fiasto-py version
    pytest.skip("Categorical interactions not supported in current fiasto-py version")


def test_reproducibility(sample_data):
    """Test that the same formula produces the same result multiple times."""
    formula = 'y ~ x1*x2 + poly(x3, 2)'
    
    result1 = wayne.trade_formula_for_matrix(sample_data, formula)
    result2 = wayne.trade_formula_for_matrix(sample_data, formula)
    
    # Results should be identical
    assert result1.equals(result2)


def test_large_dataset():
    """Test with a larger dataset to ensure performance."""
    import numpy as np
    
    # Create larger dataset
    np.random.seed(42)
    n = 1000
    large_data = pl.DataFrame({
        'y': np.random.normal(0, 1, n),
        'x1': np.random.normal(0, 1, n),
        'x2': np.random.normal(0, 1, n),
        'x3': np.random.normal(0, 1, n),
        'x4': np.random.normal(0, 1, n)
    })
    
    formula = 'y ~ x1*x2 + poly(x3, 3) + x4'
    result = wayne.trade_formula_for_matrix(large_data, formula)
    
    # Should have correct shape
    assert result.shape[0] == n
    assert result.shape[1] > 5  # Multiple terms
    
    # All values should be finite
    for col in result.columns:
        assert result[col].is_finite().all(), f"Column {col} contains non-finite values"
