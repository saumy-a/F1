"""
Basic tests for analytics calculation functions.
Tests the four functions implemented in task 1.2.
"""

import sys
import pandas as pd
from typing import Dict, Any

# Import the functions from app.py
from app import (
    calculate_analytics_performance_trends,
    calculate_analytics_consistency_score,
    calculate_analytics_dnf_rate,
    calculate_analytics_points_per_race
)


def create_sample_race_results():
    """Create sample race results for testing."""
    return [
        {
            'raceName': 'Bahrain Grand Prix',
            'date': '2024-03-02',
            'round': '1',
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1'
            }]
        },
        {
            'raceName': 'Saudi Arabian Grand Prix',
            'date': '2024-03-09',
            'round': '2',
            'Results': [{
                'position': '2',
                'points': '18',
                'status': 'Finished',
                'grid': '2'
            }]
        },
        {
            'raceName': 'Australian Grand Prix',
            'date': '2024-03-24',
            'round': '3',
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1'
            }]
        },
        {
            'raceName': 'Japanese Grand Prix',
            'date': '2024-04-07',
            'round': '4',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Engine',
                'grid': '3'
            }]
        },
        {
            'raceName': 'Chinese Grand Prix',
            'date': '2024-04-21',
            'round': '5',
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '4'
            }]
        },
        {
            'raceName': 'Miami Grand Prix',
            'date': '2024-05-05',
            'round': '6',
            'Results': [{
                'position': '2',
                'points': '18',
                'status': 'Finished',
                'grid': '2'
            }]
        }
    ]


def test_performance_trends():
    """Test calculate_analytics_performance_trends function."""
    print("\n=== Testing Performance Trends ===")
    
    race_results = create_sample_race_results()
    
    # Test with position metric
    trends_position = calculate_analytics_performance_trends(race_results, metric="position")
    print(f"✓ Position trends DataFrame shape: {trends_position.shape}")
    print(f"✓ Columns: {list(trends_position.columns)}")
    assert len(trends_position) == 6, "Should have 6 races"
    assert 'race_name' in trends_position.columns
    assert 'metric_value' in trends_position.columns
    
    # Test with points metric
    trends_points = calculate_analytics_performance_trends(race_results, metric="points")
    print(f"✓ Points trends DataFrame shape: {trends_points.shape}")
    assert len(trends_points) == 6, "Should have 6 races"
    
    # Test with empty results
    empty_trends = calculate_analytics_performance_trends([])
    assert len(empty_trends) == 0, "Empty results should return empty DataFrame"
    
    print("✅ Performance trends tests passed!")


def test_consistency_score():
    """Test calculate_analytics_consistency_score function."""
    print("\n=== Testing Consistency Score ===")
    
    race_results = create_sample_race_results()
    
    # Test with sufficient data
    consistency = calculate_analytics_consistency_score(race_results, min_races=5)
    print(f"✓ Consistency score: {consistency}")
    assert consistency is not None, "Should return consistency data"
    assert 'consistency_score' in consistency
    assert 'std_dev' in consistency
    assert 'avg_position' in consistency
    assert 'completed_races' in consistency
    assert 'total_races' in consistency
    assert 0 <= consistency['consistency_score'] <= 100, "Score should be 0-100"
    assert consistency['completed_races'] == 5, "Should have 5 completed races (1 DNF)"
    assert consistency['total_races'] == 6, "Should have 6 total races"
    
    # Test with insufficient data
    insufficient_results = race_results[:3]
    consistency_insufficient = calculate_analytics_consistency_score(insufficient_results, min_races=5)
    # Note: This will show a warning but should return None
    
    print("✅ Consistency score tests passed!")


def test_dnf_rate():
    """Test calculate_analytics_dnf_rate function."""
    print("\n=== Testing DNF Rate ===")
    
    race_results = create_sample_race_results()
    
    # Test DNF rate calculation
    dnf_data = calculate_analytics_dnf_rate(race_results)
    print(f"✓ DNF data: {dnf_data}")
    assert 'dnf_percentage' in dnf_data
    assert 'dnf_count' in dnf_data
    assert 'total_races' in dnf_data
    assert 'dnf_causes' in dnf_data
    assert dnf_data['dnf_count'] == 1, "Should have 1 DNF"
    assert dnf_data['total_races'] == 6, "Should have 6 total races"
    assert 0 <= dnf_data['dnf_percentage'] <= 100, "Percentage should be 0-100"
    assert 'Mechanical' in dnf_data['dnf_causes'], "Should categorize Engine as Mechanical"
    
    # Test with no DNFs
    no_dnf_results = [r for r in race_results if r['Results'][0]['status'] == 'Finished']
    no_dnf_data = calculate_analytics_dnf_rate(no_dnf_results)
    assert no_dnf_data['dnf_count'] == 0, "Should have 0 DNFs"
    assert no_dnf_data['dnf_percentage'] == 0.0, "Percentage should be 0"
    
    print("✅ DNF rate tests passed!")


def test_points_per_race():
    """Test calculate_analytics_points_per_race function."""
    print("\n=== Testing Points Per Race ===")
    
    race_results = create_sample_race_results()
    
    # Test including all races
    points_all = calculate_analytics_points_per_race(race_results, exclude_dnf=False)
    print(f"✓ Points per race (all): {points_all}")
    assert 'points_per_race' in points_all
    assert 'total_points' in points_all
    assert 'races_counted' in points_all
    assert points_all['races_counted'] == 6, "Should count all 6 races"
    assert points_all['total_points'] == 101.0, "Total points should be 25+18+25+0+15+18=101"
    
    # Test excluding DNFs
    points_no_dnf = calculate_analytics_points_per_race(race_results, exclude_dnf=True)
    print(f"✓ Points per race (no DNF): {points_no_dnf}")
    assert points_no_dnf['races_counted'] == 5, "Should count 5 races (excluding 1 DNF)"
    assert points_no_dnf['total_points'] == 101.0, "Total points should still be 101"
    
    # Test with empty results
    empty_points = calculate_analytics_points_per_race([])
    assert empty_points['points_per_race'] == 0.0
    assert empty_points['races_counted'] == 0
    
    print("✅ Points per race tests passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Analytics Calculation Functions (Task 1.2)")
    print("=" * 60)
    
    try:
        test_performance_trends()
        test_consistency_score()
        test_dnf_rate()
        test_points_per_race()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
