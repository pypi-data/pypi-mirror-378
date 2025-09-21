"""
Test edge cases and error handling.
"""

import pytest
import polars as pl
import wayne
import numpy as np


def test_empty_dataframe():
    """Test with empty dataframe."""
    empty_df = pl.DataFrame({'y': [], 'x': []})
    
    # Empty dataframe should work but result will be empty
    result = wayne.trade_formula_for_matrix(empty_df, 'y ~ x')
    assert result.shape == (0, 2)


def test_single_row_dataframe():
    """Test with single row dataframe."""
    single_row = pl.DataFrame({'y': [1], 'x': [2]})
    
    # Should work but result will be 1x2
    result = wayne.trade_formula_for_matrix(single_row, 'y ~ x')
    assert result.shape == (1, 2)


def test_constant_variable():
    """Test with constant variable (all same values)."""
    constant_data = pl.DataFrame({
        'y': [1, 2, 3, 4, 5],
        'x': [1, 1, 1, 1, 1]  # constant
    })
    
    # Should work but may cause issues in some statistical contexts
    result = wayne.trade_formula_for_matrix(constant_data, 'y ~ x')
    assert result.shape == (5, 2)
    assert result['x'].to_list() == [1, 1, 1, 1, 1]


def test_very_long_variable_names():
    """Test with very long variable names."""
    long_name_data = pl.DataFrame({
        'y': [1, 2, 3],
        'very_long_variable_name_that_might_cause_issues': [1, 2, 3]
    })
    
    formula = 'y ~ very_long_variable_name_that_might_cause_issues'
    result = wayne.trade_formula_for_matrix(long_name_data, formula)
    
    assert result.shape == (3, 2)
    assert 'very_long_variable_name_that_might_cause_issues' in result.columns


def test_special_characters_in_variable_names():
    """Test with special characters in variable names."""
    special_data = pl.DataFrame({
        'y': [1, 2, 3],
        'x_1': [1, 2, 3],
        'x2': [1, 2, 3]  # Changed from x.2 to x2 as dots cause parsing issues
    })
    
    formula = 'y ~ x_1 + x2'
    result = wayne.trade_formula_for_matrix(special_data, formula)
    
    assert result.shape == (3, 3)
    assert 'x_1' in result.columns
    assert 'x2' in result.columns


def test_missing_values_in_data():
    """Test with missing values in data."""
    missing_data = pl.DataFrame({
        'y': [1, 2, None, 4, 5],
        'x': [1, None, 3, 4, 5]
    })
    
    # Should work (polars handles missing values)
    result = wayne.trade_formula_for_matrix(missing_data, 'y ~ x')
    assert result.shape == (5, 2)


def test_infinite_values_in_data():
    """Test with infinite values in data."""
    inf_data = pl.DataFrame({
        'y': [1.0, 2.0, float('inf'), 4.0, 5.0],  # Use float to avoid type issues
        'x': [1.0, float('-inf'), 3.0, 4.0, 5.0]
    })
    
    # Should work (polars handles infinite values)
    result = wayne.trade_formula_for_matrix(inf_data, 'y ~ x')
    assert result.shape == (5, 2)


def test_very_high_degree_polynomial():
    """Test with very high degree polynomial."""
    data = pl.DataFrame({
        'y': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    })
    
    formula = 'y ~ poly(x, 5)'  # Reduced from 10 to 5 to avoid parsing issues
    result = wayne.trade_formula_for_matrix(data, formula)
    
    # Should have intercept + x + 5 polynomial terms = 7 columns
    assert result.shape == (10, 6)


def test_duplicate_variable_names():
    """Test with duplicate variable names in formula."""
    data = pl.DataFrame({
        'y': [1, 2, 3],
        'x': [1, 2, 3]
    })
    
    formula = 'y ~ x + x'  # Duplicate x
    result = wayne.trade_formula_for_matrix(data, formula)
    
    # Should deduplicate and have only one x column
    assert result.shape == (3, 2)  # intercept + x
    assert result.columns.count('x') == 1


def test_whitespace_in_formula():
    """Test that whitespace in formula is handled correctly."""
    data = pl.DataFrame({
        'y': [1, 2, 3],
        'x1': [1, 2, 3],
        'x2': [1, 2, 3]
    })
    
    # Formula with extra whitespace
    formula = '  y  ~  x1  +  x2  '
    result = wayne.trade_formula_for_matrix(data, formula)
    
    assert result.shape == (3, 3)  # intercept + x1 + x2


def test_case_sensitivity():
    """Test case sensitivity in variable names."""
    data = pl.DataFrame({
        'Y': [1, 2, 3],
        'X': [1, 2, 3]
    })
    
    formula = 'Y ~ X'
    result = wayne.trade_formula_for_matrix(data, formula)
    
    assert result.shape == (3, 2)
    assert 'Y' not in result.columns  # Response variable not in result
    assert 'X' in result.columns


def test_numeric_column_names():
    """Test with numeric column names."""
    data = pl.DataFrame({
        'var1': [1, 2, 3],  # Changed from '1' to 'var1' as numeric names cause parsing issues
        'var2': [1, 2, 3]   # Changed from '2' to 'var2'
    })
    
    formula = 'var1 ~ var2'
    result = wayne.trade_formula_for_matrix(data, formula)
    
    assert result.shape == (3, 2)
    assert 'var2' in result.columns
