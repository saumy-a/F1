"""
Helper utility functions for data processing and safe operations.
"""

from typing import Any
import numpy as np


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int with DNF handling.
    
    Args:
        value: Value to convert (may be string, int, or DNF indicator)
        default: Default value to return if conversion fails
        
    Returns:
        Integer value or default if conversion fails
    """
    try:
        if value == 'R' or value == 'W':  # DNF indicators
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float.
    
    Args:
        value: Value to convert
        default: Default value to return if conversion fails
        
    Returns:
        Float value or default if conversion fails
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely perform division with zero-denominator handling.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value to return if denominator is zero
        
    Returns:
        Division result or default if denominator is zero
    """
    if denominator == 0:
        return default
    return numerator / denominator


def is_dnf(status: str) -> bool:
    """
    Check if race status indicates DNF (Did Not Finish).
    
    Args:
        status: Race status string from API
        
    Returns:
        True if status indicates DNF, False otherwise
    """
    dnf_statuses = [
        'Accident', 'Engine', 'Gearbox', 'Transmission', 'Clutch',
        'Hydraulics', 'Electrical', 'Collision', 'Spun off', 'Retired',
        'Mechanical', 'Brakes', 'Suspension', 'Fuel pressure', 'Overheating'
    ]
    return status in dnf_statuses or status.startswith('+')


def safe_correlation(x: list, y: list) -> float | None:
    """
    Safely calculate Pearson correlation coefficient with variance checking.
    
    Args:
        x: First variable (list of numeric values)
        y: Second variable (list of numeric values)
        
    Returns:
        Correlation coefficient (-1 to 1) or None if calculation fails
    """
    if len(x) < 2 or len(y) < 2:
        return None
    
    if len(x) != len(y):
        return None
    
    # Check for sufficient variance
    if np.std(x) == 0 or np.std(y) == 0:
        return None
    
    try:
        correlation = np.corrcoef(x, y)[0, 1]
        return correlation
    except Exception:
        return None
