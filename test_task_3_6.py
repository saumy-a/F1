"""
Test for task 3.6: Add error handling for driver analytics.

Tests error handling for:
- Insufficient data errors (< 5 races)
- Missing qualifying or race data
- User-friendly error messages
"""

import pytest
from app import (
    calculate_analytics_consistency_score,
    calculate_analytics_qualifying_race_correlation,
    calculate_analytics_performance_trends,
    calculate_analytics_form_indicator,
)


def test_consistency_score_insufficient_data():
    """Test consistency score with insufficient completed races."""
    print("\n=== Testing Consistency Score - Insufficient Data ===")
    
    # Test with fewer than 5 completed races
    race_results = [
        {
            'Results': [{
                'position': '1',
                'status': 'Finished',
                'points': '25'
            }]
        },
        {
            'Results': [{
                'position': '2',
                'status': 'Finished',
                'points': '18'
            }]
        },
        {
            'Results': [{
                'position': 'R',
                'status': 'Engine',
                'points': '0'
            }]
        },
    ]
    
    result = calculate_analytics_consistency_score(race_results, min_races=5)
    assert result is None, "Should return None with insufficient data"
    print("✓ Returns None when fewer than 5 completed races")
    
    # Test with empty race results
    result_empty = calculate_analytics_consistency_score([], min_races=5)
    assert result_empty is None, "Should return None with empty data"
    print("✓ Returns None with empty race results")


def test_correlation_missing_qualifying_data():
    """Test correlation analysis with missing qualifying data."""
    print("\n=== Testing Correlation - Missing Qualifying Data ===")
    
    # Create race results with some missing qualifying data
    race_results = [
        {
            'raceName': 'Race 1',
            'Results': [{
                'grid': '1',
                'position': '1',
                'status': 'Finished'
            }]
        },
        {
            'raceName': 'Race 2',
            'Results': [{
                'grid': None,  # Missing qualifying data
                'position': '2',
                'status': 'Finished'
            }]
        },
        {
            'raceName': 'Race 3',
            'Results': [{
                'grid': '3',
                'position': None,  # Missing race result
                'status': 'Finished'
            }]
        },
        {
            'raceName': 'Race 4',
            'Results': [{
                'grid': '2',
                'position': '3',
                'status': 'Finished'
            }]
        },
        {
            'raceName': 'Race 5',
            'Results': [{
                'grid': '4',
                'position': '4',
                'status': 'Finished'
            }]
        },
    ]
    
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    # Should return insufficient data because only 3 races have complete data
    assert result is not None, "Should return a dict"
    assert result.get('insufficient_data') == True, "Should flag insufficient data"
    assert result.get('missing_data_count') == 2, "Should track 2 races with missing data"
    assert result.get('races_analyzed') == 3, "Should only analyze 3 races with complete data"
    
    print(f"✓ Tracks missing data count: {result['missing_data_count']}")
    print(f"✓ Analyzes only complete races: {result['races_analyzed']}")
    print(f"✓ Flags insufficient data: {result['insufficient_data']}")


def test_correlation_with_dnfs():
    """Test correlation analysis excludes DNFs but tracks them."""
    print("\n=== Testing Correlation - DNF Handling ===")
    
    race_results = [
        {
            'raceName': 'Race 1',
            'Results': [{
                'grid': '1',
                'position': '1',
                'status': 'Finished'
            }]
        },
        {
            'raceName': 'Race 2',
            'Results': [{
                'grid': '2',
                'position': 'R',
                'status': 'Engine'  # DNF
            }]
        },
        {
            'raceName': 'Race 3',
            'Results': [{
                'grid': '3',
                'position': '2',
                'status': 'Finished'
            }]
        },
        {
            'raceName': 'Race 4',
            'Results': [{
                'grid': '1',
                'position': '1',
                'status': 'Finished'
            }]
        },
        {
            'raceName': 'Race 5',
            'Results': [{
                'grid': '2',
                'position': '3',
                'status': 'Finished'
            }]
        },
        {
            'raceName': 'Race 6',
            'Results': [{
                'grid': '4',
                'position': '4',
                'status': 'Finished'
            }]
        },
    ]
    
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    assert result is not None, "Should return correlation data"
    assert result.get('insufficient_data') == False, "Should have sufficient data"
    assert result.get('races_analyzed') == 5, "Should analyze 5 finished races (excluding 1 DNF)"
    assert len(result.get('scatter_data', [])) == 5, "Should have 5 data points"
    
    print(f"✓ Excludes DNFs from analysis: {result['races_analyzed']} races analyzed")
    print(f"✓ Has sufficient data after excluding DNFs")


def test_performance_trends_empty_data():
    """Test performance trends with empty data."""
    print("\n=== Testing Performance Trends - Empty Data ===")
    
    result = calculate_analytics_performance_trends([], metric="position")
    
    # Should return empty DataFrame or None
    assert result is None or len(result) == 0, "Should handle empty data gracefully"
    print("✓ Handles empty data gracefully")


def test_form_indicator_fewer_than_n_races():
    """Test form indicator with fewer races than requested."""
    print("\n=== Testing Form Indicator - Fewer Races ===")
    
    # Only 3 races available, but requesting 5
    race_results = [
        {
            'Results': [{
                'position': '1',
                'status': 'Finished',
                'points': '25'
            }]
        },
        {
            'Results': [{
                'position': '2',
                'status': 'Finished',
                'points': '18'
            }]
        },
        {
            'Results': [{
                'position': '3',
                'status': 'Finished',
                'points': '15'
            }]
        },
    ]
    
    result = calculate_analytics_form_indicator(race_results, n_races=5)
    
    assert result is not None, "Should return form data"
    assert result.get('races_analyzed') == 3, "Should analyze all 3 available races"
    assert 'avg_position' in result
    assert 'total_points' in result
    assert 'trend_direction' in result
    
    print(f"✓ Analyzes available races: {result['races_analyzed']}")
    print(f"✓ Calculates trend with fewer races: {result['trend_direction']}")


def test_correlation_all_missing_data():
    """Test correlation when all races have missing data."""
    print("\n=== Testing Correlation - All Missing Data ===")
    
    race_results = [
        {
            'raceName': 'Race 1',
            'Results': [{
                'grid': None,
                'position': '1',
                'status': 'Finished'
            }]
        },
        {
            'raceName': 'Race 2',
            'Results': [{
                'grid': None,
                'position': '2',
                'status': 'Finished'
            }]
        },
    ]
    
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    assert result is not None, "Should return a dict"
    assert result.get('insufficient_data') == True, "Should flag insufficient data"
    assert result.get('races_analyzed') == 0, "Should have 0 races analyzed"
    assert result.get('missing_data_count') == 2, "Should track all missing data"
    
    print(f"✓ Handles all missing data: {result['missing_data_count']} races with missing data")
    print(f"✓ Flags insufficient data correctly")


def test_consistency_score_all_dnfs():
    """Test consistency score when all races are DNFs."""
    print("\n=== Testing Consistency Score - All DNFs ===")
    
    race_results = [
        {
            'Results': [{
                'position': 'R',
                'status': 'Engine',
                'points': '0'
            }]
        },
        {
            'Results': [{
                'position': 'R',
                'status': 'Accident',
                'points': '0'
            }]
        },
        {
            'Results': [{
                'position': 'R',
                'status': 'Gearbox',
                'points': '0'
            }]
        },
    ]
    
    result = calculate_analytics_consistency_score(race_results, min_races=5)
    
    assert result is None, "Should return None when no completed races"
    print("✓ Returns None when all races are DNFs")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing Task 3.6: Error Handling for Driver Analytics")
    print("=" * 60)
    
    try:
        test_consistency_score_insufficient_data()
        test_correlation_missing_qualifying_data()
        test_correlation_with_dnfs()
        test_performance_trends_empty_data()
        test_form_indicator_fewer_than_n_races()
        test_correlation_all_missing_data()
        test_consistency_score_all_dnfs()
        
        print("\n" + "=" * 60)
        print("✅ ALL ERROR HANDLING TESTS PASSED!")
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
    exit(run_all_tests())
