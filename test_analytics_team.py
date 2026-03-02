"""
Unit tests for team analytics calculations (Task 5.1).
Tests specific edge cases and examples for team analytics functions.
"""

import sys
import numpy as np
import pandas as pd
from typing import Dict, Any

# Import the functions from app.py
from app import (
    calculate_analytics_team_reliability,
    calculate_analytics_constructor_development,
    calculate_analytics_driver_pairing
)


def test_team_reliability_both_drivers_finish():
    """Test team reliability when both drivers finish all races."""
    print("\n=== Testing Team Reliability with Both Drivers Finishing ===")
    
    # Create constructor results where both drivers finish every race
    constructor_results = []
    for i in range(5):
        constructor_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [
                {
                    'position': str(i+1),
                    'points': str(25 - i*5),
                    'status': 'Finished',
                    'grid': str(i+1),
                    'Driver': {'driverId': 'driver1'}
                },
                {
                    'position': str(i+2),
                    'points': str(20 - i*5),
                    'status': 'Finished',
                    'grid': str(i+2),
                    'Driver': {'driverId': 'driver2'}
                }
            ]
        })
    
    reliability = calculate_analytics_team_reliability(constructor_results, "2024")
    
    print(f"✓ Reliability data: {reliability}")
    assert reliability is not None, "Should return reliability data"
    assert reliability['both_finished_pct'] == 100.0, "Both drivers finished all races"
    assert reliability['total_races'] == 5, "Should have 5 total races"
    assert reliability['mechanical_dnf_rate'] == 0.0, "No mechanical DNFs"
    assert reliability['avg_finish_position'] > 0, "Should have average finish position"
    
    print("✅ Both drivers finish test passed!")


def test_team_reliability_with_mechanical_dnfs():
    """Test team reliability with mechanical DNFs."""
    print("\n=== Testing Team Reliability with Mechanical DNFs ===")
    
    # Create constructor results with mechanical DNFs
    constructor_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-01-01',
            'round': '1',
            'Results': [
                {
                    'position': '1',
                    'points': '25',
                    'status': 'Finished',
                    'grid': '1',
                    'Driver': {'driverId': 'driver1'}
                },
                {
                    'position': 'R',
                    'points': '0',
                    'status': 'Engine',  # Mechanical DNF
                    'grid': '2',
                    'Driver': {'driverId': 'driver2'}
                }
            ]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-02-01',
            'round': '2',
            'Results': [
                {
                    'position': 'R',
                    'points': '0',
                    'status': 'Gearbox',  # Mechanical DNF
                    'grid': '1',
                    'Driver': {'driverId': 'driver1'}
                },
                {
                    'position': '2',
                    'points': '18',
                    'status': 'Finished',
                    'grid': '3',
                    'Driver': {'driverId': 'driver2'}
                }
            ]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-01',
            'round': '3',
            'Results': [
                {
                    'position': '1',
                    'points': '25',
                    'status': 'Finished',
                    'grid': '1',
                    'Driver': {'driverId': 'driver1'}
                },
                {
                    'position': '3',
                    'points': '15',
                    'status': 'Finished',
                    'grid': '4',
                    'Driver': {'driverId': 'driver2'}
                }
            ]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-04-01',
            'round': '4',
            'Results': [
                {
                    'position': 'R',
                    'points': '0',
                    'status': 'Accident',  # Not mechanical
                    'grid': '2',
                    'Driver': {'driverId': 'driver1'}
                },
                {
                    'position': '4',
                    'points': '12',
                    'status': 'Finished',
                    'grid': '5',
                    'Driver': {'driverId': 'driver2'}
                }
            ]
        }
    ]
    
    reliability = calculate_analytics_team_reliability(constructor_results, "2024")
    
    print(f"✓ Reliability data: {reliability}")
    assert reliability is not None, "Should return reliability data"
    assert reliability['total_races'] == 4, "Should have 4 total races"
    assert reliability['both_finished_pct'] == 25.0, "Only 1 out of 4 races had both drivers finish (25%)"
    
    # Total driver entries = 8 (2 drivers × 4 races)
    # Mechanical DNFs = 2 (Engine, Gearbox)
    # Mechanical DNF rate = 2/8 * 100 = 25%
    assert reliability['mechanical_dnf_rate'] == 25.0, "Should have 25% mechanical DNF rate (2 out of 8 entries)"
    
    print("✅ Mechanical DNF test passed!")


def test_team_reliability_empty_results():
    """Test team reliability with empty results."""
    print("\n=== Testing Team Reliability with Empty Results ===")
    
    reliability = calculate_analytics_team_reliability([], "2024")
    
    print(f"✓ Reliability data: {reliability}")
    assert reliability is not None, "Should return reliability data"
    assert reliability['both_finished_pct'] == 0.0, "Should be 0% with no data"
    assert reliability['total_races'] == 0, "Should have 0 total races"
    assert reliability['mechanical_dnf_rate'] == 0.0, "Should be 0% with no data"
    
    print("✅ Empty results test passed!")


def test_constructor_development_improving_trend():
    """Test constructor development with improving trend."""
    print("\n=== Testing Constructor Development with Improving Trend ===")
    
    # Create constructor results with improving performance (more points over time)
    constructor_results = []
    for i in range(6):
        # Points increase over time: 10, 15, 20, 25, 30, 35
        points_driver1 = 5 + i * 2.5
        points_driver2 = 5 + i * 2.5
        
        constructor_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [
                {
                    'position': str(max(1, 10 - i)),
                    'points': str(points_driver1),
                    'status': 'Finished',
                    'grid': str(i+1),
                    'Driver': {'driverId': 'driver1'}
                },
                {
                    'position': str(max(1, 11 - i)),
                    'points': str(points_driver2),
                    'status': 'Finished',
                    'grid': str(i+2),
                    'Driver': {'driverId': 'driver2'}
                }
            ]
        })
    
    development = calculate_analytics_constructor_development(constructor_results, window_size=3)
    
    print(f"✓ Development data:\n{development}")
    assert development is not None, "Should return development data"
    assert len(development) == 6, "Should have 6 rows (one per race)"
    assert 'rolling_avg_points' in development.columns, "Should have rolling_avg_points column"
    assert 'rolling_avg_position' in development.columns, "Should have rolling_avg_position column"
    assert 'trend_classification' in development.columns, "Should have trend_classification column"
    
    # With improving points, trend should be "improving"
    assert development['trend_classification'].iloc[0] == 'improving', "Trend should be improving"
    
    # Check that rolling averages are calculated
    assert not development['rolling_avg_points'].isna().all(), "Should have some rolling average values"
    
    print("✅ Improving trend test passed!")


def test_constructor_development_declining_trend():
    """Test constructor development with declining trend."""
    print("\n=== Testing Constructor Development with Declining Trend ===")
    
    # Create constructor results with declining performance (fewer points over time)
    constructor_results = []
    for i in range(6):
        # Points decrease over time: 35, 30, 25, 20, 15, 10
        points_driver1 = 35 - i * 5
        points_driver2 = 0  # Second driver scores no points
        
        constructor_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [
                {
                    'position': str(i+1),
                    'points': str(points_driver1),
                    'status': 'Finished',
                    'grid': str(i+1),
                    'Driver': {'driverId': 'driver1'}
                },
                {
                    'position': str(i+10),
                    'points': str(points_driver2),
                    'status': 'Finished',
                    'grid': str(i+2),
                    'Driver': {'driverId': 'driver2'}
                }
            ]
        })
    
    development = calculate_analytics_constructor_development(constructor_results, window_size=3)
    
    print(f"✓ Development data:\n{development}")
    assert development is not None, "Should return development data"
    assert len(development) == 6, "Should have 6 rows (one per race)"
    
    # With declining points, trend should be "declining"
    assert development['trend_classification'].iloc[0] == 'declining', "Trend should be declining"
    
    print("✅ Declining trend test passed!")


def test_constructor_development_stable_trend():
    """Test constructor development with stable trend."""
    print("\n=== Testing Constructor Development with Stable Trend ===")
    
    # Create constructor results with stable performance (consistent points)
    constructor_results = []
    for i in range(6):
        # Points stay roughly the same: 20 ± 1
        points_driver1 = 10
        points_driver2 = 10
        
        constructor_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [
                {
                    'position': '5',
                    'points': str(points_driver1),
                    'status': 'Finished',
                    'grid': str(i+1),
                    'Driver': {'driverId': 'driver1'}
                },
                {
                    'position': '6',
                    'points': str(points_driver2),
                    'status': 'Finished',
                    'grid': str(i+2),
                    'Driver': {'driverId': 'driver2'}
                }
            ]
        })
    
    development = calculate_analytics_constructor_development(constructor_results, window_size=3)
    
    print(f"✓ Development data:\n{development}")
    assert development is not None, "Should return development data"
    assert len(development) == 6, "Should have 6 rows (one per race)"
    
    # With stable points, trend should be "stable"
    assert development['trend_classification'].iloc[0] == 'stable', "Trend should be stable"
    
    print("✅ Stable trend test passed!")


def test_constructor_development_empty_results():
    """Test constructor development with empty results."""
    print("\n=== Testing Constructor Development with Empty Results ===")
    
    development = calculate_analytics_constructor_development([], window_size=3)
    
    print(f"✓ Development data:\n{development}")
    assert development is not None, "Should return development data"
    assert len(development) == 0, "Should have 0 rows with no data"
    assert 'rolling_avg_points' in development.columns, "Should have rolling_avg_points column"
    
    print("✅ Empty results test passed!")


def test_driver_pairing_balanced():
    """Test driver pairing with balanced performance."""
    print("\n=== Testing Driver Pairing with Balanced Performance ===")
    
    # Create race results for two drivers with similar performance
    driver1_results = []
    driver2_results = []
    
    for i in range(5):
        driver1_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [{
                'position': str(i+1),
                'points': str(25 - i*5),
                'status': 'Finished',
                'grid': str(i+1),
                'Driver': {'driverId': 'driver1'}
            }]
        })
        
        driver2_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [{
                'position': str(i+2),
                'points': str(20 - i*5),
                'status': 'Finished',
                'grid': str(i+2),
                'Driver': {'driverId': 'driver2'}
            }]
        })
    
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    print(f"✓ Pairing data: {pairing}")
    assert pairing is not None, "Should return pairing data"
    assert pairing['balance_flag'] == 'balanced', "Should be balanced (not >70:30)"
    assert pairing['driver1_points'] > 0, "Driver 1 should have points"
    assert pairing['driver2_points'] > 0, "Driver 2 should have points"
    assert ':' in pairing['points_ratio'], "Points ratio should be in format X:Y"
    
    # Driver 1: 25+20+15+10+5 = 75 points
    # Driver 2: 20+15+10+5+0 = 50 points
    # Total: 125 points
    # Ratio: 60:40 (balanced)
    assert pairing['driver1_points'] == 75.0, "Driver 1 should have 75 points"
    assert pairing['driver2_points'] == 50.0, "Driver 2 should have 50 points"
    
    print("✅ Balanced pairing test passed!")


def test_driver_pairing_imbalanced():
    """Test driver pairing with imbalanced performance."""
    print("\n=== Testing Driver Pairing with Imbalanced Performance ===")
    
    # Create race results where one driver dominates
    driver1_results = []
    driver2_results = []
    
    for i in range(5):
        driver1_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [{
                'position': '1',  # Always wins
                'points': '25',
                'status': 'Finished',
                'grid': '1',
                'Driver': {'driverId': 'driver1'}
            }]
        })
        
        driver2_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [{
                'position': '10',  # Always 10th
                'points': '1',
                'status': 'Finished',
                'grid': '10',
                'Driver': {'driverId': 'driver2'}
            }]
        })
    
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    print(f"✓ Pairing data: {pairing}")
    assert pairing is not None, "Should return pairing data"
    assert pairing['balance_flag'] == 'imbalanced', "Should be imbalanced (>70:30)"
    
    # Driver 1: 25*5 = 125 points
    # Driver 2: 1*5 = 5 points
    # Total: 130 points
    # Ratio: 96.2:3.8 (highly imbalanced)
    assert pairing['driver1_points'] == 125.0, "Driver 1 should have 125 points"
    assert pairing['driver2_points'] == 5.0, "Driver 2 should have 5 points"
    
    print("✅ Imbalanced pairing test passed!")


def test_driver_pairing_with_gaps():
    """Test driver pairing gap calculations."""
    print("\n=== Testing Driver Pairing Gap Calculations ===")
    
    # Create race results with specific gaps
    driver1_results = []
    driver2_results = []
    
    for i in range(3):
        driver1_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1',
                'Driver': {'driverId': 'driver1'}
            }]
        })
        
        driver2_results.append({
            'raceName': f'Race {i+1}',
            'date': f'2024-0{i+1}-01',
            'round': str(i+1),
            'Results': [{
                'position': '4',  # 3 positions behind
                'points': '12',
                'status': 'Finished',
                'grid': '4',  # 3 positions behind in quali
                'Driver': {'driverId': 'driver2'}
            }]
        })
    
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    print(f"✓ Pairing data: {pairing}")
    assert pairing is not None, "Should return pairing data"
    
    # Qualifying gap: |1-4| = 3 positions (consistent across all races)
    # Race gap: |1-4| = 3 positions (consistent across all races)
    assert pairing['quali_gap'] == 3.0, "Average qualifying gap should be 3 positions"
    assert pairing['race_gap'] == 3.0, "Average race gap should be 3 positions"
    
    print("✅ Gap calculations test passed!")


def test_driver_pairing_with_dnfs():
    """Test driver pairing with DNFs (should exclude from gap calculations)."""
    print("\n=== Testing Driver Pairing with DNFs ===")
    
    # Create race results with some DNFs
    driver1_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-01-01',
            'round': '1',
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1',
                'Driver': {'driverId': 'driver1'}
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
                'grid': '1',
                'Driver': {'driverId': 'driver1'}
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
                'grid': '2',
                'Driver': {'driverId': 'driver1'}
            }]
        }
    ]
    
    driver2_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-01-01',
            'round': '1',
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '3',
                'Driver': {'driverId': 'driver2'}
            }]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-02-01',
            'round': '2',
            'Results': [{
                'position': '4',
                'points': '12',
                'status': 'Finished',
                'grid': '4',
                'Driver': {'driverId': 'driver2'}
            }]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-01',
            'round': '3',
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Accident',  # DNF
                'grid': '3',
                'Driver': {'driverId': 'driver2'}
            }]
        }
    ]
    
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    print(f"✓ Pairing data: {pairing}")
    assert pairing is not None, "Should return pairing data"
    
    # Points: Driver 1 = 25+0+18 = 43, Driver 2 = 15+12+0 = 27
    assert pairing['driver1_points'] == 43.0, "Driver 1 should have 43 points"
    assert pairing['driver2_points'] == 27.0, "Driver 2 should have 27 points"
    
    # Race gap should only count Race 1 (both finished)
    # Race 1: |1-3| = 2
    # Race 2: Driver 1 DNF (excluded)
    # Race 3: Driver 2 DNF (excluded)
    assert pairing['race_gap'] == 2.0, "Race gap should only count races where both finished"
    
    print("✅ DNF handling test passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Team Analytics Calculations (Task 5.1)")
    print("=" * 60)
    
    try:
        test_team_reliability_both_drivers_finish()
        test_team_reliability_with_mechanical_dnfs()
        test_team_reliability_empty_results()
        test_constructor_development_improving_trend()
        test_constructor_development_declining_trend()
        test_constructor_development_stable_trend()
        test_constructor_development_empty_results()
        test_driver_pairing_balanced()
        test_driver_pairing_imbalanced()
        test_driver_pairing_with_gaps()
        test_driver_pairing_with_dnfs()
        
        print("\n" + "=" * 60)
        print("✅ ALL TEAM ANALYTICS UNIT TESTS PASSED!")
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
