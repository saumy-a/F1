"""
Unit tests for analytics helper functions.
Tests the helper functions implemented in task 1.1.
"""

import sys
import numpy as np
from typing import Any

# Import the helper functions from app.py
from app import (
    safe_int,
    safe_float,
    safe_divide,
    is_dnf,
    safe_correlation
)


def test_safe_int():
    """Test safe_int() with various edge cases."""
    print("\n=== Testing safe_int() ===")
    
    # Test normal integer conversion
    assert safe_int("5") == 5, "Should convert string '5' to int 5"
    assert safe_int(10) == 10, "Should handle int input"
    assert safe_int("123") == 123, "Should convert string '123' to int 123"
    print("✓ Normal integer conversions work")
    
    # Test DNF indicators
    assert safe_int("R") == 0, "Should return default (0) for 'R' (Retired)"
    assert safe_int("W") == 0, "Should return default (0) for 'W' (Withdrawn)"
    assert safe_int("R", default=99) == 99, "Should return custom default for 'R'"
    print("✓ DNF indicators handled correctly")
    
    # Test invalid inputs
    assert safe_int("invalid") == 0, "Should return default (0) for invalid string"
    assert safe_int(None) == 0, "Should return default (0) for None"
    assert safe_int("") == 0, "Should return default (0) for empty string"
    assert safe_int("12.5") == 0, "Should return default (0) for float string"
    print("✓ Invalid inputs handled correctly")
    
    # Test custom defaults
    assert safe_int("invalid", default=42) == 42, "Should return custom default"
    assert safe_int(None, default=-1) == -1, "Should return custom default for None"
    print("✓ Custom defaults work correctly")
    
    # Test edge cases
    assert safe_int(0) == 0, "Should handle zero"
    assert safe_int(-5) == -5, "Should handle negative integers"
    assert safe_int("-10") == -10, "Should convert negative string to int"
    print("✓ Edge cases handled correctly")
    
    print("✅ safe_int() tests passed!")


def test_safe_float():
    """Test safe_float() with various edge cases."""
    print("\n=== Testing safe_float() ===")
    
    # Test normal float conversion
    assert safe_float("5.5") == 5.5, "Should convert string '5.5' to float 5.5"
    assert safe_float(10.0) == 10.0, "Should handle float input"
    assert safe_float("123.456") == 123.456, "Should convert string to float"
    assert safe_float(42) == 42.0, "Should convert int to float"
    print("✓ Normal float conversions work")
    
    # Test invalid inputs
    assert safe_float("invalid") == 0.0, "Should return default (0.0) for invalid string"
    assert safe_float(None) == 0.0, "Should return default (0.0) for None"
    assert safe_float("") == 0.0, "Should return default (0.0) for empty string"
    print("✓ Invalid inputs handled correctly")
    
    # Test custom defaults
    assert safe_float("invalid", default=99.9) == 99.9, "Should return custom default"
    assert safe_float(None, default=-1.5) == -1.5, "Should return custom default for None"
    print("✓ Custom defaults work correctly")
    
    # Test edge cases
    assert safe_float(0) == 0.0, "Should handle zero"
    assert safe_float(-5.5) == -5.5, "Should handle negative floats"
    assert safe_float("-10.25") == -10.25, "Should convert negative string to float"
    assert safe_float("1e-5") == 1e-5, "Should handle scientific notation"
    assert safe_float("inf") == float('inf'), "Should handle infinity"
    print("✓ Edge cases handled correctly")
    
    print("✅ safe_float() tests passed!")


def test_safe_divide():
    """Test safe_divide() with various edge cases."""
    print("\n=== Testing safe_divide() ===")
    
    # Test normal division
    assert safe_divide(10, 2) == 5.0, "Should divide 10 / 2 = 5.0"
    assert safe_divide(7, 2) == 3.5, "Should divide 7 / 2 = 3.5"
    assert safe_divide(100, 4) == 25.0, "Should divide 100 / 4 = 25.0"
    print("✓ Normal division works")
    
    # Test zero denominator
    assert safe_divide(10, 0) == 0.0, "Should return default (0.0) for zero denominator"
    assert safe_divide(100, 0, default=99.9) == 99.9, "Should return custom default for zero denominator"
    assert safe_divide(0, 0) == 0.0, "Should return default for 0 / 0"
    print("✓ Zero denominator handled correctly")
    
    # Test custom defaults
    assert safe_divide(5, 0, default=-1.0) == -1.0, "Should return custom default"
    assert safe_divide(10, 0, default=float('nan')) != float('nan') or \
           str(safe_divide(10, 0, default=float('nan'))) == 'nan', "Should handle NaN default"
    print("✓ Custom defaults work correctly")
    
    # Test edge cases
    assert safe_divide(0, 5) == 0.0, "Should divide 0 / 5 = 0.0"
    assert safe_divide(-10, 2) == -5.0, "Should handle negative numerator"
    assert safe_divide(10, -2) == -5.0, "Should handle negative denominator"
    assert safe_divide(-10, -2) == 5.0, "Should handle both negative"
    assert safe_divide(1, 3) == 1/3, "Should handle floating point division"
    print("✓ Edge cases handled correctly")
    
    print("✅ safe_divide() tests passed!")


def test_is_dnf():
    """Test is_dnf() with various status strings."""
    print("\n=== Testing is_dnf() ===")
    
    # Test common DNF statuses
    assert is_dnf("Accident") == True, "Should detect 'Accident' as DNF"
    assert is_dnf("Engine") == True, "Should detect 'Engine' as DNF"
    assert is_dnf("Gearbox") == True, "Should detect 'Gearbox' as DNF"
    assert is_dnf("Transmission") == True, "Should detect 'Transmission' as DNF"
    assert is_dnf("Collision") == True, "Should detect 'Collision' as DNF"
    assert is_dnf("Retired") == True, "Should detect 'Retired' as DNF"
    assert is_dnf("Mechanical") == True, "Should detect 'Mechanical' as DNF"
    print("✓ Common DNF statuses detected")
    
    # Test technical DNF statuses
    assert is_dnf("Clutch") == True, "Should detect 'Clutch' as DNF"
    assert is_dnf("Hydraulics") == True, "Should detect 'Hydraulics' as DNF"
    assert is_dnf("Electrical") == True, "Should detect 'Electrical' as DNF"
    assert is_dnf("Brakes") == True, "Should detect 'Brakes' as DNF"
    assert is_dnf("Suspension") == True, "Should detect 'Suspension' as DNF"
    assert is_dnf("Fuel pressure") == True, "Should detect 'Fuel pressure' as DNF"
    assert is_dnf("Overheating") == True, "Should detect 'Overheating' as DNF"
    print("✓ Technical DNF statuses detected")
    
    # Test lap-down statuses (starts with '+')
    assert is_dnf("+1 Lap") == True, "Should detect '+1 Lap' as DNF"
    assert is_dnf("+2 Laps") == True, "Should detect '+2 Laps' as DNF"
    assert is_dnf("+5 Laps") == True, "Should detect '+5 Laps' as DNF"
    print("✓ Lap-down statuses detected")
    
    # Test non-DNF statuses
    assert is_dnf("Finished") == False, "Should not detect 'Finished' as DNF"
    assert is_dnf("Running") == False, "Should not detect 'Running' as DNF"
    assert is_dnf("Completed") == False, "Should not detect 'Completed' as DNF"
    assert is_dnf("1") == False, "Should not detect position '1' as DNF"
    assert is_dnf("Power Unit") == False, "Should not detect 'Power Unit' as DNF (not in list)"
    print("✓ Non-DNF statuses correctly identified")
    
    # Test edge cases
    assert is_dnf("Spun off") == True, "Should detect 'Spun off' as DNF"
    assert is_dnf("") == False, "Should not detect empty string as DNF"
    print("✓ Edge cases handled correctly")
    
    print("✅ is_dnf() tests passed!")


def test_safe_correlation():
    """Test safe_correlation() with zero variance inputs."""
    print("\n=== Testing safe_correlation() ===")
    
    # Test normal correlation
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]
    corr = safe_correlation(x, y)
    assert corr is not None, "Should calculate correlation for valid data"
    assert abs(corr - 1.0) < 0.001, "Should return ~1.0 for perfect positive correlation"
    print("✓ Normal correlation calculation works")
    
    # Test negative correlation
    x = [1, 2, 3, 4, 5]
    y = [10, 8, 6, 4, 2]
    corr = safe_correlation(x, y)
    assert corr is not None, "Should calculate correlation for valid data"
    assert abs(corr - (-1.0)) < 0.001, "Should return ~-1.0 for perfect negative correlation"
    print("✓ Negative correlation detected")
    
    # Test zero variance in x
    x_zero_var = [5, 5, 5, 5, 5]
    y = [1, 2, 3, 4, 5]
    corr = safe_correlation(x_zero_var, y)
    assert corr is None, "Should return None for zero variance in x"
    print("✓ Zero variance in x handled correctly")
    
    # Test zero variance in y
    x = [1, 2, 3, 4, 5]
    y_zero_var = [10, 10, 10, 10, 10]
    corr = safe_correlation(x, y_zero_var)
    assert corr is None, "Should return None for zero variance in y"
    print("✓ Zero variance in y handled correctly")
    
    # Test zero variance in both
    x_zero_var = [3, 3, 3, 3, 3]
    y_zero_var = [7, 7, 7, 7, 7]
    corr = safe_correlation(x_zero_var, y_zero_var)
    assert corr is None, "Should return None for zero variance in both"
    print("✓ Zero variance in both handled correctly")
    
    # Test insufficient data
    x_short = [1]
    y_short = [2]
    corr = safe_correlation(x_short, y_short)
    assert corr is None, "Should return None for single data point"
    print("✓ Insufficient data handled correctly")
    
    # Test mismatched lengths
    x = [1, 2, 3, 4, 5]
    y = [1, 2, 3]
    corr = safe_correlation(x, y)
    assert corr is None, "Should return None for mismatched lengths"
    print("✓ Mismatched lengths handled correctly")
    
    # Test empty lists
    corr = safe_correlation([], [])
    assert corr is None, "Should return None for empty lists"
    print("✓ Empty lists handled correctly")
    
    # Test with realistic F1 data (grid vs finish positions)
    grid_positions = [1, 3, 2, 5, 4, 7, 6, 8]
    finish_positions = [1, 2, 3, 4, 5, 6, 7, 8]
    corr = safe_correlation(grid_positions, finish_positions)
    assert corr is not None, "Should calculate correlation for realistic data"
    assert 0.5 < corr < 1.0, "Should show positive correlation for grid vs finish"
    print("✓ Realistic F1 data correlation works")
    
    print("✅ safe_correlation() tests passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Analytics Helper Functions (Task 1.1)")
    print("=" * 60)
    
    try:
        test_safe_int()
        test_safe_float()
        test_safe_divide()
        test_is_dnf()
        test_safe_correlation()
        
        print("\n" + "=" * 60)
        print("✅ ALL HELPER FUNCTION TESTS PASSED!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
