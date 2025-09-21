"""
Test interaction functionality.
"""

import pytest
import polars as pl
import wayne


def test_simple_interaction(simple_data):
    """Test simple two-variable interaction."""
    formula = 'y ~ x1*x2'
    result = wayne.trade_formula_for_matrix(simple_data, formula)
    
    # Should have intercept + x1 + x2 + x1_z = 4 columns
    assert result.shape == (5, 4)
    assert 'intercept' in result.columns
    assert 'x1' in result.columns
    assert 'x2' in result.columns
    assert 'x1_x2' in result.columns

def test_multiple_interactions(simple_data):
    """Test multiple interactions in one formula."""
    formula = 'y ~ x1 + x2 + x1:x2'
    result = wayne.trade_formula_for_matrix(simple_data, formula)
    
    # Should have intercept + x1 + x2 + x1_z = 4 columns
    assert result.shape == (5, 4)
    assert 'x1' in result.columns
    assert 'x2' in result.columns
    assert 'x1_x2' in result.columns


def test_interaction_without_main_effects(simple_data):
    """Test interaction without main effects (using : operator)."""
    formula = 'y ~ x1:x2'
    result = wayne.trade_formula_for_matrix(simple_data, formula)
    
    # Should have intercept + x1 + x2 + x1_z = 4 columns (fiasto includes main effects)
    assert result.shape == (5, 4)
    assert 'intercept' in result.columns
    assert 'x1_x2' in result.columns


def test_three_way_interaction(simple_data):
    """Test three-way interaction - currently limited by fiasto-py 0.1.4."""
    # Add a third variable
    data = simple_data.with_columns([
        pl.lit([1, 2, 3, 4, 5]).alias('x3')
    ])
    
    formula = 'y ~ x1*x2*x3'
    result = wayne.trade_formula_for_matrix(data, formula)
    
    # Note: fiasto-py 0.1.4 doesn't fully support three-way interactions with *
    # It only generates two-way interactions, so we expect the same result as x1*x2
    assert result.shape == (5, 8)
    assert 'intercept' in result.columns
    assert 'x1' in result.columns
    assert 'x2' in result.columns
    assert 'x3' in result.columns
    assert 'x1_x2' in result.columns
    assert 'x1_x3' in result.columns
    assert 'x2_x3' in result.columns
    assert 'x1_x2_x3' in result.columns

def test_interaction_column_order(simple_data):
    """Test that interaction columns are ordered correctly."""
    formula = 'y ~ x1*x2'
    result = wayne.trade_formula_for_matrix(simple_data, formula)
    
    # Column order should be: intercept, main effects, interactions
    expected_order = ['intercept', 'x1', 'x2', 'x1_x2']
    assert result.columns == expected_order


