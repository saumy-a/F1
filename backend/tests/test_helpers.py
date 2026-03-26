"""
Unit tests for helper utility functions.
"""

import pytest
import numpy as np
from app.utils.helpers import safe_int, safe_float, safe_divide, is_dnf, safe_correlation


def test_safe_int_valid():
    """Test safe_int with valid inputs."""
    assert safe_int(5) == 5
    assert safe_int("10") == 10
    assert safe_int("3") == 3


def test_safe_int_dnf_indicators():
    """Test safe_int with DNF indicators."""
    assert safe_int('R') == 0
    assert safe_int('W') == 0
    assert safe_int('R', default=99) == 99


def test_safe_int_invalid():
    """Test safe_int with invalid inputs."""
    assert safe_int("invalid") == 0
    assert safe_int(None) == 0
    assert safe_int("abc", default=42) == 42


def test_safe_float_valid():
    """Test safe_float with valid inputs."""
    assert safe_float(5.5) == 5.5
    assert safe_float("10.2") == 10.2
    assert safe_float(3) == 3.0


def test_safe_float_invalid():
    """Test safe_float with invalid inputs."""
    assert safe_float("invalid") == 0.0
    assert safe_float(None) == 0.0
    assert safe_float("abc", default=3.14) == 3.14


def test_safe_divide_valid():
    """Test safe_divide with valid inputs."""
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(7, 2) == 3.5
    assert safe_divide(0, 5) == 0.0


def test_safe_divide_zero_denominator():
    """Test safe_divide with zero denominator."""
    assert safe_divide(10, 0) == 0.0
    assert safe_divide(10, 0, default=99.9) == 99.9


def test_is_dnf_mechanical():
    """Test is_dnf with mechanical failures."""
    assert is_dnf('Engine') is True
    assert is_dnf('Gearbox') is True
    assert is_dnf('Transmission') is True
    assert is_dnf('Brakes') is True


def test_is_dnf_accident():
    """Test is_dnf with accidents."""
    assert is_dnf('Accident') is True
    assert is_dnf('Collision') is True
    assert is_dnf('Spun off') is True


def test_is_dnf_finished():
    """Test is_dnf with finished status."""
    assert is_dnf('Finished') is False
    assert is_dnf('+1 Lap') is True  # Lapped cars are considered DNF


def test_safe_correlation_valid():
    """Test safe_correlation with valid data."""
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]
    
    result = safe_correlation(x, y)
    assert result is not None
    assert abs(result - 1.0) < 0.01  # Perfect positive correlation


def test_safe_correlation_insufficient_data():
    """Test safe_correlation with insufficient data."""
    assert safe_correlation([1], [2]) is None
    assert safe_correlation([], []) is None


def test_safe_correlation_mismatched_length():
    """Test safe_correlation with mismatched lengths."""
    assert safe_correlation([1, 2, 3], [1, 2]) is None


def test_safe_correlation_zero_variance():
    """Test safe_correlation with zero variance."""
    x = [5, 5, 5, 5]
    y = [1, 2, 3, 4]
    
    result = safe_correlation(x, y)
    assert result is None  # Cannot calculate correlation with zero variance
