"""
Test for task 3.1: Implement remaining driver analytics calculations.
Tests calculate_analytics_qualifying_race_correlation and calculate_analytics_form_indicator.
"""

import sys
from typing import Dict, Any

# Import the functions from app.py
from app import (
    calculate_analytics_qualifying_race_correlation,
    calculate_analytics_form_indicator
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
                'grid': '3'
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
                'grid': '2'
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
        },
        {
            'raceName': 'Monaco Grand Prix',
            'date': '2024-05-26',
            'round': '7',
            'Results': [{
                'position': '4',
                'points': '12',
                'status': 'Finished',
                'grid': '5'
            }]
        }
    ]


def test_qualifying_race_correlation():
    """Test calculate_analytics_qualifying_race_correlation function."""
    print("\n=== Testing Qualifying-Race Correlation ===")
    
    race_results = create_sample_race_results()
    
    # Test with sufficient data
    correlation = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    print(f"✓ Correlation data: {correlation}")
    
    assert correlation is not None, "Should return correlation data"
    assert 'correlation_coefficient' in correlation
    assert 'avg_position_change' in correlation
    assert 'classification' in correlation
    assert 'scatter_data' in correlation
    assert 'races_analyzed' in correlation
    
    # Check correlation coefficient is in valid range
    if correlation['correlation_coefficient'] is not None:
        assert -1 <= correlation['correlation_coefficient'] <= 1, "Correlation should be between -1 and 1"
    
    # Check classification is valid
    valid_classifications = [
        "strong race performer",
        "qualifying-dependent performer",
        "balanced performer",
        "insufficient data"
    ]
    assert correlation['classification'] in valid_classifications, f"Invalid classification: {correlation['classification']}"
    
    # Check scatter data structure
    assert len(correlation['scatter_data']) > 0, "Should have scatter data points"
    for point in correlation['scatter_data']:
        assert 'grid' in point
        assert 'finish' in point
        assert 'race_name' in point
    
    # Check that DNFs are excluded (we have 6 finished races, 1 DNF)
    assert correlation['races_analyzed'] == 6, "Should analyze 6 finished races (excluding 1 DNF)"
    
    print(f"  - Correlation coefficient: {correlation['correlation_coefficient']}")
    print(f"  - Avg position change: {correlation['avg_position_change']}")
    print(f"  - Classification: {correlation['classification']}")
    print(f"  - Races analyzed: {correlation['races_analyzed']}")
    
    # Test with insufficient data
    insufficient_results = race_results[:3]
    correlation_insufficient = calculate_analytics_qualifying_race_correlation(insufficient_results, min_races=5)
    assert correlation_insufficient is not None, "Should return a dict even with insufficient data"
    assert correlation_insufficient.get('insufficient_data') == True, "Should flag insufficient data"
    assert correlation_insufficient['races_analyzed'] < 5, "Should have fewer than 5 races analyzed"
    
    # Test with empty results
    empty_correlation = calculate_analytics_qualifying_race_correlation([])
    assert empty_correlation is None, "Should return None with empty results"
    
    print("✅ Qualifying-race correlation tests passed!")


def test_form_indicator():
    """Test calculate_analytics_form_indicator function."""
    print("\n=== Testing Form Indicator ===")
    
    race_results = create_sample_race_results()
    
    # Test with default n_races=5
    form = calculate_analytics_form_indicator(race_results, n_races=5)
    print(f"✓ Form indicator data: {form}")
    
    assert form is not None, "Should return form data"
    assert 'avg_position' in form
    assert 'total_points' in form
    assert 'trend_direction' in form
    assert 'trend_slope' in form
    assert 'races_analyzed' in form
    
    # Check trend direction is valid
    valid_trends = ["improving", "declining", "stable"]
    assert form['trend_direction'] in valid_trends, f"Invalid trend direction: {form['trend_direction']}"
    
    # Check that races_analyzed is correct (should be <= n_races and exclude DNFs)
    assert form['races_analyzed'] <= 5, "Should analyze at most 5 races"
    assert form['races_analyzed'] > 0, "Should analyze at least 1 race"
    
    print(f"  - Avg position: {form['avg_position']}")
    print(f"  - Total points: {form['total_points']}")
    print(f"  - Trend direction: {form['trend_direction']}")
    print(f"  - Trend slope: {form['trend_slope']}")
    print(f"  - Races analyzed: {form['races_analyzed']}")
    
    # Test trend classification logic
    # Create improving trend (positions getting better/lower)
    improving_results = [
        {
            'raceName': f'Race {i}',
            'Results': [{
                'position': str(5 - i),  # 5, 4, 3, 2, 1
                'points': str(10 + i * 5),
                'status': 'Finished'
            }]
        }
        for i in range(5)
    ]
    form_improving = calculate_analytics_form_indicator(improving_results, n_races=5)
    print(f"\n✓ Improving trend test:")
    print(f"  - Trend direction: {form_improving['trend_direction']}")
    print(f"  - Trend slope: {form_improving['trend_slope']}")
    # Slope should be negative (positions decreasing = improving)
    assert form_improving['trend_slope'] < 0, "Improving trend should have negative slope"
    
    # Create declining trend (positions getting worse/higher)
    declining_results = [
        {
            'raceName': f'Race {i}',
            'Results': [{
                'position': str(1 + i),  # 1, 2, 3, 4, 5
                'points': str(25 - i * 5),
                'status': 'Finished'
            }]
        }
        for i in range(5)
    ]
    form_declining = calculate_analytics_form_indicator(declining_results, n_races=5)
    print(f"\n✓ Declining trend test:")
    print(f"  - Trend direction: {form_declining['trend_direction']}")
    print(f"  - Trend slope: {form_declining['trend_slope']}")
    # Slope should be positive (positions increasing = declining)
    assert form_declining['trend_slope'] > 0, "Declining trend should have positive slope"
    
    # Test with empty results
    empty_form = calculate_analytics_form_indicator([])
    assert empty_form is None, "Should return None with empty results"
    
    print("\n✅ Form indicator tests passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Task 3.1: Remaining Driver Analytics Calculations")
    print("=" * 60)
    
    try:
        test_qualifying_race_correlation()
        test_form_indicator()
        
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
