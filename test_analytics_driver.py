"""
Unit tests for driver analytics calculations (Task 3.5).
Tests specific edge cases and examples for driver analytics functions.
"""

import sys
import numpy as np
from typing import Dict, Any

# Import the functions from app.py
from app import (
    calculate_analytics_consistency_score,
    calculate_analytics_dnf_rate,
    calculate_analytics_form_indicator
)


def test_consistency_score_perfect_consistency():
    """Test consistency score with perfect consistency (std_dev = 0)."""
    print("\n=== Testing Consistency Score with Perfect Consistency ===")
    
    # Create race results where driver finishes in the same position every time
    race_results = []
    for i in range(6):
        race_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [{
                'position': '3',  # Always finishes 3rd
                'points': '15',
                'status': 'Finished',
                'grid': str(i+1)
            }]
        })
    
    consistency = calculate_analytics_consistency_score(race_results, min_races=5)
    
    print(f"✓ Consistency data: {consistency}")
    assert consistency is not None, "Should return consistency data"
    assert consistency['std_dev'] == 0.0, "Standard deviation should be 0 for perfect consistency"
    assert consistency['consistency_score'] == 100.0, "Consistency score should be 100 for std_dev = 0"
    assert consistency['avg_position'] == 3.0, "Average position should be 3.0"
    assert consistency['completed_races'] == 6, "Should have 6 completed races"
    
    print("✅ Perfect consistency test passed!")


def test_consistency_score_excludes_dnf():
    """Test consistency score excludes DNF results."""
    print("\n=== Testing Consistency Score Excludes DNF ===")
    
    # Create race results with some DNFs
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-01-01',
            'round': '1',
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1'
            }]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-02-01',
            'round': '2',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Engine',  # DNF
                'grid': '2'
            }]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-01',
            'round': '3',
            'Results': [{
                'position': '2',
                'points': '18',
                'status': 'Finished',
                'grid': '3'
            }]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-04-01',
            'round': '4',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Accident',  # DNF
                'grid': '1'
            }]
        },
        {
            'raceName': 'Race 5',
            'date': '2024-05-01',
            'round': '5',
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '2'
            }]
        },
        {
            'raceName': 'Race 6',
            'date': '2024-06-01',
            'round': '6',
            'Results': [{
                'position': '2',
                'points': '18',
                'status': 'Finished',
                'grid': '4'
            }]
        },
        {
            'raceName': 'Race 7',
            'date': '2024-07-01',
            'round': '7',
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1'
            }]
        }
    ]
    
    consistency = calculate_analytics_consistency_score(race_results, min_races=5)
    
    print(f"✓ Consistency data: {consistency}")
    assert consistency is not None, "Should return consistency data"
    assert consistency['total_races'] == 7, "Should count all 7 races"
    assert consistency['completed_races'] == 5, "Should count only 5 completed races (excluding 2 DNFs)"
    
    # Verify the calculation only uses finished positions: [1, 2, 1, 2, 1]
    expected_positions = [1, 2, 1, 2, 1]
    expected_avg = np.mean(expected_positions)
    expected_std = np.std(expected_positions)
    
    assert abs(consistency['avg_position'] - expected_avg) < 0.01, \
        f"Average position should be {expected_avg}, got {consistency['avg_position']}"
    assert abs(consistency['std_dev'] - expected_std) < 0.01, \
        f"Std dev should be {expected_std}, got {consistency['std_dev']}"
    
    print("✅ DNF exclusion test passed!")


def test_dnf_rate_no_dnfs():
    """Test DNF rate with no DNFs."""
    print("\n=== Testing DNF Rate with No DNFs ===")
    
    # Create race results with all finishes
    race_results = []
    for i in range(5):
        race_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [{
                'position': str(i+1),
                'points': str(25 - i*5),
                'status': 'Finished',
                'grid': str(i+1)
            }]
        })
    
    dnf_data = calculate_analytics_dnf_rate(race_results)
    
    print(f"✓ DNF data: {dnf_data}")
    assert dnf_data['dnf_count'] == 0, "Should have 0 DNFs"
    assert dnf_data['dnf_percentage'] == 0.0, "DNF percentage should be 0.0"
    assert dnf_data['total_races'] == 5, "Should have 5 total races"
    assert len(dnf_data['dnf_causes']) == 0, "Should have no DNF causes"
    
    print("✅ No DNFs test passed!")


def test_dnf_rate_all_dnfs():
    """Test DNF rate with all DNFs."""
    print("\n=== Testing DNF Rate with All DNFs ===")
    
    # Create race results with all DNFs
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-01-01',
            'round': '1',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Engine',
                'grid': '1'
            }]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-02-01',
            'round': '2',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Accident',
                'grid': '2'
            }]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-01',
            'round': '3',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Gearbox',
                'grid': '3'
            }]
        }
    ]
    
    dnf_data = calculate_analytics_dnf_rate(race_results)
    
    print(f"✓ DNF data: {dnf_data}")
    assert dnf_data['dnf_count'] == 3, "Should have 3 DNFs"
    assert dnf_data['dnf_percentage'] == 100.0, "DNF percentage should be 100.0"
    assert dnf_data['total_races'] == 3, "Should have 3 total races"
    
    print("✅ All DNFs test passed!")


def test_dnf_cause_categorization():
    """Test DNF cause categorization."""
    print("\n=== Testing DNF Cause Categorization ===")
    
    # Create race results with various DNF causes
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-01-01',
            'round': '1',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Engine',  # Mechanical
                'grid': '1'
            }]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-02-01',
            'round': '2',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Gearbox',  # Mechanical
                'grid': '2'
            }]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-01',
            'round': '3',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Accident',  # Accident
                'grid': '3'
            }]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-04-01',
            'round': '4',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Collision',  # Accident
                'grid': '4'
            }]
        },
        {
            'raceName': 'Race 5',
            'date': '2024-05-01',
            'round': '5',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Retired',  # Other (generic retirement)
                'grid': '5'
            }]
        },
        {
            'raceName': 'Race 6',
            'date': '2024-06-01',
            'round': '6',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Electrical',  # Mechanical
                'grid': '6'
            }]
        }
    ]
    
    dnf_data = calculate_analytics_dnf_rate(race_results)
    
    print(f"✓ DNF data: {dnf_data}")
    print(f"✓ DNF causes: {dnf_data['dnf_causes']}")
    
    assert dnf_data['dnf_count'] == 6, "Should have 6 DNFs"
    assert 'Mechanical' in dnf_data['dnf_causes'], "Should have Mechanical category"
    assert 'Accident' in dnf_data['dnf_causes'], "Should have Accident category"
    assert 'Other' in dnf_data['dnf_causes'], "Should have Other category"
    
    assert dnf_data['dnf_causes']['Mechanical'] == 3, "Should have 3 Mechanical DNFs (Engine, Gearbox, Electrical)"
    assert dnf_data['dnf_causes']['Accident'] == 2, "Should have 2 Accident DNFs (Accident, Collision)"
    assert dnf_data['dnf_causes']['Other'] == 1, "Should have 1 Other DNF (Retired)"
    
    print("✅ DNF cause categorization test passed!")


def test_form_indicator_improving_trend():
    """Test form indicator with improving trend."""
    print("\n=== Testing Form Indicator with Improving Trend ===")
    
    # Create race results with improving positions (getting better over time)
    # Most recent races first, with positions improving (getting lower)
    race_results = [
        {
            'raceName': 'Race 5',
            'date': '2024-05-01',
            'round': '5',
            'Results': [{
                'position': '6',  # Most recent - worst position
                'points': '8',
                'status': 'Finished',
                'grid': '7'
            }]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-04-01',
            'round': '4',
            'Results': [{
                'position': '5',
                'points': '10',
                'status': 'Finished',
                'grid': '6'
            }]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-01',
            'round': '3',
            'Results': [{
                'position': '4',
                'points': '12',
                'status': 'Finished',
                'grid': '5'
            }]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-02-01',
            'round': '2',
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '4'
            }]
        },
        {
            'raceName': 'Race 1',
            'date': '2024-01-01',
            'round': '1',
            'Results': [{
                'position': '2',  # Oldest - best position
                'points': '18',
                'status': 'Finished',
                'grid': '3'
            }]
        }
    ]
    
    form = calculate_analytics_form_indicator(race_results, n_races=5)
    
    print(f"✓ Form data: {form}")
    assert form is not None, "Should return form data"
    assert form['races_analyzed'] == 5, "Should analyze 5 races"
    assert form['trend_direction'] == 'improving', "Trend should be improving (positions getting lower)"
    assert form['trend_slope'] < 0, "Slope should be negative for improving trend"
    
    # Positions are [6, 5, 4, 3, 2] in order (improving from 6 to 2)
    expected_avg = (6 + 5 + 4 + 3 + 2) / 5
    expected_points = 8 + 10 + 12 + 15 + 18
    
    assert abs(form['avg_position'] - expected_avg) < 0.01, \
        f"Average position should be {expected_avg}, got {form['avg_position']}"
    assert abs(form['total_points'] - expected_points) < 0.1, \
        f"Total points should be {expected_points}, got {form['total_points']}"
    
    print("✅ Improving trend test passed!")


def test_form_indicator_declining_trend():
    """Test form indicator with declining trend."""
    print("\n=== Testing Form Indicator with Declining Trend ===")
    
    # Create race results with declining positions (getting worse over time)
    # Most recent races first, with positions declining (getting higher)
    race_results = [
        {
            'raceName': 'Race 5',
            'date': '2024-05-01',
            'round': '5',
            'Results': [{
                'position': '2',  # Most recent - best position
                'points': '18',
                'status': 'Finished',
                'grid': '1'
            }]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-04-01',
            'round': '4',
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '2'
            }]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-01',
            'round': '3',
            'Results': [{
                'position': '4',
                'points': '12',
                'status': 'Finished',
                'grid': '3'
            }]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-02-01',
            'round': '2',
            'Results': [{
                'position': '6',
                'points': '8',
                'status': 'Finished',
                'grid': '5'
            }]
        },
        {
            'raceName': 'Race 1',
            'date': '2024-01-01',
            'round': '1',
            'Results': [{
                'position': '8',  # Oldest - worst position
                'points': '4',
                'status': 'Finished',
                'grid': '7'
            }]
        }
    ]
    
    form = calculate_analytics_form_indicator(race_results, n_races=5)
    
    print(f"✓ Form data: {form}")
    assert form is not None, "Should return form data"
    assert form['races_analyzed'] == 5, "Should analyze 5 races"
    assert form['trend_direction'] == 'declining', "Trend should be declining (positions getting higher)"
    assert form['trend_slope'] > 0, "Slope should be positive for declining trend"
    
    # Positions are [2, 3, 4, 6, 8] in order (declining from 2 to 8)
    expected_avg = (2 + 3 + 4 + 6 + 8) / 5
    expected_points = 18 + 15 + 12 + 8 + 4
    
    assert abs(form['avg_position'] - expected_avg) < 0.01, \
        f"Average position should be {expected_avg}, got {form['avg_position']}"
    assert abs(form['total_points'] - expected_points) < 0.1, \
        f"Total points should be {expected_points}, got {form['total_points']}"
    
    print("✅ Declining trend test passed!")


def test_form_indicator_stable_trend():
    """Test form indicator with stable trend."""
    print("\n=== Testing Form Indicator with Stable Trend ===")
    
    # Create race results with stable positions (small variations)
    race_results = [
        {
            'raceName': 'Race 5',
            'date': '2024-05-01',
            'round': '5',
            'Results': [{
                'position': '4',
                'points': '12',
                'status': 'Finished',
                'grid': '3'
            }]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-04-01',
            'round': '4',
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '4'
            }]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-01',
            'round': '3',
            'Results': [{
                'position': '4',
                'points': '12',
                'status': 'Finished',
                'grid': '5'
            }]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-02-01',
            'round': '2',
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '3'
            }]
        },
        {
            'raceName': 'Race 1',
            'date': '2024-01-01',
            'round': '1',
            'Results': [{
                'position': '4',
                'points': '12',
                'status': 'Finished',
                'grid': '4'
            }]
        }
    ]
    
    form = calculate_analytics_form_indicator(race_results, n_races=5)
    
    print(f"✓ Form data: {form}")
    assert form is not None, "Should return form data"
    assert form['races_analyzed'] == 5, "Should analyze 5 races"
    assert form['trend_direction'] == 'stable', "Trend should be stable (small slope)"
    assert abs(form['trend_slope']) < 0.3, "Slope should be small for stable trend"
    
    print("✅ Stable trend test passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Driver Analytics Calculations (Task 3.5)")
    print("=" * 60)
    
    try:
        test_consistency_score_perfect_consistency()
        test_consistency_score_excludes_dnf()
        test_dnf_rate_no_dnfs()
        test_dnf_rate_all_dnfs()
        test_dnf_cause_categorization()
        test_form_indicator_improving_trend()
        test_form_indicator_declining_trend()
        test_form_indicator_stable_trend()
        
        print("\n" + "=" * 60)
        print("✅ ALL DRIVER ANALYTICS UNIT TESTS PASSED!")
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
