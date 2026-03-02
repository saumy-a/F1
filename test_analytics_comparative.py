"""
Unit tests for comparative analytics calculation functions.
Tests the three functions implemented in task 7.4.
"""

import sys
import pandas as pd
from typing import Dict, Any

# Import the functions from app.py
from app import (
    calculate_analytics_multi_driver_comparison,
    calculate_analytics_season_comparison,
    calculate_analytics_percentile_rankings
)


def create_sample_driver_results(driver_name: str, positions: list, points: list):
    """Create sample race results for a driver."""
    results = []
    for i, (pos, pts) in enumerate(zip(positions, points)):
        results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{(i%9)+1}-01',
            'round': str(i+1),
            'Results': [{
                'position': str(pos) if pos != 'R' else 'R',
                'points': str(pts),
                'status': 'Finished' if pos != 'R' else 'Engine',
                'grid': str((i % 10) + 1)
            }]
        })
    return results


def test_multi_driver_comparison():
    """Test calculate_analytics_multi_driver_comparison function."""
    print("\n=== Testing Multi-Driver Comparison ===")
    
    # Create sample data for 3 drivers
    drivers_data = {
        'Driver A': create_sample_driver_results('Driver A', [1, 2, 1, 3, 2], [25, 18, 25, 15, 18]),
        'Driver B': create_sample_driver_results('Driver B', [3, 4, 2, 5, 3], [15, 12, 18, 10, 15]),
        'Driver C': create_sample_driver_results('Driver C', [5, 6, 4, 7, 5], [10, 8, 12, 6, 10])
    }
    
    # Test with all default metrics
    comparison = calculate_analytics_multi_driver_comparison(drivers_data)
    print(f"✓ Comparison DataFrame shape: {comparison.shape}")
    print(f"✓ Columns: {list(comparison.columns)}")
    print(f"✓ Drivers: {list(comparison['driver_name'])}")
    
    assert len(comparison) == 3, "Should have 3 drivers"
    assert 'driver_name' in comparison.columns
    assert 'avg_finish' in comparison.columns
    assert 'points_per_race' in comparison.columns
    assert 'consistency_score' in comparison.columns
    assert 'dnf_rate' in comparison.columns
    
    # Verify Driver A has best average finish
    driver_a_row = comparison[comparison['driver_name'] == 'Driver A'].iloc[0]
    assert driver_a_row['avg_finish'] < 3, "Driver A should have avg finish < 3"
    assert driver_a_row['points_per_race'] > 15, "Driver A should have high points per race"
    
    # Test with specific metrics
    comparison_limited = calculate_analytics_multi_driver_comparison(
        drivers_data,
        metrics=['avg_finish', 'points_per_race']
    )
    assert 'avg_finish' in comparison_limited.columns
    assert 'points_per_race' in comparison_limited.columns
    
    # Test with empty data
    empty_comparison = calculate_analytics_multi_driver_comparison({})
    assert len(empty_comparison) == 0, "Empty data should return empty DataFrame"
    
    print("✅ Multi-driver comparison tests passed!")


def test_multi_driver_comparison_max_drivers():
    """Test multi-driver comparison with maximum 10 drivers."""
    print("\n=== Testing Multi-Driver Comparison with 10 Drivers ===")
    
    # Create sample data for 10 drivers (maximum supported)
    drivers_data = {}
    for i in range(10):
        driver_name = f'Driver {i+1}'
        # Create varied performance data
        positions = [i+1, i+2, i+1, i+3, i+2]
        points = [25-i*2, 18-i*2, 25-i*2, 15-i*2, 18-i*2]
        drivers_data[driver_name] = create_sample_driver_results(driver_name, positions, points)
    
    # Test with 10 drivers
    comparison = calculate_analytics_multi_driver_comparison(drivers_data)
    print(f"✓ Comparison DataFrame shape: {comparison.shape}")
    print(f"✓ Number of drivers: {len(comparison)}")
    
    assert len(comparison) == 10, "Should handle 10 drivers"
    assert 'driver_name' in comparison.columns
    assert 'avg_finish' in comparison.columns
    assert 'points_per_race' in comparison.columns
    assert 'consistency_score' in comparison.columns
    assert 'dnf_rate' in comparison.columns
    
    # Verify all driver names are present
    driver_names = list(comparison['driver_name'])
    for i in range(10):
        assert f'Driver {i+1}' in driver_names, f"Driver {i+1} should be in comparison"
    
    # Verify performance ordering (Driver 1 should be best)
    driver_1_row = comparison[comparison['driver_name'] == 'Driver 1'].iloc[0]
    driver_10_row = comparison[comparison['driver_name'] == 'Driver 10'].iloc[0]
    
    assert driver_1_row['avg_finish'] < driver_10_row['avg_finish'], \
        "Driver 1 should have better average finish than Driver 10"
    assert driver_1_row['points_per_race'] > driver_10_row['points_per_race'], \
        "Driver 1 should have more points per race than Driver 10"
    
    print("✅ Multi-driver comparison with 10 drivers test passed!")


def test_season_comparison():
    """Test calculate_analytics_season_comparison function."""
    print("\n=== Testing Season Comparison ===")
    
    # Create sample data for 3 seasons
    entity_results_by_season = {
        '2022': create_sample_driver_results('Driver', [3, 4, 2, 5, 3], [15, 12, 18, 10, 15]),
        '2023': create_sample_driver_results('Driver', [2, 3, 1, 4, 2], [18, 15, 25, 12, 18]),
        '2024': create_sample_driver_results('Driver', [1, 2, 1, 3, 1], [25, 18, 25, 15, 25])
    }
    
    # Test season comparison
    comparison = calculate_analytics_season_comparison(entity_results_by_season)
    print(f"✓ Season comparison DataFrame shape: {comparison.shape}")
    print(f"✓ Columns: {list(comparison.columns)}")
    print(f"✓ Seasons: {list(comparison['season'])}")
    
    assert len(comparison) == 3, "Should have 3 seasons"
    assert 'season' in comparison.columns
    assert 'avg_finish' in comparison.columns
    assert 'total_points' in comparison.columns
    assert 'points_per_race' in comparison.columns
    assert 'consistency_score' in comparison.columns
    assert 'yoy_change_pct' in comparison.columns
    assert 'normalized_points_per_race' in comparison.columns
    
    # Verify seasons are in chronological order
    assert comparison.iloc[0]['season'] == '2022'
    assert comparison.iloc[1]['season'] == '2023'
    assert comparison.iloc[2]['season'] == '2024'
    
    # Verify year-over-year changes
    # First season should have None for yoy_change
    assert comparison.iloc[0]['yoy_change_pct'] is None or pd.isna(comparison.iloc[0]['yoy_change_pct'])
    
    # 2023 should show improvement over 2022
    if comparison.iloc[1]['yoy_change_pct'] is not None:
        assert comparison.iloc[1]['yoy_change_pct'] > 0, "2023 should show improvement"
    
    # Test with constructor type
    comparison_constructor = calculate_analytics_season_comparison(
        entity_results_by_season,
        entity_type="constructor"
    )
    assert len(comparison_constructor) == 3, "Should work with constructor type"
    
    # Test with empty data
    empty_comparison = calculate_analytics_season_comparison({})
    assert len(empty_comparison) == 0, "Empty data should return empty DataFrame"
    
    print("✅ Season comparison tests passed!")


def test_percentile_rankings():
    """Test calculate_analytics_percentile_rankings function."""
    print("\n=== Testing Percentile Rankings ===")
    
    # Create sample data for multiple drivers
    all_drivers_results = {
        'Driver 1': create_sample_driver_results('Driver 1', [1, 2, 1, 3, 2], [25, 18, 25, 15, 18]),  # Best
        'Driver 2': create_sample_driver_results('Driver 2', [3, 4, 2, 5, 3], [15, 12, 18, 10, 15]),
        'Driver 3': create_sample_driver_results('Driver 3', [5, 6, 4, 7, 5], [10, 8, 12, 6, 10]),
        'Driver 4': create_sample_driver_results('Driver 4', [7, 8, 6, 9, 7], [6, 4, 8, 2, 6]),
        'Driver 5': create_sample_driver_results('Driver 5', [10, 11, 9, 12, 10], [1, 0, 2, 0, 1]),  # Worst
    }
    
    # Test percentile rankings for Driver 1 (best driver)
    driver1_results = all_drivers_results['Driver 1']
    percentiles = calculate_analytics_percentile_rankings(
        driver1_results,
        all_drivers_results,
        '2024'
    )
    
    print(f"✓ Percentile rankings: {percentiles}")
    
    assert 'avg_finish_percentile' in percentiles
    assert 'points_percentile' in percentiles
    assert 'consistency_percentile' in percentiles
    assert 'field_size' in percentiles
    
    # Verify percentiles are in valid range
    assert 0 <= percentiles['avg_finish_percentile'] <= 100
    assert 0 <= percentiles['points_percentile'] <= 100
    assert 0 <= percentiles['consistency_percentile'] <= 100
    
    # Driver 1 should have high percentiles (best performance)
    assert percentiles['avg_finish_percentile'] >= 60, "Best driver should have high avg_finish percentile"
    assert percentiles['points_percentile'] >= 60, "Best driver should have high points percentile"
    
    assert percentiles['field_size'] == 5, "Should have 5 drivers in field"
    
    # Test percentile rankings for Driver 5 (worst driver)
    driver5_results = all_drivers_results['Driver 5']
    percentiles_worst = calculate_analytics_percentile_rankings(
        driver5_results,
        all_drivers_results,
        '2024'
    )
    
    # Driver 5 should have low percentiles (worst performance)
    assert percentiles_worst['avg_finish_percentile'] <= 40, "Worst driver should have low avg_finish percentile"
    assert percentiles_worst['points_percentile'] <= 40, "Worst driver should have low points percentile"
    
    # Test with insufficient data
    insufficient_drivers = {
        'Driver 1': create_sample_driver_results('Driver 1', [1, 2], [25, 18])  # Only 2 races
    }
    percentiles_insufficient = calculate_analytics_percentile_rankings(
        insufficient_drivers['Driver 1'],
        insufficient_drivers,
        '2024'
    )
    # Should still return valid structure even with limited data
    assert 'field_size' in percentiles_insufficient
    
    # Test with empty data
    empty_percentiles = calculate_analytics_percentile_rankings([], {}, '2024')
    assert empty_percentiles['field_size'] == 0
    assert empty_percentiles['avg_finish_percentile'] == 0.0
    
    print("✅ Percentile rankings tests passed!")


def test_points_normalization():
    """Test points normalization for different scoring systems."""
    print("\n=== Testing Points Normalization ===")
    
    # Create data for pre-2010 season (10 points for win)
    old_season_results = {
        '2009': create_sample_driver_results('Driver', [1, 2, 1, 3, 2], [10, 8, 10, 6, 8])
    }
    
    # Create data for modern season (25 points for win)
    modern_season_results = {
        '2024': create_sample_driver_results('Driver', [1, 2, 1, 3, 2], [25, 18, 25, 15, 18])
    }
    
    # Combine for comparison
    combined_results = {**old_season_results, **modern_season_results}
    
    comparison = calculate_analytics_season_comparison(combined_results)
    
    print(f"✓ Normalized points comparison:")
    for _, row in comparison.iterrows():
        print(f"  Season {row['season']}: PPR={row['points_per_race']}, Normalized={row['normalized_points_per_race']}")
    
    # Verify normalization
    old_season_row = comparison[comparison['season'] == '2009'].iloc[0]
    modern_season_row = comparison[comparison['season'] == '2024'].iloc[0]
    
    # Old season points should be multiplied by 2.5
    expected_normalized = old_season_row['points_per_race'] * 2.5
    assert abs(old_season_row['normalized_points_per_race'] - expected_normalized) < 0.1, \
        "Pre-2010 points should be normalized by 2.5x"
    
    # Modern season points should remain unchanged
    assert modern_season_row['normalized_points_per_race'] == modern_season_row['points_per_race'], \
        "Modern season points should not be normalized"
    
    print("✅ Points normalization tests passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Comparative Analytics Functions (Task 7.4)")
    print("=" * 60)
    
    try:
        test_multi_driver_comparison()
        test_multi_driver_comparison_max_drivers()
        test_season_comparison()
        test_percentile_rankings()
        test_points_normalization()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
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
