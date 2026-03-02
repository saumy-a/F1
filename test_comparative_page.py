"""
Unit tests for comparative analytics page implementation.
"""

import sys
sys.path.insert(0, '.')

import pandas as pd
from typing import Dict, Any

# Import functions from app
from app import (
    calculate_analytics_multi_driver_comparison,
    calculate_analytics_season_comparison,
    calculate_analytics_percentile_rankings,
    create_analytics_radar_chart,
    create_analytics_grouped_bar_chart,
    create_analytics_horizontal_percentile_chart
)


def test_multi_driver_comparison_with_sample_data():
    """Test multi-driver comparison with sample race data."""
    # Create sample race data for 3 drivers
    driver1_results = [
        {
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1'
            }]
        },
        {
            'Results': [{
                'position': '2',
                'points': '18',
                'status': 'Finished',
                'grid': '2'
            }]
        },
        {
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1'
            }]
        },
        {
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '3'
            }]
        },
        {
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '2'
            }]
        }
    ]
    
    driver2_results = [
        {
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '3'
            }]
        },
        {
            'Results': [{
                'position': '4',
                'points': '12',
                'status': 'Finished',
                'grid': '4'
            }]
        },
        {
            'Results': [{
                'position': '5',
                'points': '10',
                'status': 'Finished',
                'grid': '5'
            }]
        },
        {
            'Results': [{
                'position': '4',
                'points': '12',
                'status': 'Finished',
                'grid': '4'
            }]
        },
        {
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '3'
            }]
        }
    ]
    
    driver3_results = [
        {
            'Results': [{
                'position': '5',
                'points': '10',
                'status': 'Finished',
                'grid': '6'
            }]
        },
        {
            'Results': [{
                'position': '6',
                'points': '8',
                'status': 'Finished',
                'grid': '7'
            }]
        },
        {
            'Results': [{
                'position': 'R',
                'points': '0',
                'status': 'Engine',
                'grid': '5'
            }]
        },
        {
            'Results': [{
                'position': '7',
                'points': '6',
                'status': 'Finished',
                'grid': '8'
            }]
        },
        {
            'Results': [{
                'position': '5',
                'points': '10',
                'status': 'Finished',
                'grid': '6'
            }]
        }
    ]
    
    drivers_data = {
        'Driver A': driver1_results,
        'Driver B': driver2_results,
        'Driver C': driver3_results
    }
    
    # Calculate comparison
    comparison_df = calculate_analytics_multi_driver_comparison(drivers_data)
    
    # Verify results
    assert not comparison_df.empty, "Comparison DataFrame should not be empty"
    assert len(comparison_df) == 3, "Should have 3 drivers"
    assert 'driver_name' in comparison_df.columns, "Should have driver_name column"
    assert 'avg_finish' in comparison_df.columns, "Should have avg_finish column"
    assert 'points_per_race' in comparison_df.columns, "Should have points_per_race column"
    assert 'consistency_score' in comparison_df.columns, "Should have consistency_score column"
    assert 'dnf_rate' in comparison_df.columns, "Should have dnf_rate column"
    
    # Verify Driver A has best average finish
    driver_a_row = comparison_df[comparison_df['driver_name'] == 'Driver A']
    assert not driver_a_row.empty, "Driver A should be in results"
    assert driver_a_row['avg_finish'].values[0] < 2.0, "Driver A should have avg finish < 2.0"
    
    # Verify Driver C has DNF
    driver_c_row = comparison_df[comparison_df['driver_name'] == 'Driver C']
    assert not driver_c_row.empty, "Driver C should be in results"
    assert driver_c_row['dnf_rate'].values[0] > 0, "Driver C should have DNF rate > 0"
    
    print("✓ Multi-driver comparison test passed")


def test_season_comparison_with_sample_data():
    """Test season-over-season comparison with sample data."""
    # Create sample race data for 2 seasons
    season_2023_results = [
        {
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '3'
            }]
        },
        {
            'Results': [{
                'position': '4',
                'points': '12',
                'status': 'Finished',
                'grid': '4'
            }]
        },
        {
            'Results': [{
                'position': '5',
                'points': '10',
                'status': 'Finished',
                'grid': '5'
            }]
        },
        {
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '3'
            }]
        },
        {
            'Results': [{
                'position': '4',
                'points': '12',
                'status': 'Finished',
                'grid': '4'
            }]
        }
    ]
    
    season_2024_results = [
        {
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1'
            }]
        },
        {
            'Results': [{
                'position': '2',
                'points': '18',
                'status': 'Finished',
                'grid': '2'
            }]
        },
        {
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '1'
            }]
        },
        {
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished',
                'grid': '3'
            }]
        },
        {
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished',
                'grid': '2'
            }]
        }
    ]
    
    entity_results_by_season = {
        '2023': season_2023_results,
        '2024': season_2024_results
    }
    
    # Calculate season comparison
    comparison_df = calculate_analytics_season_comparison(entity_results_by_season)
    
    # Verify results
    assert not comparison_df.empty, "Comparison DataFrame should not be empty"
    assert len(comparison_df) == 2, "Should have 2 seasons"
    assert 'season' in comparison_df.columns, "Should have season column"
    assert 'avg_finish' in comparison_df.columns, "Should have avg_finish column"
    assert 'total_points' in comparison_df.columns, "Should have total_points column"
    assert 'points_per_race' in comparison_df.columns, "Should have points_per_race column"
    assert 'yoy_change_pct' in comparison_df.columns, "Should have yoy_change_pct column"
    
    # Verify 2024 has better performance than 2023
    season_2023_row = comparison_df[comparison_df['season'] == '2023']
    season_2024_row = comparison_df[comparison_df['season'] == '2024']
    
    assert not season_2023_row.empty, "2023 season should be in results"
    assert not season_2024_row.empty, "2024 season should be in results"
    
    assert season_2024_row['points_per_race'].values[0] > season_2023_row['points_per_race'].values[0], \
        "2024 should have higher points per race than 2023"
    
    # Verify YoY change is calculated for 2024
    assert pd.notna(season_2024_row['yoy_change_pct'].values[0]), "2024 should have YoY change"
    assert season_2024_row['yoy_change_pct'].values[0] > 0, "2024 should have positive YoY change"
    
    print("✓ Season comparison test passed")


def test_percentile_rankings_with_sample_data():
    """Test percentile rankings calculation with sample data."""
    # Create sample race data for target driver
    target_driver_results = [
        {
            'Results': [{
                'position': '2',
                'points': '18',
                'status': 'Finished'
            }]
        },
        {
            'Results': [{
                'position': '3',
                'points': '15',
                'status': 'Finished'
            }]
        },
        {
            'Results': [{
                'position': '2',
                'points': '18',
                'status': 'Finished'
            }]
        },
        {
            'Results': [{
                'position': '1',
                'points': '25',
                'status': 'Finished'
            }]
        },
        {
            'Results': [{
                'position': '2',
                'points': '18',
                'status': 'Finished'
            }]
        }
    ]
    
    # Create sample data for all drivers (5 drivers total)
    all_drivers_results = {
        'Target Driver': target_driver_results,
        'Driver A': [
            {'Results': [{'position': '1', 'points': '25', 'status': 'Finished'}]},
            {'Results': [{'position': '1', 'points': '25', 'status': 'Finished'}]},
            {'Results': [{'position': '1', 'points': '25', 'status': 'Finished'}]},
            {'Results': [{'position': '1', 'points': '25', 'status': 'Finished'}]},
            {'Results': [{'position': '1', 'points': '25', 'status': 'Finished'}]}
        ],
        'Driver B': [
            {'Results': [{'position': '5', 'points': '10', 'status': 'Finished'}]},
            {'Results': [{'position': '6', 'points': '8', 'status': 'Finished'}]},
            {'Results': [{'position': '5', 'points': '10', 'status': 'Finished'}]},
            {'Results': [{'position': '7', 'points': '6', 'status': 'Finished'}]},
            {'Results': [{'position': '5', 'points': '10', 'status': 'Finished'}]}
        ],
        'Driver C': [
            {'Results': [{'position': '8', 'points': '4', 'status': 'Finished'}]},
            {'Results': [{'position': '9', 'points': '2', 'status': 'Finished'}]},
            {'Results': [{'position': '10', 'points': '1', 'status': 'Finished'}]},
            {'Results': [{'position': '8', 'points': '4', 'status': 'Finished'}]},
            {'Results': [{'position': '9', 'points': '2', 'status': 'Finished'}]}
        ],
        'Driver D': [
            {'Results': [{'position': '12', 'points': '0', 'status': 'Finished'}]},
            {'Results': [{'position': '13', 'points': '0', 'status': 'Finished'}]},
            {'Results': [{'position': '14', 'points': '0', 'status': 'Finished'}]},
            {'Results': [{'position': '12', 'points': '0', 'status': 'Finished'}]},
            {'Results': [{'position': '13', 'points': '0', 'status': 'Finished'}]}
        ]
    }
    
    # Calculate percentile rankings
    percentiles = calculate_analytics_percentile_rankings(
        target_driver_results,
        all_drivers_results,
        '2024'
    )
    
    # Verify results
    assert 'avg_finish_percentile' in percentiles, "Should have avg_finish_percentile"
    assert 'points_percentile' in percentiles, "Should have points_percentile"
    assert 'consistency_percentile' in percentiles, "Should have consistency_percentile"
    assert 'field_size' in percentiles, "Should have field_size"
    
    assert percentiles['field_size'] == 5, "Should have 5 drivers in field"
    
    # Target driver should be in upper percentiles (better than most)
    assert 0 <= percentiles['avg_finish_percentile'] <= 100, "Percentile should be 0-100"
    assert 0 <= percentiles['points_percentile'] <= 100, "Percentile should be 0-100"
    assert 0 <= percentiles['consistency_percentile'] <= 100, "Percentile should be 0-100"
    
    # Target driver (avg finish ~2) should be better than drivers with avg finish > 5
    assert percentiles['avg_finish_percentile'] > 50, "Target driver should be above 50th percentile for finish"
    assert percentiles['points_percentile'] > 50, "Target driver should be above 50th percentile for points"
    
    print("✓ Percentile rankings test passed")


def test_radar_chart_creation():
    """Test radar chart creation with sample data."""
    # Create sample comparison data
    comparison_data = pd.DataFrame({
        'driver_name': ['Driver A', 'Driver B', 'Driver C'],
        'Finishing Position': [90.0, 75.0, 60.0],
        'Points Scoring': [85.0, 70.0, 55.0],
        'Consistency': [92.0, 78.0, 65.0],
        'Reliability': [88.0, 72.0, 58.0]
    })
    
    metrics = ['Finishing Position', 'Points Scoring', 'Consistency', 'Reliability']
    entity_names = ['Driver A', 'Driver B', 'Driver C']
    
    # Create radar chart
    fig = create_analytics_radar_chart(comparison_data, metrics, entity_names)
    
    # Verify chart was created
    assert fig is not None, "Figure should be created"
    assert len(fig.data) > 0, "Figure should have traces"
    
    print("✓ Radar chart creation test passed")


def test_grouped_bar_chart_creation():
    """Test grouped bar chart creation with sample data."""
    # Create sample comparison data
    comparison_data = pd.DataFrame({
        'driver_name': ['Driver A', 'Driver B', 'Driver C'],
        'avg_finish': [1.5, 3.8, 6.2],
        'points_per_race': [22.5, 15.3, 8.7],
        'consistency_score': [92.0, 78.0, 65.0]
    })
    
    # Create grouped bar chart
    fig = create_analytics_grouped_bar_chart(
        comparison_data,
        'driver_name',
        ['avg_finish', 'points_per_race', 'consistency_score'],
        "Driver Performance Metrics"
    )
    
    # Verify chart was created
    assert fig is not None, "Figure should be created"
    assert len(fig.data) > 0, "Figure should have traces"
    
    print("✓ Grouped bar chart creation test passed")


def test_horizontal_percentile_chart_creation():
    """Test horizontal percentile chart creation with sample data."""
    percentile_data = {
        'Avg Finish': 85.5,
        'Points Scored': 78.3,
        'Consistency': 92.1
    }
    
    # Create horizontal percentile chart
    fig = create_analytics_horizontal_percentile_chart(percentile_data, "Test Driver")
    
    # Verify chart was created
    assert fig is not None, "Figure should be created"
    assert len(fig.data) > 0, "Figure should have traces"
    
    print("✓ Horizontal percentile chart creation test passed")


if __name__ == "__main__":
    print("Running comparative analytics page tests...\n")
    
    test_multi_driver_comparison_with_sample_data()
    test_season_comparison_with_sample_data()
    test_percentile_rankings_with_sample_data()
    test_radar_chart_creation()
    test_grouped_bar_chart_creation()
    test_horizontal_percentile_chart_creation()
    
    print("\n✅ All comparative analytics page tests passed!")
