"""
Unit tests for analytics calculation functions.
"""

import pytest
import pandas as pd
from app.services.analytics import (
    calculate_performance_trends,
    calculate_consistency_score,
    calculate_dnf_rate,
    calculate_points_per_race,
    calculate_qualifying_race_correlation,
    calculate_form_indicator,
    calculate_team_reliability,
    calculate_constructor_development,
    calculate_driver_pairing,
    calculate_circuit_performance,
    calculate_circuit_difficulty,
    calculate_multi_driver_comparison,
    calculate_season_comparison,
    calculate_percentile_rankings,
    calculate_championship_projection,
)


def test_calculate_performance_trends_empty():
    """Test performance trends with empty data."""
    result = calculate_performance_trends([])
    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert list(result.columns) == ['race_name', 'race_date', 'round', 'metric_value']


def test_calculate_performance_trends_position():
    """Test performance trends with position metric."""
    race_results = [
        {
            'raceName': 'Monaco GP',
            'date': '2024-05-26',
            'round': '8',
            'Results': [{'position': '3', 'points': '15'}]
        },
        {
            'raceName': 'Spanish GP',
            'date': '2024-06-02',
            'round': '9',
            'Results': [{'position': '1', 'points': '25'}]
        }
    ]
    
    result = calculate_performance_trends(race_results, metric="position")
    assert len(result) == 2
    assert result.iloc[0]['metric_value'] == 3
    assert result.iloc[1]['metric_value'] == 1



def test_calculate_consistency_score_insufficient_data():
    """Test consistency score with insufficient data."""
    race_results = [
        {'Results': [{'position': '5', 'status': 'Finished'}]},
        {'Results': [{'position': '3', 'status': 'Finished'}]}
    ]
    
    result = calculate_consistency_score(race_results, min_races=5)
    assert result is None


def test_calculate_consistency_score_valid():
    """Test consistency score with valid data."""
    race_results = [
        {'Results': [{'position': str(i), 'status': 'Finished'}]}
        for i in [5, 4, 6, 5, 4]
    ]
    
    result = calculate_consistency_score(race_results, min_races=5)
    assert result is not None
    assert 'consistency_score' in result
    assert 'std_dev' in result
    assert 'avg_position' in result
    assert result['completed_races'] == 5


def test_calculate_dnf_rate_empty():
    """Test DNF rate with empty data."""
    result = calculate_dnf_rate([])
    assert result['dnf_percentage'] == 0.0
    assert result['dnf_count'] == 0
    assert result['total_races'] == 0


def test_calculate_dnf_rate_with_dnfs():
    """Test DNF rate with DNF data."""
    race_results = [
        {'Results': [{'status': 'Finished', 'position': '1'}]},
        {'Results': [{'status': 'Engine', 'position': 'R'}]},
        {'Results': [{'status': 'Accident', 'position': 'R'}]},
        {'Results': [{'status': 'Finished', 'position': '3'}]}
    ]
    
    result = calculate_dnf_rate(race_results)
    assert result['dnf_count'] == 2
    assert result['total_races'] == 4
    assert result['dnf_percentage'] == 50.0
    assert 'Mechanical' in result['dnf_causes']
    assert 'Accident' in result['dnf_causes']



def test_calculate_points_per_race():
    """Test points per race calculation."""
    race_results = [
        {'Results': [{'points': '25', 'status': 'Finished'}]},
        {'Results': [{'points': '18', 'status': 'Finished'}]},
        {'Results': [{'points': '0', 'status': 'Engine'}]},
        {'Results': [{'points': '15', 'status': 'Finished'}]}
    ]
    
    result = calculate_points_per_race(race_results, exclude_dnf=False)
    assert result['total_points'] == 58.0
    assert result['races_counted'] == 4
    assert result['points_per_race'] == 14.5
    
    # Test with DNF exclusion
    result_exclude = calculate_points_per_race(race_results, exclude_dnf=True)
    assert result_exclude['races_counted'] == 3
    assert result_exclude['points_per_race'] == round(58.0 / 3, 2)


def test_calculate_form_indicator():
    """Test form indicator calculation."""
    race_results = [
        {'Results': [{'position': '3', 'points': '15', 'status': 'Finished'}]},
        {'Results': [{'position': '2', 'points': '18', 'status': 'Finished'}]},
        {'Results': [{'position': '1', 'points': '25', 'status': 'Finished'}]}
    ]
    
    result = calculate_form_indicator(race_results, n_races=3)
    assert result is not None
    assert 'avg_position' in result
    assert 'total_points' in result
    assert 'trend_direction' in result
    assert result['trend_direction'] == 'improving'  # Positions getting better (lower)


def test_calculate_championship_projection():
    """Test championship projection calculation."""
    current_standings = [
        {
            'Driver': {'givenName': 'Max', 'familyName': 'Verstappen'},
            'points': '250',
            'position': '1'
        },
        {
            'Driver': {'givenName': 'Lewis', 'familyName': 'Hamilton'},
            'points': '200',
            'position': '2'
        }
    ]
    
    result = calculate_championship_projection(current_standings, remaining_races=5, year='2024')
    assert 'projections' in result
    assert 'remaining_races' in result
    assert result['remaining_races'] == 5
    assert len(result['projections']) == 2
    assert result['projections'][0]['driver_name'] == 'Max Verstappen'


def test_calculate_multi_driver_comparison():
    """Test multi-driver comparison."""
    drivers_data = {
        'Driver A': [
            {'Results': [{'position': '1', 'points': '25', 'status': 'Finished'}]},
            {'Results': [{'position': '2', 'points': '18', 'status': 'Finished'}]}
        ],
        'Driver B': [
            {'Results': [{'position': '3', 'points': '15', 'status': 'Finished'}]},
            {'Results': [{'position': '4', 'points': '12', 'status': 'Finished'}]}
        ]
    }
    
    result = calculate_multi_driver_comparison(drivers_data)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert 'driver_name' in result.columns
    assert 'avg_finish' in result.columns
    assert 'points_per_race' in result.columns
