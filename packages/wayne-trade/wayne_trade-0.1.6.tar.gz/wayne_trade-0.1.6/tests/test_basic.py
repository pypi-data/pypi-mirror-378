"""
Test basic functionality of wayne package.
"""

import pytest
import polars as pl
import wayne


def test_simple_formula(simple_data):
    """Test simple formula without interactions or transformations."""
    formula = 'y ~ x1 + x2'
    result = wayne.trade_formula_for_matrix(simple_data, formula)
    
    # Should have intercept + x1 + x2 = 3 columns
    assert result.shape == (5, 3)
    assert 'intercept' in result.columns
    assert 'x1' in result.columns
    assert 'x2' in result.columns
    
    # Check that intercept is all 1s
    assert result['intercept'].to_list() == [1, 1, 1, 1, 1]


def test_formula_without_intercept(simple_data):
    """Test formula without intercept (-1)."""
    formula = 'y ~ x1 + x2 - 1'
    result = wayne.trade_formula_for_matrix(simple_data, formula)
    
    # Should have x1 + x2 = 2 columns, no intercept
    assert result.shape == (5, 2)
    assert 'intercept' not in result.columns
    assert 'x1' in result.columns
    assert 'x2' in result.columns


def test_single_variable_formula(simple_data):
    """Test formula with single variable."""
    formula = 'y ~ x1'
    result = wayne.trade_formula_for_matrix(simple_data, formula)
    
    # Should have intercept + x1 = 2 columns
    assert result.shape == (5, 2)
    assert 'intercept' in result.columns
    assert 'x1' in result.columns


def test_empty_formula_raises_error(simple_data):
    """Test that empty formula raises appropriate error."""
    with pytest.raises(ValueError):
        wayne.trade_formula_for_matrix(simple_data, '')


def test_invalid_formula_raises_error(simple_data):
    """Test that invalid formula raises appropriate error."""
    with pytest.raises(ValueError):
        wayne.trade_formula_for_matrix(simple_data, 'invalid formula')


def test_dataframe_type_check():
    """Test that non-polars DataFrame raises error."""
    import pandas as pd
    df = pd.DataFrame({'y': [1, 2, 3], 'x': [1, 2, 3]})
    
    with pytest.raises(AttributeError):
        wayne.trade_formula_for_matrix(df, 'y ~ x')
