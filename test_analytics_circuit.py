"""
Unit tests for circuit analytics calculations (Task 7.1).
Tests specific edge cases and examples for circuit analytics functions.
"""

import sys
import pandas as pd
from typing import Dict, Any

# Import the functions from app.py
from app import (
    calculate_analytics_circuit_performance,
    calculate_analytics_circuit_difficulty
)


def test_circuit_performance_basic():
    """Test circuit performance calculation with basic data."""
    print("\n=== Testing Circuit Performance with Basic Data ===")
    
    # Create race results for a driver at a specific circuit
    race_results = [
        {
            'raceName': 'Monaco Grand Prix',
            'date': '2022-05-29',
            'round': '7',
            'Circuit': {'circuitName': 'Monaco'},
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1'
            }]
        },
        {
            'raceName': 'Monaco Grand Prix',
            'date': '2023-05-28',
            'round': '6',
            'Circuit': {'circuitName': 'Monaco'},
            'Results': [{
                'position': '2',
                'points': '18',
                'status': 'Finished',
                'grid': '2'
            }]
        },
        {
            'raceName': 'Monaco Grand Prix',
            'date': '2024-05-26',
            'round': '8',
            'Circuit': {'circuitName': 'Monaco'},
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '3'
            }]
        }
    ]
    
    perf = calculate_analytics_circuit_performance(race_results, 'Monaco', min_appearances=3)
    
    print(f"✓ Circuit performance data: {perf}")
    assert perf is not None, "Should return performance data"
    assert perf['appearances'] == 3, "Should have 3 appearances"
    assert perf['avg_finish'] == 2.0, "Average finish should be 2.0 (1+2+3)/3"
    assert perf['win_rate'] == 33.3, "Win rate should be 33.3% (1 win in 3 races)"
    assert perf['podium_rate'] == 100.0, "Podium rate should be 100% (all 3 races)"
    assert perf['points_rate'] == 100.0, "Points rate should be 100% (all 3 races)"
    assert perf['low_sample_warning'] == False, "Should not have low sample warning with 3 races"
    
    print("✅ Basic circuit performance test passed!")


def test_circuit_performance_with_dnf():
    """Test circuit performance excludes DNF from average but counts in rates."""
    print("\n=== Testing Circuit Performance with DNF ===")
    
    # Create race results with a DNF
    race_results = [
        {
            'raceName': 'Silverstone Grand Prix',
            'date': '2022-07-03',
            'round': '10',
            'Circuit': {'circuitName': 'Silverstone'},
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1'
            }]
        },
        {
            'raceName': 'Silverstone Grand Prix',
            'date': '2023-07-09',
            'round': '11',
            'Circuit': {'circuitName': 'Silverstone'},
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Engine',  # DNF
                'grid': '2'
            }]
        },
        {
            'raceName': 'Silverstone Grand Prix',
            'date': '2024-07-07',
            'round': '12',
            'Circuit': {'circuitName': 'Silverstone'},
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '3'
            }]
        }
    ]
    
    perf = calculate_analytics_circuit_performance(race_results, 'Silverstone', min_appearances=3)
    
    print(f"✓ Circuit performance data: {perf}")
    assert perf is not None, "Should return performance data"
    assert perf['appearances'] == 3, "Should have 3 appearances"
    assert perf['avg_finish'] == 2.0, "Average finish should be 2.0 (only counting finished races: 1+3)/2"
    assert perf['win_rate'] == 33.3, "Win rate should be 33.3% (1 win in 3 races)"
    assert perf['podium_rate'] == 66.7, "Podium rate should be 66.7% (2 podiums in 3 races)"
    assert perf['points_rate'] == 66.7, "Points rate should be 66.7% (2 points finishes in 3 races)"
    
    print("✅ Circuit performance with DNF test passed!")


def test_circuit_performance_low_sample_warning():
    """Test low sample size warning."""
    print("\n=== Testing Circuit Performance Low Sample Warning ===")
    
    # Create race results with only 2 appearances (below minimum of 3)
    race_results = [
        {
            'raceName': 'Spa Grand Prix',
            'date': '2023-07-30',
            'round': '13',
            'Circuit': {'circuitName': 'Spa-Francorchamps'},
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1'
            }]
        },
        {
            'raceName': 'Spa Grand Prix',
            'date': '2024-07-28',
            'round': '14',
            'Circuit': {'circuitName': 'Spa-Francorchamps'},
            'Results': [{
                'position': '2',
                'points': '18',
                'status': 'Finished',
                'grid': '2'
            }]
        }
    ]
    
    perf = calculate_analytics_circuit_performance(race_results, 'Spa-Francorchamps', min_appearances=3)
    
    print(f"✓ Circuit performance data: {perf}")
    assert perf is not None, "Should return performance data"
    assert perf['appearances'] == 2, "Should have 2 appearances"
    assert perf['low_sample_warning'] == True, "Should have low sample warning with only 2 races"
    assert perf['avg_finish'] == 1.5, "Average finish should be 1.5"
    
    print("✅ Low sample warning test passed!")


def test_circuit_performance_no_data():
    """Test circuit performance with no data."""
    print("\n=== Testing Circuit Performance with No Data ===")
    
    perf = calculate_analytics_circuit_performance([], 'Monza', min_appearances=3)
    
    print(f"✓ Circuit performance data: {perf}")
    assert perf is not None, "Should return performance data"
    assert perf['appearances'] == 0, "Should have 0 appearances"
    assert perf['avg_finish'] is None, "Average finish should be None"
    assert perf['win_rate'] == 0.0, "Win rate should be 0.0"
    assert perf['podium_rate'] == 0.0, "Podium rate should be 0.0"
    assert perf['points_rate'] == 0.0, "Points rate should be 0.0"
    assert perf['low_sample_warning'] == True, "Should have low sample warning"
    
    print("✅ No data test passed!")


def test_circuit_difficulty_basic():
    """Test circuit difficulty calculation with basic data."""
    print("\n=== Testing Circuit Difficulty with Basic Data ===")
    
    # Create race data for multiple circuits
    all_races_data = [
        # Monaco - high difficulty (high DNF rate, position changes)
        {
            'raceName': 'Monaco Grand Prix',
            'date': '2023-05-28',
            'round': '6',
            'Circuit': {'circuitName': 'Monaco'},
            'Results': [
                {'position': '1', 'grid': '1', 'status': 'Finished'},
                {'position': '2', 'grid': '3', 'status': 'Finished'},
                {'position': 'R', 'grid': '2', 'status': 'Accident'},  # DNF
                {'position': '3', 'grid': '5', 'status': 'Finished'},
                {'position': 'R', 'grid': '4', 'status': 'Collision'},  # DNF
            ]
        },
        {
            'raceName': 'Monaco Grand Prix',
            'date': '2024-05-26',
            'round': '8',
            'Circuit': {'circuitName': 'Monaco'},
            'Results': [
                {'position': '1', 'grid': '2', 'status': 'Finished'},
                {'position': '2', 'grid': '1', 'status': 'Finished'},
                {'position': 'R', 'grid': '3', 'status': 'Engine'},  # DNF
                {'position': '3', 'grid': '6', 'status': 'Finished'},
                {'position': '4', 'grid': '4', 'status': 'Finished'},
            ]
        },
        # Monza - low difficulty (low DNF rate, fewer position changes)
        {
            'raceName': 'Italian Grand Prix',
            'date': '2023-09-03',
            'round': '14',
            'Circuit': {'circuitName': 'Monza'},
            'Results': [
                {'position': '1', 'grid': '1', 'status': 'Finished'},
                {'position': '2', 'grid': '2', 'status': 'Finished'},
                {'position': '3', 'grid': '3', 'status': 'Finished'},
                {'position': '4', 'grid': '4', 'status': 'Finished'},
                {'position': '5', 'grid': '5', 'status': 'Finished'},
            ]
        },
        {
            'raceName': 'Italian Grand Prix',
            'date': '2024-09-01',
            'round': '16',
            'Circuit': {'circuitName': 'Monza'},
            'Results': [
                {'position': '1', 'grid': '1', 'status': 'Finished'},
                {'position': '2', 'grid': '3', 'status': 'Finished'},
                {'position': '3', 'grid': '2', 'status': 'Finished'},
                {'position': '4', 'grid': '4', 'status': 'Finished'},
                {'position': '5', 'grid': '5', 'status': 'Finished'},
            ]
        }
    ]
    
    df = calculate_analytics_circuit_difficulty(all_races_data, ['2023', '2024'])
    
    print(f"✓ Circuit difficulty DataFrame:\n{df}")
    assert isinstance(df, pd.DataFrame), "Should return a DataFrame"
    assert len(df) == 2, "Should have 2 circuits"
    assert 'circuit_name' in df.columns, "Should have circuit_name column"
    assert 'dnf_rate' in df.columns, "Should have dnf_rate column"
    assert 'avg_position_change' in df.columns, "Should have avg_position_change column"
    assert 'difficulty_score' in df.columns, "Should have difficulty_score column"
    assert 'races_analyzed' in df.columns, "Should have races_analyzed column"
    
    # Check Monaco (should be more difficult)
    monaco = df[df['circuit_name'] == 'Monaco'].iloc[0]
    assert monaco['races_analyzed'] == 2, "Monaco should have 2 races"
    assert monaco['dnf_rate'] > 0, "Monaco should have DNFs"
    
    # Check Monza (should be less difficult)
    monza = df[df['circuit_name'] == 'Monza'].iloc[0]
    assert monza['races_analyzed'] == 2, "Monza should have 2 races"
    assert monza['dnf_rate'] == 0.0, "Monza should have no DNFs"
    
    # Monaco should be more difficult than Monza
    assert monaco['difficulty_score'] > monza['difficulty_score'], \
        "Monaco should have higher difficulty score than Monza"
    
    # DataFrame should be sorted by difficulty score (descending)
    assert df.iloc[0]['difficulty_score'] >= df.iloc[1]['difficulty_score'], \
        "DataFrame should be sorted by difficulty score descending"
    
    print("✅ Basic circuit difficulty test passed!")


def test_circuit_difficulty_empty_data():
    """Test circuit difficulty with empty data."""
    print("\n=== Testing Circuit Difficulty with Empty Data ===")
    
    df = calculate_analytics_circuit_difficulty([], [])
    
    print(f"✓ Circuit difficulty DataFrame:\n{df}")
    assert isinstance(df, pd.DataFrame), "Should return a DataFrame"
    assert len(df) == 0, "Should have 0 rows"
    assert 'circuit_name' in df.columns, "Should have circuit_name column"
    assert 'dnf_rate' in df.columns, "Should have dnf_rate column"
    assert 'avg_position_change' in df.columns, "Should have avg_position_change column"
    assert 'difficulty_score' in df.columns, "Should have difficulty_score column"
    
    print("✅ Empty data test passed!")


def test_circuit_difficulty_score_range():
    """Test that difficulty scores are in valid range (0-100)."""
    print("\n=== Testing Circuit Difficulty Score Range ===")
    
    # Create extreme data to test score boundaries
    all_races_data = [
        {
            'raceName': 'Test Circuit',
            'date': '2024-01-01',
            'round': '1',
            'Circuit': {'circuitName': 'Test Circuit'},
            'Results': [
                {'position': '1', 'grid': '20', 'status': 'Finished'},  # Large position change
                {'position': '2', 'grid': '19', 'status': 'Finished'},
                {'position': 'R', 'grid': '1', 'status': 'Accident'},  # DNF
                {'position': 'R', 'grid': '2', 'status': 'Engine'},  # DNF
                {'position': 'R', 'grid': '3', 'status': 'Collision'},  # DNF
            ]
        }
    ]
    
    df = calculate_analytics_circuit_difficulty(all_races_data, ['2024'])
    
    print(f"✓ Circuit difficulty DataFrame:\n{df}")
    assert len(df) == 1, "Should have 1 circuit"
    
    difficulty_score = df.iloc[0]['difficulty_score']
    print(f"✓ Difficulty score: {difficulty_score}")
    
    assert 0 <= difficulty_score <= 100, "Difficulty score should be between 0 and 100"
    
    print("✅ Difficulty score range test passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Circuit Analytics Calculations (Task 7.1)")
    print("=" * 60)
    
    try:
        test_circuit_performance_basic()
        test_circuit_performance_with_dnf()
        test_circuit_performance_low_sample_warning()
        test_circuit_performance_no_data()
        test_circuit_difficulty_basic()
        test_circuit_difficulty_empty_data()
        test_circuit_difficulty_score_range()
        
        print("\n" + "=" * 60)
        print("✅ ALL CIRCUIT ANALYTICS UNIT TESTS PASSED!")
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
