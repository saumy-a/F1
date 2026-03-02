"""
Property-based tests for analytics calculation functions using Hypothesis.
These tests validate universal correctness properties across all valid inputs.
"""

import sys
import pandas as pd
from hypothesis import given, strategies as st, assume, settings
from hypothesis.strategies import composite
from typing import Dict, Any, List

# Import the functions from app.py
from app import (
    calculate_analytics_performance_trends,
    calculate_analytics_consistency_score,
    calculate_analytics_qualifying_race_correlation,
    calculate_analytics_form_indicator,
    create_analytics_trend_chart,
    calculate_analytics_circuit_performance,
    calculate_analytics_circuit_difficulty,
    calculate_analytics_multi_driver_comparison
)
import plotly.graph_objects as go
import numpy as np


# ============================================================================
# Test Data Generators (Strategies)
# ============================================================================

@composite
def race_result_strategy(draw):
    """
    Generate a single race result dictionary.
    
    Generates realistic F1 race result data with:
    - Race metadata (name, date, round)
    - Driver result (position, points, status, grid)
    """
    race_name = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
    # Generate date as string directly
    year = draw(st.integers(min_value=2000, max_value=2024))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))  # Use 28 to avoid invalid dates
    race_date = f"{year:04d}-{month:02d}-{day:02d}"
    race_round = draw(st.integers(min_value=1, max_value=24))
    
    # Generate position - either a valid position (1-20) or 'R' for retirement
    is_dnf = draw(st.booleans())
    if is_dnf:
        position = 'R'
        points = '0'
        status = draw(st.sampled_from(['Engine', 'Gearbox', 'Accident', 'Collision', 'Hydraulics', 'Electrical']))
    else:
        position_int = draw(st.integers(min_value=1, max_value=20))
        position = str(position_int)
        # Points based on position (simplified F1 points system)
        points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
        points = str(points_map.get(position_int, 0))
        status = 'Finished'
    
    grid = draw(st.integers(min_value=1, max_value=20))
    
    return {
        'raceName': race_name,
        'date': race_date,
        'round': str(race_round),
        'Results': [{
            'position': position,
            'points': points,
            'status': status,
            'grid': str(grid)
        }]
    }


@composite
def race_results_list_strategy(draw, min_races=0, max_races=24):
    """
    Generate a list of race results.
    
    Args:
        min_races: Minimum number of races
        max_races: Maximum number of races
    """
    num_races = draw(st.integers(min_value=min_races, max_value=max_races))
    races = [draw(race_result_strategy()) for _ in range(num_races)]
    
    # Ensure rounds are sequential and unique
    for i, race in enumerate(races):
        race['round'] = str(i + 1)
    
    return races


# ============================================================================
# Property 1: Performance Trends Calculation
# **Validates: Requirements 1.1, 1.2, 1.5**
# ============================================================================

@given(race_results=race_results_list_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_performance_trends_one_row_per_race(race_results):
    """
    Property: For any driver's race results, calculating performance trends
    should produce a DataFrame with exactly one row per race.
    
    **Validates: Requirements 1.1, 1.2, 1.5**
    """
    # Test with position metric
    trends_position = calculate_analytics_performance_trends(race_results, metric="position")
    
    # Property: One row per race
    assert len(trends_position) == len(race_results), \
        f"Expected {len(race_results)} rows, got {len(trends_position)}"
    
    # Test with points metric
    trends_points = calculate_analytics_performance_trends(race_results, metric="points")
    
    # Property: One row per race
    assert len(trends_points) == len(race_results), \
        f"Expected {len(race_results)} rows, got {len(trends_points)}"


@given(race_results=race_results_list_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_performance_trends_correct_columns(race_results):
    """
    Property: For any driver's race results, the performance trends DataFrame
    should have the correct columns: race_name, race_date, round, metric_value.
    
    **Validates: Requirements 1.1, 1.2, 1.5**
    """
    trends = calculate_analytics_performance_trends(race_results, metric="position")
    
    # Property: Correct columns exist
    expected_columns = {'race_name', 'race_date', 'round', 'metric_value'}
    actual_columns = set(trends.columns)
    
    assert expected_columns == actual_columns, \
        f"Expected columns {expected_columns}, got {actual_columns}"


@given(race_results=race_results_list_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_performance_trends_position_metric_values(race_results):
    """
    Property: For position metric, metric_value should be either a valid
    integer position (1-20) or None for DNFs.
    
    **Validates: Requirements 1.1, 1.5**
    """
    trends = calculate_analytics_performance_trends(race_results, metric="position")
    
    for idx, row in trends.iterrows():
        metric_value = row['metric_value']
        
        # Property: metric_value is either None (DNF) or a valid position
        if pd.notna(metric_value):
            assert isinstance(metric_value, (int, float)), \
                f"Position metric_value should be numeric, got {type(metric_value)}"
            assert 1 <= metric_value <= 20, \
                f"Position should be 1-20, got {metric_value}"


@given(race_results=race_results_list_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_performance_trends_points_metric_values(race_results):
    """
    Property: For points metric, metric_value should be a non-negative number.
    
    **Validates: Requirements 1.2, 1.5**
    """
    trends = calculate_analytics_performance_trends(race_results, metric="points")
    
    for idx, row in trends.iterrows():
        metric_value = row['metric_value']
        
        # Property: metric_value is non-negative
        assert metric_value >= 0, \
            f"Points should be non-negative, got {metric_value}"


@given(race_results=race_results_list_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_performance_trends_round_numbers_sequential(race_results):
    """
    Property: Round numbers in the output should match the input race rounds.
    
    **Validates: Requirements 1.1, 1.2, 1.5**
    """
    trends = calculate_analytics_performance_trends(race_results, metric="position")
    
    # Property: Round numbers match input
    for i, (race, trend_row) in enumerate(zip(race_results, trends.itertuples())):
        expected_round = int(race['round'])
        actual_round = trend_row.round
        
        assert expected_round == actual_round, \
            f"Race {i}: Expected round {expected_round}, got {actual_round}"


def test_property_performance_trends_empty_input():
    """
    Property: Empty input should produce an empty DataFrame with correct columns.
    
    **Validates: Requirements 1.1, 1.2, 1.5**
    """
    trends = calculate_analytics_performance_trends([], metric="position")
    
    # Property: Empty DataFrame with correct columns
    assert len(trends) == 0, "Empty input should produce empty DataFrame"
    
    expected_columns = {'race_name', 'race_date', 'round', 'metric_value'}
    actual_columns = set(trends.columns)
    
    assert expected_columns == actual_columns, \
        f"Expected columns {expected_columns}, got {actual_columns}"


# ============================================================================
# Property 2: Consistency Score Calculation
# **Validates: Requirements 2.1, 2.2, 2.3**
# ============================================================================

@composite
def race_results_with_min_finished_strategy(draw, min_finished=5, max_races=24):
    """
    Generate a list of race results with at least min_finished completed races.
    
    This ensures we have enough data for consistency score calculation.
    """
    # Generate at least min_finished races, up to max_races
    num_races = draw(st.integers(min_value=min_finished, max_value=max_races))
    races = []
    
    # Ensure we have at least min_finished finished races
    finished_count = 0
    for i in range(num_races):
        race = draw(race_result_strategy())
        race['round'] = str(i + 1)
        
        # Force some races to be finished if we haven't met the minimum
        if finished_count < min_finished and i < num_races:
            # Override to make it a finished race
            position_int = draw(st.integers(min_value=1, max_value=20))
            points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
            race['Results'][0]['position'] = str(position_int)
            race['Results'][0]['points'] = str(points_map.get(position_int, 0))
            race['Results'][0]['status'] = 'Finished'
            finished_count += 1
        elif race['Results'][0]['status'] == 'Finished':
            finished_count += 1
        
        races.append(race)
    
    return races


@given(race_results=race_results_with_min_finished_strategy(min_finished=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_consistency_score_range(race_results):
    """
    Property: For any set of race results with at least 5 completed races,
    the consistency score should be in the range 0-100.
    
    **Validates: Requirements 2.1, 2.2, 2.3**
    """
    result = calculate_analytics_consistency_score(race_results, min_races=5)
    
    # Should not be None since we have at least 5 finished races
    if result is not None:
        # Property: Consistency score is in range 0-100
        assert 0 <= result['consistency_score'] <= 100, \
            f"Consistency score should be 0-100, got {result['consistency_score']}"
        
        # Property: Standard deviation is non-negative
        assert result['std_dev'] >= 0, \
            f"Standard deviation should be non-negative, got {result['std_dev']}"
        
        # Property: Average position is positive
        assert result['avg_position'] > 0, \
            f"Average position should be positive, got {result['avg_position']}"
        
        # Property: Completed races is at least min_races
        assert result['completed_races'] >= 5, \
            f"Should have at least 5 completed races, got {result['completed_races']}"
        
        # Property: Total races is at least completed races
        assert result['total_races'] >= result['completed_races'], \
            f"Total races ({result['total_races']}) should be >= completed races ({result['completed_races']})"


@given(race_results=race_results_with_min_finished_strategy(min_finished=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_consistency_score_inverse_proportional_to_std_dev(race_results):
    """
    Property: The consistency score should be inversely proportional to standard deviation.
    Higher std_dev should result in lower consistency score.
    
    **Validates: Requirements 2.2**
    """
    result = calculate_analytics_consistency_score(race_results, min_races=5)
    
    if result is not None:
        std_dev = result['std_dev']
        consistency_score = result['consistency_score']
        
        # Property: Inverse relationship between std_dev and consistency_score
        # Formula: consistency_score = max(0, 100 - (std_dev * 10))
        expected_score = max(0, 100 - (std_dev * 10))
        
        # Allow small floating point differences
        assert abs(consistency_score - expected_score) < 0.2, \
            f"Consistency score {consistency_score} doesn't match expected {expected_score} for std_dev {std_dev}"
        
        # Property: Perfect consistency (std_dev = 0) should give score of 100
        if std_dev == 0:
            assert consistency_score == 100, \
                f"Perfect consistency (std_dev=0) should give score 100, got {consistency_score}"
        
        # Property: High variance (std_dev >= 10) should give score of 0
        if std_dev >= 10:
            assert consistency_score == 0, \
                f"High variance (std_dev={std_dev}) should give score 0, got {consistency_score}"


@given(race_results=race_results_list_strategy(min_races=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_consistency_score_excludes_dnf(race_results):
    """
    Property: DNF results should be excluded from consistency calculation.
    Only completed races should count toward completed_races.
    
    **Validates: Requirements 2.3**
    """
    result = calculate_analytics_consistency_score(race_results, min_races=5)
    
    if result is not None:
        # Count actual finished races in input
        finished_count = 0
        for race in race_results:
            results = race.get('Results', [])
            if results:
                status = results[0].get('status', '')
                position = results[0].get('position', 'R')
                
                # Check if it's a finished race (not DNF)
                if status == 'Finished' and position != 'R':
                    try:
                        pos_int = int(position)
                        if pos_int > 0:
                            finished_count += 1
                    except (ValueError, TypeError):
                        pass
        
        # Property: completed_races should match actual finished races
        assert result['completed_races'] == finished_count, \
            f"Completed races {result['completed_races']} should match actual finished count {finished_count}"
        
        # Property: completed_races should be <= total_races
        assert result['completed_races'] <= result['total_races'], \
            f"Completed races {result['completed_races']} should be <= total races {result['total_races']}"


def test_property_consistency_score_insufficient_data():
    """
    Property: When there are fewer than min_races completed races,
    the function should return None.
    
    **Validates: Requirements 2.1**
    """
    # Create race results with only 3 finished races
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-03-01',
            'round': '1',
            'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-03-08',
            'round': '2',
            'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '2'}]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-15',
            'round': '3',
            'Results': [{'position': 'R', 'points': '0', 'status': 'Engine', 'grid': '1'}]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-03-22',
            'round': '4',
            'Results': [{'position': '3', 'points': '15', 'status': 'Finished', 'grid': '3'}]
        }
    ]
    
    result = calculate_analytics_consistency_score(race_results, min_races=5)
    
    # Property: Should return None when insufficient data
    assert result is None, \
        f"Should return None with only 3 finished races (min_races=5), got {result}"


def test_property_consistency_score_perfect_consistency():
    """
    Property: When a driver finishes in the same position every race,
    std_dev should be 0 and consistency_score should be 100.
    
    **Validates: Requirements 2.2**
    """
    # Create race results with identical positions
    race_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': '5', 'points': '10', 'status': 'Finished', 'grid': '5'}]
        }
        for i in range(1, 8)
    ]
    
    result = calculate_analytics_consistency_score(race_results, min_races=5)
    
    assert result is not None, "Should return result with sufficient data"
    
    # Property: Perfect consistency should have std_dev = 0
    assert result['std_dev'] == 0, \
        f"Perfect consistency should have std_dev=0, got {result['std_dev']}"
    
    # Property: Perfect consistency should have consistency_score = 100
    assert result['consistency_score'] == 100, \
        f"Perfect consistency should have score=100, got {result['consistency_score']}"


# ============================================================================
# Property 3: Qualifying-Race Correlation Calculation
# **Validates: Requirements 3.1, 3.2**
# ============================================================================

@composite
def race_results_with_grid_and_finish_strategy(draw, min_races=5, max_races=24):
    """
    Generate a list of race results with valid grid and finish positions.
    
    This ensures we have enough data for correlation calculation.
    """
    num_races = draw(st.integers(min_value=min_races, max_value=max_races))
    races = []
    
    for i in range(num_races):
        race_name = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
        year = draw(st.integers(min_value=2000, max_value=2024))
        month = draw(st.integers(min_value=1, max_value=12))
        day = draw(st.integers(min_value=1, max_value=28))
        race_date = f"{year:04d}-{month:02d}-{day:02d}"
        
        # Generate valid grid and finish positions
        grid = draw(st.integers(min_value=1, max_value=20))
        position = draw(st.integers(min_value=1, max_value=20))
        
        # Calculate points based on position
        points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
        points = points_map.get(position, 0)
        
        race = {
            'raceName': race_name,
            'date': race_date,
            'round': str(i + 1),
            'Results': [{
                'position': str(position),
                'points': str(points),
                'status': 'Finished',
                'grid': str(grid)
            }]
        }
        
        races.append(race)
    
    return races


@given(race_results=race_results_with_grid_and_finish_strategy(min_races=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_correlation_coefficient_range(race_results):
    """
    Property: For any driver's race results with sufficient data,
    the correlation coefficient should be between -1 and 1.
    
    **Validates: Requirements 3.1, 3.2**
    """
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    # Should not be None since we have at least 5 finished races with grid data
    if result is not None:
        correlation = result['correlation_coefficient']
        
        # Property: Correlation coefficient is in range -1 to 1
        if correlation is not None:
            assert -1 <= correlation <= 1, \
                f"Correlation coefficient should be -1 to 1, got {correlation}"


@given(race_results=race_results_with_grid_and_finish_strategy(min_races=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_correlation_scatter_data_matches_input(race_results):
    """
    Property: For any driver's race results, the scatter data should have
    one entry per finished race with valid grid and finish positions.
    
    **Validates: Requirements 3.1, 3.2**
    """
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    if result is not None:
        scatter_data = result['scatter_data']
        
        # Count expected finished races with valid grid/finish data
        expected_count = 0
        for race in race_results:
            results = race.get('Results', [])
            if results:
                res = results[0]
                if res.get('status') == 'Finished' and res.get('grid') and res.get('position'):
                    expected_count += 1
        
        # Property: Scatter data should match finished races count
        assert len(scatter_data) == expected_count, \
            f"Scatter data should have {expected_count} entries, got {len(scatter_data)}"
        
        # Property: Each scatter data point should have grid and finish
        for point in scatter_data:
            assert 'grid' in point, "Scatter point should have 'grid' key"
            assert 'finish' in point, "Scatter point should have 'finish' key"
            assert 'race_name' in point, "Scatter point should have 'race_name' key"
            
            # Property: Grid and finish should be valid positions (1-20)
            assert 1 <= point['grid'] <= 20, \
                f"Grid position should be 1-20, got {point['grid']}"
            assert 1 <= point['finish'] <= 20, \
                f"Finish position should be 1-20, got {point['finish']}"


@given(race_results=race_results_with_grid_and_finish_strategy(min_races=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_correlation_avg_position_change(race_results):
    """
    Property: For any driver's race results, the average position change
    should be calculated correctly as (finish - grid) averaged across races.
    
    **Validates: Requirements 3.2**
    """
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    if result is not None:
        scatter_data = result['scatter_data']
        avg_position_change = result['avg_position_change']
        
        if scatter_data:
            # Calculate expected average position change
            position_changes = [point['finish'] - point['grid'] for point in scatter_data]
            expected_avg = sum(position_changes) / len(position_changes)
            
            # Property: Average position change should match calculation
            # Allow small floating point differences
            assert abs(avg_position_change - expected_avg) < 0.01, \
                f"Average position change {avg_position_change} doesn't match expected {expected_avg}"


@given(race_results=race_results_with_grid_and_finish_strategy(min_races=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_correlation_classification(race_results):
    """
    Property: For any driver's race results, the classification should
    match the correlation coefficient value according to the rules:
    - correlation < -0.3: "strong race performer"
    - correlation > 0.7: "qualifying-dependent performer"
    - otherwise: "balanced performer"
    
    **Validates: Requirements 3.1**
    """
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    if result is not None:
        correlation = result['correlation_coefficient']
        classification = result['classification']
        
        if correlation is not None:
            # Property: Classification should match correlation value
            if correlation < -0.3:
                assert classification == "strong race performer", \
                    f"Correlation {correlation} < -0.3 should classify as 'strong race performer', got '{classification}'"
            elif correlation > 0.7:
                assert classification == "qualifying-dependent performer", \
                    f"Correlation {correlation} > 0.7 should classify as 'qualifying-dependent performer', got '{classification}'"
            else:
                assert classification == "balanced performer", \
                    f"Correlation {correlation} in [-0.3, 0.7] should classify as 'balanced performer', got '{classification}'"
        else:
            # If correlation is None, classification should indicate insufficient data
            assert classification == "insufficient data", \
                f"When correlation is None, classification should be 'insufficient data', got '{classification}'"


@given(race_results=race_results_with_grid_and_finish_strategy(min_races=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_correlation_races_analyzed(race_results):
    """
    Property: For any driver's race results, the races_analyzed count
    should match the number of finished races with valid grid/finish data.
    
    **Validates: Requirements 3.1, 3.2**
    """
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    if result is not None:
        races_analyzed = result['races_analyzed']
        scatter_data = result['scatter_data']
        
        # Property: races_analyzed should match scatter_data length
        assert races_analyzed == len(scatter_data), \
            f"races_analyzed {races_analyzed} should match scatter_data length {len(scatter_data)}"
        
        # Property: races_analyzed should be at least min_races
        assert races_analyzed >= 5, \
            f"races_analyzed should be at least 5, got {races_analyzed}"


def test_property_correlation_insufficient_data():
    """
    Property: When there are fewer than min_races with valid grid/finish data,
    the function should return None.
    
    **Validates: Requirements 3.1**
    """
    # Create race results with only 3 finished races with grid data
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-03-01',
            'round': '1',
            'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '2'}]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-03-08',
            'round': '2',
            'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '3'}]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-15',
            'round': '3',
            'Results': [{'position': 'R', 'points': '0', 'status': 'Engine', 'grid': '1'}]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-03-22',
            'round': '4',
            'Results': [{'position': '3', 'points': '15', 'status': 'Finished', 'grid': '4'}]
        }
    ]
    
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    # Property: Should return dict with insufficient_data flag when insufficient data
    assert result is not None, "Should return a dict even with insufficient data"
    assert result.get('insufficient_data') == True, \
        f"Should flag insufficient data with only 3 finished races (min_races=5)"
    assert result.get('races_analyzed') == 3, "Should indicate 3 races were analyzed"


def test_property_correlation_excludes_dnf():
    """
    Property: DNF results should be excluded from correlation calculation.
    
    **Validates: Requirements 3.1**
    """
    # Create race results with some DNFs
    race_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': str(i), 'points': '10', 'status': 'Finished', 'grid': str(i)}]
        }
        for i in range(1, 8)
    ]
    
    # Add DNF races
    race_results.extend([
        {
            'raceName': 'Race 8',
            'date': '2024-03-08',
            'round': '8',
            'Results': [{'position': 'R', 'points': '0', 'status': 'Engine', 'grid': '1'}]
        },
        {
            'raceName': 'Race 9',
            'date': '2024-03-09',
            'round': '9',
            'Results': [{'position': 'R', 'points': '0', 'status': 'Accident', 'grid': '2'}]
        }
    ])
    
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    assert result is not None, "Should return result with sufficient finished races"
    
    # Property: races_analyzed should only count finished races
    assert result['races_analyzed'] == 7, \
        f"Should analyze only 7 finished races (excluding 2 DNFs), got {result['races_analyzed']}"
    
    # Property: scatter_data should only include finished races
    assert len(result['scatter_data']) == 7, \
        f"Scatter data should have 7 entries (excluding DNFs), got {len(result['scatter_data'])}"


def test_property_correlation_perfect_correlation():
    """
    Property: When grid position equals finish position for all races,
    correlation should be 1.0 (perfect positive correlation).
    
    **Validates: Requirements 3.1**
    """
    # Create race results where grid = finish for all races
    race_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': str(i), 'points': '10', 'status': 'Finished', 'grid': str(i)}]
        }
        for i in range(1, 8)
    ]
    
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    assert result is not None, "Should return result with sufficient data"
    
    # Property: Perfect positive correlation should have coefficient close to 1.0
    correlation = result['correlation_coefficient']
    assert correlation is not None, "Correlation should not be None"
    assert abs(correlation - 1.0) < 0.01, \
        f"Perfect positive correlation should be ~1.0, got {correlation}"
    
    # Property: Average position change should be 0 (no change)
    assert abs(result['avg_position_change']) < 0.01, \
        f"No position change should give avg_position_change ~0, got {result['avg_position_change']}"
    
    # Property: Should be classified as qualifying-dependent performer
    assert result['classification'] == "qualifying-dependent performer", \
        f"Perfect correlation should classify as 'qualifying-dependent performer', got '{result['classification']}'"


def test_property_correlation_inverse_correlation():
    """
    Property: When a driver consistently gains positions (finish < grid),
    correlation should be negative.
    
    **Validates: Requirements 3.1, 3.2**
    """
    # Create race results where driver always gains positions
    # Starting from worse grid positions but finishing better
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-03-01',
            'round': '1',
            'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '10'}]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-03-02',
            'round': '2',
            'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '12'}]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-03',
            'round': '3',
            'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '15'}]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-03-04',
            'round': '4',
            'Results': [{'position': '3', 'points': '15', 'status': 'Finished', 'grid': '14'}]
        },
        {
            'raceName': 'Race 5',
            'date': '2024-03-05',
            'round': '5',
            'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '16'}]
        },
        {
            'raceName': 'Race 6',
            'date': '2024-03-06',
            'round': '6',
            'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '18'}]
        }
    ]
    
    result = calculate_analytics_qualifying_race_correlation(race_results, min_races=5)
    
    assert result is not None, "Should return result with sufficient data"
    
    # Property: Inverse relationship should have negative correlation
    correlation = result['correlation_coefficient']
    assert correlation is not None, "Correlation should not be None"
    assert correlation < 0, \
        f"Inverse relationship should have negative correlation, got {correlation}"
    
    # Property: Average position change should be negative (gained positions on average)
    assert result['avg_position_change'] < 0, \
        f"Gaining positions should give negative avg_position_change, got {result['avg_position_change']}"


# ============================================================================
# Property 8: Form Indicator Calculation
# **Validates: Requirements 6.1, 6.2, 6.3**
# ============================================================================

@given(race_results=race_results_with_min_finished_strategy(min_finished=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_form_indicator_trend_direction_matches_slope(race_results):
    """
    Property: For any driver's recent race results, the trend direction
    should correctly match the linear regression slope:
    - slope < -0.3: "improving" (positions getting lower/better)
    - slope > 0.3: "declining" (positions getting higher/worse)
    - |slope| <= 0.3: "stable"
    
    **Validates: Requirements 6.1, 6.2, 6.3**
    """
    result = calculate_analytics_form_indicator(race_results, n_races=5)
    
    if result is not None:
        trend_direction = result['trend_direction']
        trend_slope = result['trend_slope']
        
        # Property: Trend direction should match slope classification
        # Implementation uses: abs(slope) < 0.3 for stable (strict inequality)
        # Account for floating point precision with small epsilon
        epsilon = 1e-9
        if abs(trend_slope) < 0.3 - epsilon:
            assert trend_direction == "stable", \
                f"Slope {trend_slope} with |slope| < 0.3 should be 'stable', got '{trend_direction}'"
        elif abs(trend_slope) > 0.3 + epsilon:
            # Clearly outside stable range
            if trend_slope < 0:
                assert trend_direction == "improving", \
                    f"Slope {trend_slope} < -0.3 should be 'improving', got '{trend_direction}'"
            else:
                assert trend_direction == "declining", \
                    f"Slope {trend_slope} > 0.3 should be 'declining', got '{trend_direction}'"
        # else: boundary case around ±0.3, could be either stable or improving/declining due to floating point


@given(race_results=race_results_with_min_finished_strategy(min_finished=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_form_indicator_avg_position_calculation(race_results):
    """
    Property: For any driver's recent race results, the average position
    should be calculated correctly as the mean of finishing positions
    for completed races.
    
    **Validates: Requirements 6.1**
    """
    result = calculate_analytics_form_indicator(race_results, n_races=5)
    
    if result is not None:
        avg_position = result['avg_position']
        races_analyzed = result['races_analyzed']
        
        # Property: Average position should be positive
        assert avg_position > 0, \
            f"Average position should be positive, got {avg_position}"
        
        # Property: Average position should be reasonable (1-20 for F1)
        assert 1 <= avg_position <= 20, \
            f"Average position should be 1-20, got {avg_position}"
        
        # Property: Races analyzed should be at least 1
        assert races_analyzed >= 1, \
            f"Races analyzed should be at least 1, got {races_analyzed}"
        
        # Manually calculate expected average from the input
        positions = []
        for race in race_results[:5]:  # Take first 5 races
            results = race.get('Results', [])
            if results:
                result_data = results[0]
                position = result_data.get('position', None)
                status = result_data.get('status', 'Finished')
                
                # Only include finished races
                if position and position != 'R' and status == 'Finished':
                    try:
                        pos_int = int(position)
                        if pos_int > 0:
                            positions.append(pos_int)
                    except (ValueError, TypeError):
                        pass
        
        if positions:
            expected_avg = sum(positions) / len(positions)
            # Property: Calculated average should match expected
            assert abs(avg_position - expected_avg) < 0.01, \
                f"Average position {avg_position} doesn't match expected {expected_avg}"


@given(race_results=race_results_with_min_finished_strategy(min_finished=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_form_indicator_total_points_calculation(race_results):
    """
    Property: For any driver's recent race results, the total points
    should be the sum of points scored in analyzed races.
    
    **Validates: Requirements 6.2**
    """
    result = calculate_analytics_form_indicator(race_results, n_races=5)
    
    if result is not None:
        total_points = result['total_points']
        
        # Property: Total points should be non-negative
        assert total_points >= 0, \
            f"Total points should be non-negative, got {total_points}"
        
        # Property: Total points should be reasonable (max 125 for 5 races with 25 points each)
        assert total_points <= 125, \
            f"Total points for 5 races should be <= 125, got {total_points}"


@given(race_results=race_results_with_min_finished_strategy(min_finished=5, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_form_indicator_races_analyzed_count(race_results):
    """
    Property: For any driver's race results, the races_analyzed count
    should indicate the actual number of races used in the calculation,
    which may be less than n_races if fewer races are available.
    
    **Validates: Requirements 6.5**
    """
    n_races = 5
    result = calculate_analytics_form_indicator(race_results, n_races=n_races)
    
    if result is not None:
        races_analyzed = result['races_analyzed']
        
        # Property: Races analyzed should be at least 1
        assert races_analyzed >= 1, \
            f"Races analyzed should be at least 1, got {races_analyzed}"
        
        # Property: Races analyzed should not exceed n_races
        assert races_analyzed <= n_races, \
            f"Races analyzed should not exceed n_races={n_races}, got {races_analyzed}"
        
        # Property: Races analyzed should not exceed total available races
        assert races_analyzed <= len(race_results), \
            f"Races analyzed should not exceed total races {len(race_results)}, got {races_analyzed}"


def test_property_form_indicator_improving_trend():
    """
    Property: When a driver's positions are improving (getting lower),
    the trend direction should be "improving" and slope should be negative.
    
    **Validates: Requirements 6.3**
    """
    # Create race results with improving trend (positions getting better)
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-03-01',
            'round': '1',
            'Results': [{'position': '10', 'points': '1', 'status': 'Finished', 'grid': '10'}]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-03-08',
            'round': '2',
            'Results': [{'position': '8', 'points': '4', 'status': 'Finished', 'grid': '8'}]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-15',
            'round': '3',
            'Results': [{'position': '6', 'points': '8', 'status': 'Finished', 'grid': '6'}]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-03-22',
            'round': '4',
            'Results': [{'position': '4', 'points': '12', 'status': 'Finished', 'grid': '4'}]
        },
        {
            'raceName': 'Race 5',
            'date': '2024-03-29',
            'round': '5',
            'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '2'}]
        }
    ]
    
    result = calculate_analytics_form_indicator(race_results, n_races=5)
    
    assert result is not None, "Should return result with sufficient data"
    
    # Property: Improving positions should have negative slope
    assert result['trend_slope'] < 0, \
        f"Improving trend should have negative slope, got {result['trend_slope']}"
    
    # Property: Should be classified as improving
    assert result['trend_direction'] == "improving", \
        f"Should be classified as 'improving', got '{result['trend_direction']}'"
    
    # Property: Average position should be reasonable
    assert 1 <= result['avg_position'] <= 10, \
        f"Average position should be 1-10, got {result['avg_position']}"


def test_property_form_indicator_declining_trend():
    """
    Property: When a driver's positions are declining (getting higher/worse),
    the trend direction should be "declining" and slope should be positive.
    
    **Validates: Requirements 6.3**
    """
    # Create race results with declining trend (positions getting worse)
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-03-01',
            'round': '1',
            'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '2'}]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-03-08',
            'round': '2',
            'Results': [{'position': '4', 'points': '12', 'status': 'Finished', 'grid': '4'}]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-15',
            'round': '3',
            'Results': [{'position': '6', 'points': '8', 'status': 'Finished', 'grid': '6'}]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-03-22',
            'round': '4',
            'Results': [{'position': '8', 'points': '4', 'status': 'Finished', 'grid': '8'}]
        },
        {
            'raceName': 'Race 5',
            'date': '2024-03-29',
            'round': '5',
            'Results': [{'position': '10', 'points': '1', 'status': 'Finished', 'grid': '10'}]
        }
    ]
    
    result = calculate_analytics_form_indicator(race_results, n_races=5)
    
    assert result is not None, "Should return result with sufficient data"
    
    # Property: Declining positions should have positive slope
    assert result['trend_slope'] > 0, \
        f"Declining trend should have positive slope, got {result['trend_slope']}"
    
    # Property: Should be classified as declining
    assert result['trend_direction'] == "declining", \
        f"Should be classified as 'declining', got '{result['trend_direction']}'"


def test_property_form_indicator_stable_trend():
    """
    Property: When a driver's positions are stable (consistent),
    the trend direction should be "stable" and slope should be near zero.
    
    **Validates: Requirements 6.3**
    """
    # Create race results with stable trend (consistent positions)
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-03-01',
            'round': '1',
            'Results': [{'position': '5', 'points': '10', 'status': 'Finished', 'grid': '5'}]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-03-08',
            'round': '2',
            'Results': [{'position': '5', 'points': '10', 'status': 'Finished', 'grid': '5'}]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-15',
            'round': '3',
            'Results': [{'position': '5', 'points': '10', 'status': 'Finished', 'grid': '5'}]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-03-22',
            'round': '4',
            'Results': [{'position': '5', 'points': '10', 'status': 'Finished', 'grid': '5'}]
        },
        {
            'raceName': 'Race 5',
            'date': '2024-03-29',
            'round': '5',
            'Results': [{'position': '5', 'points': '10', 'status': 'Finished', 'grid': '5'}]
        }
    ]
    
    result = calculate_analytics_form_indicator(race_results, n_races=5)
    
    assert result is not None, "Should return result with sufficient data"
    
    # Property: Stable positions should have slope near zero
    assert abs(result['trend_slope']) < 0.3, \
        f"Stable trend should have |slope| < 0.3, got {result['trend_slope']}"
    
    # Property: Should be classified as stable
    assert result['trend_direction'] == "stable", \
        f"Should be classified as 'stable', got '{result['trend_direction']}'"
    
    # Property: Average position should be exactly 5
    assert abs(result['avg_position'] - 5.0) < 0.01, \
        f"Average position should be 5.0, got {result['avg_position']}"


def test_property_form_indicator_fewer_than_n_races():
    """
    Property: When fewer than n_races are available, the function should
    use all available races and indicate the actual count in races_analyzed.
    
    **Validates: Requirements 6.5**
    """
    # Create race results with only 3 races
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-03-01',
            'round': '1',
            'Results': [{'position': '3', 'points': '15', 'status': 'Finished', 'grid': '3'}]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-03-08',
            'round': '2',
            'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '2'}]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-15',
            'round': '3',
            'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
        }
    ]
    
    result = calculate_analytics_form_indicator(race_results, n_races=5)
    
    assert result is not None, "Should return result even with fewer than n_races"
    
    # Property: races_analyzed should be 3 (all available races)
    assert result['races_analyzed'] == 3, \
        f"Should analyze all 3 available races, got {result['races_analyzed']}"
    
    # Property: Should still calculate trend direction
    assert result['trend_direction'] in ['improving', 'declining', 'stable'], \
        f"Should have valid trend direction, got '{result['trend_direction']}'"


def test_property_form_indicator_excludes_dnf():
    """
    Property: DNF results should be excluded from form indicator calculation.
    Only completed races should count toward the analysis.
    
    **Validates: Requirements 6.1, 6.2**
    """
    # Create race results with some DNFs
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-03-01',
            'round': '1',
            'Results': [{'position': '3', 'points': '15', 'status': 'Finished', 'grid': '3'}]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-03-08',
            'round': '2',
            'Results': [{'position': 'R', 'points': '0', 'status': 'Engine', 'grid': '2'}]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-15',
            'round': '3',
            'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '2'}]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-03-22',
            'round': '4',
            'Results': [{'position': 'R', 'points': '0', 'status': 'Accident', 'grid': '1'}]
        },
        {
            'raceName': 'Race 5',
            'date': '2024-03-29',
            'round': '5',
            'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
        }
    ]
    
    result = calculate_analytics_form_indicator(race_results, n_races=5)
    
    assert result is not None, "Should return result with some finished races"
    
    # Property: races_analyzed should only count finished races (3 in this case)
    assert result['races_analyzed'] == 3, \
        f"Should analyze only 3 finished races (excluding 2 DNFs), got {result['races_analyzed']}"
    
    # Property: Average position should only consider finished races
    # Positions: 3, 2, 1 -> average = 2.0
    expected_avg = (3 + 2 + 1) / 3
    assert abs(result['avg_position'] - expected_avg) < 0.01, \
        f"Average position should be {expected_avg}, got {result['avg_position']}"
    
    # Property: Total points should only include finished races
    # Points: 15, 18, 25 -> total = 58
    expected_points = 15 + 18 + 25
    assert abs(result['total_points'] - expected_points) < 0.1, \
        f"Total points should be {expected_points}, got {result['total_points']}"


def test_property_form_indicator_empty_input():
    """
    Property: When given empty race results, the function should return None.
    
    **Validates: Requirements 6.1**
    """
    result = calculate_analytics_form_indicator([], n_races=5)
    
    # Property: Should return None for empty input
    assert result is None, \
        f"Should return None for empty input, got {result}"


def test_property_form_indicator_all_dnf():
    """
    Property: When all races are DNFs, the function should return None
    since there are no finished races to analyze.
    
    **Validates: Requirements 6.1**
    """
    # Create race results with all DNFs
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-03-01',
            'round': '1',
            'Results': [{'position': 'R', 'points': '0', 'status': 'Engine', 'grid': '1'}]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-03-08',
            'round': '2',
            'Results': [{'position': 'R', 'points': '0', 'status': 'Accident', 'grid': '2'}]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-15',
            'round': '3',
            'Results': [{'position': 'R', 'points': '0', 'status': 'Gearbox', 'grid': '3'}]
        }
    ]
    
    result = calculate_analytics_form_indicator(race_results, n_races=5)
    
    # Property: Should return None when all races are DNFs
    assert result is None, \
        f"Should return None when all races are DNFs, got {result}"


# ============================================================================
# Property 4: Performance Trend Chart Structure
# **Validates: Requirements 1.3, 1.4**
# ============================================================================

@given(race_results=race_results_list_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_chart_has_proper_traces(race_results):
    """
    Property: For any performance trend data, the generated Plotly figure
    should contain at least one trace (line plot).
    
    **Validates: Requirements 1.3, 1.4**
    """
    # Generate trend data
    trend_data = calculate_analytics_performance_trends(race_results, metric="position")
    
    # Create chart
    fig = create_analytics_trend_chart(
        trend_data=trend_data,
        metric_name="Position",
        driver_name="Test Driver",
        team_color="#1E41FF"
    )
    
    # Property: Figure should be a Plotly Figure object
    assert isinstance(fig, go.Figure), \
        f"Should return a Plotly Figure, got {type(fig)}"
    
    # Property: Figure should have at least one trace
    assert len(fig.data) > 0, \
        "Figure should have at least one trace"
    
    # Property: First trace should be a Scatter plot (line chart)
    assert isinstance(fig.data[0], go.Scatter), \
        f"First trace should be Scatter plot, got {type(fig.data[0])}"


@given(race_results=race_results_list_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_chart_has_proper_axes(race_results):
    """
    Property: For any performance trend data, the chart should have
    properly labeled x-axis and y-axis.
    
    **Validates: Requirements 1.3**
    """
    # Generate trend data
    trend_data = calculate_analytics_performance_trends(race_results, metric="position")
    
    # Create chart
    fig = create_analytics_trend_chart(
        trend_data=trend_data,
        metric_name="Position",
        driver_name="Test Driver"
    )
    
    # Property: X-axis should have a title
    assert fig.layout.xaxis.title is not None, \
        "X-axis should have a title"
    assert fig.layout.xaxis.title.text is not None, \
        "X-axis title should have text"
    
    # Property: Y-axis should have a title
    assert fig.layout.yaxis.title is not None, \
        "Y-axis should have a title"
    assert fig.layout.yaxis.title.text is not None, \
        "Y-axis title should have text"
    
    # Property: Chart should have a title
    assert fig.layout.title is not None, \
        "Chart should have a title"


@given(race_results=race_results_list_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_chart_has_hover_data(race_results):
    """
    Property: For any performance trend data, the chart should have hover
    data including race name, date, and metric values.
    
    **Validates: Requirements 1.4**
    """
    # Generate trend data
    trend_data = calculate_analytics_performance_trends(race_results, metric="position")
    
    # Create chart
    fig = create_analytics_trend_chart(
        trend_data=trend_data,
        metric_name="Position",
        driver_name="Test Driver"
    )
    
    # Property: Hover mode should be configured
    assert fig.layout.hovermode is not None, \
        "Hover mode should be configured"
    
    # Property: First trace should have hover template
    assert fig.data[0].hovertemplate is not None, \
        "Trace should have hover template configured"
    
    # Property: Hover template should reference customdata (race name, date)
    hover_template = fig.data[0].hovertemplate
    assert 'customdata' in hover_template or '%{' in hover_template, \
        "Hover template should include data references"
    
    # Property: Custom data should be provided for hover
    if not trend_data.empty:
        assert fig.data[0].customdata is not None, \
            "Custom data should be provided for hover tooltips"


@given(race_results=race_results_list_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_chart_data_matches_input(race_results):
    """
    Property: For any performance trend data, the chart should display
    the same number of data points as the input race results.
    
    **Validates: Requirements 1.3**
    """
    # Generate trend data
    trend_data = calculate_analytics_performance_trends(race_results, metric="position")
    
    # Create chart
    fig = create_analytics_trend_chart(
        trend_data=trend_data,
        metric_name="Position",
        driver_name="Test Driver"
    )
    
    if not trend_data.empty:
        # Property: Number of data points should match input
        assert len(fig.data[0].x) == len(race_results), \
            f"Chart should have {len(race_results)} data points, got {len(fig.data[0].x)}"
        
        assert len(fig.data[0].y) == len(race_results), \
            f"Chart should have {len(race_results)} y-values, got {len(fig.data[0].y)}"


def test_property_chart_empty_data_handling():
    """
    Property: When given empty trend data, the chart should still return
    a valid Figure object (with a "no data" message).
    
    **Validates: Requirements 1.3**
    """
    # Create empty DataFrame with correct columns
    empty_trend_data = pd.DataFrame(columns=['race_name', 'race_date', 'round', 'metric_value'])
    
    # Create chart with empty data
    fig = create_analytics_trend_chart(
        trend_data=empty_trend_data,
        metric_name="Position",
        driver_name="Test Driver"
    )
    
    # Property: Should return a valid Figure
    assert isinstance(fig, go.Figure), \
        "Should return a Figure even with empty data"
    
    # Property: Figure should handle empty data gracefully
    # (either with annotation or empty traces)
    assert fig is not None, \
        "Figure should not be None"


def test_property_chart_styling_consistency():
    """
    Property: Charts should have consistent styling with F1 theme,
    including proper colors, fonts, and layout.
    
    **Validates: Requirements 1.3**
    """
    # Create sample race results
    race_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': str(i), 'points': '10', 'status': 'Finished', 'grid': '1'}]
        }
        for i in range(1, 6)
    ]
    
    trend_data = calculate_analytics_performance_trends(race_results, metric="position")
    
    # Test with custom team color
    fig_with_color = create_analytics_trend_chart(
        trend_data=trend_data,
        metric_name="Position",
        driver_name="Test Driver",
        team_color="#1E41FF"
    )
    
    # Property: Line should use the provided team color
    assert fig_with_color.data[0].line.color == "#1E41FF", \
        "Line should use provided team color"
    
    # Test without team color (should use default F1 red)
    fig_default_color = create_analytics_trend_chart(
        trend_data=trend_data,
        metric_name="Position",
        driver_name="Test Driver"
    )
    
    # Property: Should have a default color when none provided
    assert fig_default_color.data[0].line.color is not None, \
        "Line should have a color"
    
    # Property: Chart should have reasonable height
    assert fig_with_color.layout.height is not None, \
        "Chart should have height configured"
    assert fig_with_color.layout.height > 0, \
        "Chart height should be positive"


# ============================================================================
# Test Runner
# ============================================================================

def main():
    """Run all property tests."""
    print("=" * 80)
    print("Property-Based Tests for Analytics Functions")
    print("=" * 80)
    
    try:
        print("\n=== Property 1: Performance Trends Calculation ===")
        print("Testing: One row per race...")
        test_property_performance_trends_one_row_per_race()
        print("✅ PASSED")
        
        print("Testing: Correct columns...")
        test_property_performance_trends_correct_columns()
        print("✅ PASSED")
        
        print("Testing: Position metric values...")
        test_property_performance_trends_position_metric_values()
        print("✅ PASSED")
        
        print("Testing: Points metric values...")
        test_property_performance_trends_points_metric_values()
        print("✅ PASSED")
        
        print("Testing: Round numbers sequential...")
        test_property_performance_trends_round_numbers_sequential()
        print("✅ PASSED")
        
        print("Testing: Empty input handling...")
        test_property_performance_trends_empty_input()
        print("✅ PASSED")
        
        print("\n=== Property 2: Consistency Score Calculation ===")
        print("Testing: Score in 0-100 range...")
        test_property_consistency_score_range()
        print("✅ PASSED")
        
        print("Testing: Inverse proportional to std dev...")
        test_property_consistency_score_inverse_proportional_to_std_dev()
        print("✅ PASSED")
        
        print("Testing: Excludes DNF results...")
        test_property_consistency_score_excludes_dnf()
        print("✅ PASSED")
        
        print("Testing: Insufficient data handling...")
        test_property_consistency_score_insufficient_data()
        print("✅ PASSED")
        
        print("Testing: Perfect consistency...")
        test_property_consistency_score_perfect_consistency()
        print("✅ PASSED")
        
        print("\n=== Property 3: Qualifying-Race Correlation Calculation ===")
        print("Testing: Correlation coefficient range...")
        test_property_correlation_coefficient_range()
        print("✅ PASSED")
        
        print("Testing: Scatter data matches input...")
        test_property_correlation_scatter_data_matches_input()
        print("✅ PASSED")
        
        print("Testing: Average position change...")
        test_property_correlation_avg_position_change()
        print("✅ PASSED")
        
        print("Testing: Classification logic...")
        test_property_correlation_classification()
        print("✅ PASSED")
        
        print("Testing: Races analyzed count...")
        test_property_correlation_races_analyzed()
        print("✅ PASSED")
        
        print("Testing: Insufficient data handling...")
        test_property_correlation_insufficient_data()
        print("✅ PASSED")
        
        print("Testing: Excludes DNF results...")
        test_property_correlation_excludes_dnf()
        print("✅ PASSED")
        
        print("Testing: Perfect correlation...")
        test_property_correlation_perfect_correlation()
        print("✅ PASSED")
        
        print("Testing: Inverse correlation...")
        test_property_correlation_inverse_correlation()
        print("✅ PASSED")
        
        print("\n=== Property 8: Form Indicator Calculation ===")
        print("Testing: Trend direction matches slope...")
        test_property_form_indicator_trend_direction_matches_slope()
        print("✅ PASSED")
        
        print("Testing: Average position calculation...")
        test_property_form_indicator_avg_position_calculation()
        print("✅ PASSED")
        
        print("Testing: Total points calculation...")
        test_property_form_indicator_total_points_calculation()
        print("✅ PASSED")
        
        print("Testing: Races analyzed count...")
        test_property_form_indicator_races_analyzed_count()
        print("✅ PASSED")
        
        print("Testing: Improving trend...")
        test_property_form_indicator_improving_trend()
        print("✅ PASSED")
        
        print("Testing: Declining trend...")
        test_property_form_indicator_declining_trend()
        print("✅ PASSED")
        
        print("Testing: Stable trend...")
        test_property_form_indicator_stable_trend()
        print("✅ PASSED")
        
        print("Testing: Fewer than n_races...")
        test_property_form_indicator_fewer_than_n_races()
        print("✅ PASSED")
        
        print("Testing: Excludes DNF results...")
        test_property_form_indicator_excludes_dnf()
        print("✅ PASSED")
        
        print("Testing: Empty input handling...")
        test_property_form_indicator_empty_input()
        print("✅ PASSED")
        
        print("Testing: All DNF handling...")
        test_property_form_indicator_all_dnf()
        print("✅ PASSED")
        
        print("\n=== Property 4: Performance Trend Chart Structure ===")
        print("Testing: Chart has proper traces...")
        test_property_chart_has_proper_traces()
        print("✅ PASSED")
        
        print("Testing: Chart has proper axes...")
        test_property_chart_has_proper_axes()
        print("✅ PASSED")
        
        print("Testing: Chart has hover data...")
        test_property_chart_has_hover_data()
        print("✅ PASSED")
        
        print("Testing: Chart data matches input...")
        test_property_chart_data_matches_input()
        print("✅ PASSED")
        
        print("Testing: Empty data handling...")
        test_property_chart_empty_data_handling()
        print("✅ PASSED")
        
        print("Testing: Styling consistency...")
        test_property_chart_styling_consistency()
        print("✅ PASSED")
        
        print("\n=== Property 9: Team Reliability Calculation ===")
        print("Testing: Both finished percentage range...")
        test_property_team_reliability_both_finished_pct_range()
        print("✅ PASSED")
        
        print("Testing: Mechanical DNF rate range...")
        test_property_team_reliability_mechanical_dnf_rate_range()
        print("✅ PASSED")
        
        print("Testing: Average finish position positive...")
        test_property_team_reliability_avg_finish_position_positive()
        print("✅ PASSED")
        
        print("Testing: Total races matches input...")
        test_property_team_reliability_total_races_matches_input()
        print("✅ PASSED")
        
        print("Testing: Empty input handling...")
        test_property_team_reliability_empty_input()
        print("✅ PASSED")
        
        print("Testing: Both drivers always finish...")
        test_property_team_reliability_both_drivers_always_finish()
        print("✅ PASSED")
        
        print("Testing: Mechanical DNF categorization...")
        test_property_team_reliability_mechanical_dnf_categorization()
        print("✅ PASSED")
        
        print("\n=== Property 10: Constructor Development Trends ===")
        print("Testing: One row per race...")
        test_property_constructor_development_one_row_per_race()
        print("✅ PASSED")
        
        print("Testing: Correct columns...")
        test_property_constructor_development_correct_columns()
        print("✅ PASSED")
        
        print("Testing: Rolling window size...")
        test_property_constructor_development_rolling_window_size()
        print("✅ PASSED")
        
        print("Testing: Trend classification valid...")
        test_property_constructor_development_trend_classification_valid()
        print("✅ PASSED")
        
        print("Testing: Empty input handling...")
        test_property_constructor_development_empty_input()
        print("✅ PASSED")
        
        print("Testing: Improving trend...")
        test_property_constructor_development_improving_trend()
        print("✅ PASSED")
        
        print("Testing: Declining trend...")
        test_property_constructor_development_declining_trend()
        print("✅ PASSED")
        
        print("\n=== Property 11: Driver Pairing Effectiveness ===")
        print("Testing: Points ratio format...")
        test_property_driver_pairing_points_ratio_format()
        print("✅ PASSED")
        
        print("Testing: Qualifying gap non-negative...")
        test_property_driver_pairing_quali_gap_non_negative()
        print("✅ PASSED")
        
        print("Testing: Race gap non-negative...")
        test_property_driver_pairing_race_gap_non_negative()
        print("✅ PASSED")
        
        print("Testing: Balance flag valid...")
        test_property_driver_pairing_balance_flag_valid()
        print("✅ PASSED")
        
        print("Testing: Points non-negative...")
        test_property_driver_pairing_points_non_negative()
        print("✅ PASSED")
        
        print("Testing: Imbalanced flag...")
        test_property_driver_pairing_imbalanced_flag()
        print("✅ PASSED")
        
        print("Testing: Balanced flag...")
        test_property_driver_pairing_balanced_flag()
        print("✅ PASSED")
        
        print("\n=== Property 12: Circuit-Specific Performance ===")
        print("Testing: Rates in range...")
        test_property_circuit_performance_rates_in_range()
        print("✅ PASSED")
        
        print("Testing: Average finish positive...")
        test_property_circuit_performance_avg_finish_positive()
        print("✅ PASSED")
        
        print("Testing: Low sample warning...")
        test_property_circuit_performance_low_sample_warning()
        print("✅ PASSED")
        
        print("Testing: Appearances count...")
        test_property_circuit_performance_appearances_count()
        print("✅ PASSED")
        
        print("\n=== Property 13: Circuit Difficulty Rating ===")
        print("Testing: Difficulty score range...")
        test_property_circuit_difficulty_score_range()
        print("✅ PASSED")
        
        print("Testing: DNF rate range...")
        test_property_circuit_difficulty_dnf_rate_range()
        print("✅ PASSED")
        
        print("Testing: Position change non-negative...")
        test_property_circuit_difficulty_position_change_non_negative()
        print("✅ PASSED")
        
        print("Testing: DataFrame structure...")
        test_property_circuit_difficulty_dataframe_structure()
        print("✅ PASSED")
        
        print("Testing: Empty input handling...")
        test_property_circuit_difficulty_empty_input()
        print("✅ PASSED")
        
        print("\n" + "=" * 80)
        print("✅ ALL PROPERTY TESTS PASSED!")
        print("=" * 80)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Property test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())


# ============================================================================
# Property 9: Team Reliability Calculation
# **Validates: Requirements 7.1, 7.2, 7.3, 7.5**
# ============================================================================

from app import calculate_analytics_team_reliability

@composite
def constructor_race_results_strategy(draw, min_races=1, max_races=24):
    """
    Generate a list of constructor race results with two drivers per race.
    """
    num_races = draw(st.integers(min_value=min_races, max_value=max_races))
    races = []
    
    for i in range(num_races):
        race_name = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
        year = draw(st.integers(min_value=2000, max_value=2024))
        month = draw(st.integers(min_value=1, max_value=12))
        day = draw(st.integers(min_value=1, max_value=28))
        race_date = f"{year:04d}-{month:02d}-{day:02d}"
        
        # Generate results for two drivers
        results = []
        for driver_idx in range(2):
            is_dnf = draw(st.booleans())
            if is_dnf:
                position = 'R'
                points = '0'
                status = draw(st.sampled_from(['Engine', 'Gearbox', 'Accident', 'Collision', 'Hydraulics', 'Electrical']))
            else:
                position_int = draw(st.integers(min_value=1, max_value=20))
                position = str(position_int)
                points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
                points = str(points_map.get(position_int, 0))
                status = 'Finished'
            
            grid = draw(st.integers(min_value=1, max_value=20))
            
            results.append({
                'position': position,
                'points': points,
                'status': status,
                'grid': str(grid),
                'Driver': {'driverId': f'driver{driver_idx+1}'}
            })
        
        race = {
            'raceName': race_name,
            'date': race_date,
            'round': str(i + 1),
            'Results': results
        }
        
        races.append(race)
    
    return races


@given(constructor_results=constructor_race_results_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_team_reliability_both_finished_pct_range(constructor_results):
    """
    Property: For any constructor's race results, the both_finished_pct
    should be in the range 0-100.
    
    **Validates: Requirements 7.1, 7.5**
    """
    reliability = calculate_analytics_team_reliability(constructor_results, "2024")
    
    # Property: both_finished_pct is in range 0-100
    assert 0 <= reliability['both_finished_pct'] <= 100, \
        f"both_finished_pct should be 0-100, got {reliability['both_finished_pct']}"


@given(constructor_results=constructor_race_results_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_team_reliability_mechanical_dnf_rate_range(constructor_results):
    """
    Property: For any constructor's race results, the mechanical_dnf_rate
    should be in the range 0-100.
    
    **Validates: Requirements 7.3, 7.5**
    """
    reliability = calculate_analytics_team_reliability(constructor_results, "2024")
    
    # Property: mechanical_dnf_rate is in range 0-100
    assert 0 <= reliability['mechanical_dnf_rate'] <= 100, \
        f"mechanical_dnf_rate should be 0-100, got {reliability['mechanical_dnf_rate']}"


@given(constructor_results=constructor_race_results_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_team_reliability_avg_finish_position_positive(constructor_results):
    """
    Property: For any constructor's race results, the avg_finish_position
    should be non-negative (0 if no finishes, positive otherwise).
    
    **Validates: Requirements 7.2, 7.5**
    """
    reliability = calculate_analytics_team_reliability(constructor_results, "2024")
    
    # Property: avg_finish_position is non-negative
    assert reliability['avg_finish_position'] >= 0, \
        f"avg_finish_position should be non-negative, got {reliability['avg_finish_position']}"


@given(constructor_results=constructor_race_results_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_team_reliability_total_races_matches_input(constructor_results):
    """
    Property: For any constructor's race results, the total_races count
    should match the number of input races.
    
    **Validates: Requirements 7.1, 7.5**
    """
    reliability = calculate_analytics_team_reliability(constructor_results, "2024")
    
    # Property: total_races matches input length
    assert reliability['total_races'] == len(constructor_results), \
        f"total_races should be {len(constructor_results)}, got {reliability['total_races']}"


def test_property_team_reliability_empty_input():
    """
    Property: Empty input should return zero values for all metrics.
    
    **Validates: Requirements 7.1, 7.2, 7.3, 7.5**
    """
    reliability = calculate_analytics_team_reliability([], "2024")
    
    # Property: All metrics should be 0 for empty input
    assert reliability['both_finished_pct'] == 0.0, "both_finished_pct should be 0 for empty input"
    assert reliability['avg_finish_position'] == 0.0, "avg_finish_position should be 0 for empty input"
    assert reliability['mechanical_dnf_rate'] == 0.0, "mechanical_dnf_rate should be 0 for empty input"
    assert reliability['total_races'] == 0, "total_races should be 0 for empty input"


def test_property_team_reliability_both_drivers_always_finish():
    """
    Property: When both drivers finish every race, both_finished_pct should be 100.
    
    **Validates: Requirements 7.1**
    """
    # Create constructor results where both drivers always finish
    constructor_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [
                {'position': str(i), 'points': '10', 'status': 'Finished', 'grid': str(i), 'Driver': {'driverId': 'driver1'}},
                {'position': str(i+1), 'points': '8', 'status': 'Finished', 'grid': str(i+1), 'Driver': {'driverId': 'driver2'}}
            ]
        }
        for i in range(1, 6)
    ]
    
    reliability = calculate_analytics_team_reliability(constructor_results, "2024")
    
    # Property: both_finished_pct should be 100 when both drivers always finish
    assert reliability['both_finished_pct'] == 100.0, \
        f"both_finished_pct should be 100 when both drivers always finish, got {reliability['both_finished_pct']}"


def test_property_team_reliability_mechanical_dnf_categorization():
    """
    Property: Only mechanical DNFs should count toward mechanical_dnf_rate.
    
    **Validates: Requirements 7.3**
    """
    # Create constructor results with specific DNF types
    constructor_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-03-01',
            'round': '1',
            'Results': [
                {'position': 'R', 'points': '0', 'status': 'Engine', 'grid': '1', 'Driver': {'driverId': 'driver1'}},  # Mechanical
                {'position': '1', 'points': '25', 'status': 'Finished', 'grid': '2', 'Driver': {'driverId': 'driver2'}}
            ]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-03-02',
            'round': '2',
            'Results': [
                {'position': 'R', 'points': '0', 'status': 'Accident', 'grid': '1', 'Driver': {'driverId': 'driver1'}},  # Not mechanical
                {'position': '2', 'points': '18', 'status': 'Finished', 'grid': '2', 'Driver': {'driverId': 'driver2'}}
            ]
        }
    ]
    
    reliability = calculate_analytics_team_reliability(constructor_results, "2024")
    
    # Total driver entries = 4 (2 drivers × 2 races)
    # Mechanical DNFs = 1 (Engine)
    # Expected rate = 1/4 * 100 = 25%
    assert reliability['mechanical_dnf_rate'] == 25.0, \
        f"mechanical_dnf_rate should be 25% (1 mechanical out of 4 entries), got {reliability['mechanical_dnf_rate']}"


# ============================================================================
# Property 10: Constructor Development Trends
# **Validates: Requirements 8.1, 8.2, 8.4**
# ============================================================================

from app import calculate_analytics_constructor_development

@given(constructor_results=constructor_race_results_strategy(min_races=1, max_races=24), 
       window_size=st.integers(min_value=2, max_value=5))
@settings(max_examples=100, deadline=None)
def test_property_constructor_development_one_row_per_race(constructor_results, window_size):
    """
    Property: For any constructor's race results, the development DataFrame
    should have exactly one row per race.
    
    **Validates: Requirements 8.1, 8.2, 8.4**
    """
    development = calculate_analytics_constructor_development(constructor_results, window_size=window_size)
    
    # Property: One row per race
    assert len(development) == len(constructor_results), \
        f"Expected {len(constructor_results)} rows, got {len(development)}"


@given(constructor_results=constructor_race_results_strategy(min_races=1, max_races=24), 
       window_size=st.integers(min_value=2, max_value=5))
@settings(max_examples=100, deadline=None)
def test_property_constructor_development_correct_columns(constructor_results, window_size):
    """
    Property: For any constructor's race results, the development DataFrame
    should have the correct columns.
    
    **Validates: Requirements 8.1, 8.2, 8.4**
    """
    development = calculate_analytics_constructor_development(constructor_results, window_size=window_size)
    
    # Property: Correct columns exist
    expected_columns = {'race_name', 'round', 'points', 'avg_position', 
                       'rolling_avg_points', 'rolling_avg_position', 'trend_classification'}
    actual_columns = set(development.columns)
    
    assert expected_columns == actual_columns, \
        f"Expected columns {expected_columns}, got {actual_columns}"


@given(constructor_results=constructor_race_results_strategy(min_races=3, max_races=24), 
       window_size=st.integers(min_value=2, max_value=5))
@settings(max_examples=100, deadline=None)
def test_property_constructor_development_rolling_window_size(constructor_results, window_size):
    """
    Property: For any constructor's race results, the rolling averages should
    respect the window size (first window_size-1 rows may have NaN, rest should have values).
    
    **Validates: Requirements 8.1, 8.2**
    """
    assume(len(constructor_results) >= window_size)
    
    development = calculate_analytics_constructor_development(constructor_results, window_size=window_size)
    
    # Property: Rolling averages should have values after window_size-1 rows
    if len(development) >= window_size:
        # Check that we have rolling average values
        non_null_count = development['rolling_avg_points'].notna().sum()
        assert non_null_count > 0, "Should have some rolling average values"


@given(constructor_results=constructor_race_results_strategy(min_races=3, max_races=24), 
       window_size=st.integers(min_value=2, max_value=5))
@settings(max_examples=100, deadline=None)
def test_property_constructor_development_trend_classification_valid(constructor_results, window_size):
    """
    Property: For any constructor's race results, the trend_classification
    should be one of: "improving", "declining", "stable", or "insufficient data".
    
    **Validates: Requirements 8.4**
    """
    development = calculate_analytics_constructor_development(constructor_results, window_size=window_size)
    
    if not development.empty:
        trend = development['trend_classification'].iloc[0]
        
        # Property: Trend classification is valid
        valid_trends = {'improving', 'declining', 'stable', 'insufficient data'}
        assert trend in valid_trends, \
            f"Trend classification should be one of {valid_trends}, got '{trend}'"


def test_property_constructor_development_empty_input():
    """
    Property: Empty input should return an empty DataFrame with correct columns.
    
    **Validates: Requirements 8.1, 8.2, 8.4**
    """
    development = calculate_analytics_constructor_development([], window_size=3)
    
    # Property: Empty DataFrame with correct columns
    assert len(development) == 0, "Empty input should produce empty DataFrame"
    
    # When empty, the DataFrame only has the column names defined in the return statement
    expected_columns = {'race_name', 'round', 'rolling_avg_points', 
                       'rolling_avg_position', 'trend_classification'}
    actual_columns = set(development.columns)
    
    assert expected_columns == actual_columns, \
        f"Expected columns {expected_columns}, got {actual_columns}"


def test_property_constructor_development_improving_trend():
    """
    Property: When points increase consistently, trend should be "improving".
    
    **Validates: Requirements 8.4**
    """
    # Create constructor results with increasing points
    constructor_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [
                {'position': str(10-i), 'points': str(5 + i*5), 'status': 'Finished', 'grid': str(i), 'Driver': {'driverId': 'driver1'}},
                {'position': str(11-i), 'points': str(5 + i*5), 'status': 'Finished', 'grid': str(i+1), 'Driver': {'driverId': 'driver2'}}
            ]
        }
        for i in range(1, 7)
    ]
    
    development = calculate_analytics_constructor_development(constructor_results, window_size=3)
    
    # Property: Trend should be "improving" with increasing points
    assert development['trend_classification'].iloc[0] == 'improving', \
        f"Trend should be 'improving' with increasing points, got '{development['trend_classification'].iloc[0]}'"


def test_property_constructor_development_declining_trend():
    """
    Property: When points decrease consistently, trend should be "declining".
    
    **Validates: Requirements 8.4**
    """
    # Create constructor results with decreasing points
    constructor_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [
                {'position': str(i), 'points': str(35 - i*5), 'status': 'Finished', 'grid': str(i), 'Driver': {'driverId': 'driver1'}},
                {'position': str(i+1), 'points': '0', 'status': 'Finished', 'grid': str(i+1), 'Driver': {'driverId': 'driver2'}}
            ]
        }
        for i in range(1, 7)
    ]
    
    development = calculate_analytics_constructor_development(constructor_results, window_size=3)
    
    # Property: Trend should be "declining" with decreasing points
    assert development['trend_classification'].iloc[0] == 'declining', \
        f"Trend should be 'declining' with decreasing points, got '{development['trend_classification'].iloc[0]}'"


# ============================================================================
# Property 11: Driver Pairing Effectiveness
# **Validates: Requirements 9.1, 9.2, 9.3**
# ============================================================================

from app import calculate_analytics_driver_pairing

@composite
def driver_race_results_strategy(draw, min_races=1, max_races=24):
    """
    Generate a list of race results for a single driver.
    """
    num_races = draw(st.integers(min_value=min_races, max_value=max_races))
    races = []
    
    for i in range(num_races):
        race_name = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
        year = draw(st.integers(min_value=2000, max_value=2024))
        month = draw(st.integers(min_value=1, max_value=12))
        day = draw(st.integers(min_value=1, max_value=28))
        race_date = f"{year:04d}-{month:02d}-{day:02d}"
        
        is_dnf = draw(st.booleans())
        if is_dnf:
            position = 'R'
            points = '0'
            status = draw(st.sampled_from(['Engine', 'Gearbox', 'Accident', 'Collision', 'Hydraulics', 'Electrical']))
        else:
            position_int = draw(st.integers(min_value=1, max_value=20))
            position = str(position_int)
            points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
            points = str(points_map.get(position_int, 0))
            status = 'Finished'
        
        grid = draw(st.integers(min_value=1, max_value=20))
        
        race = {
            'raceName': race_name,
            'date': race_date,
            'round': str(i + 1),
            'Results': [{
                'position': position,
                'points': points,
                'status': status,
                'grid': str(grid),
                'Driver': {'driverId': 'driver'}
            }]
        }
        
        races.append(race)
    
    return races


@given(driver1_results=driver_race_results_strategy(min_races=1, max_races=24),
       driver2_results=driver_race_results_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_driver_pairing_points_ratio_format(driver1_results, driver2_results):
    """
    Property: For any two drivers' race results, the points_ratio should be
    in the format "X.X:Y.Y" where X and Y are percentages.
    
    **Validates: Requirements 9.1**
    """
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    # Property: points_ratio has correct format
    assert ':' in pairing['points_ratio'], "points_ratio should contain ':'"
    
    # Parse the ratio
    parts = pairing['points_ratio'].split(':')
    assert len(parts) == 2, "points_ratio should have exactly two parts"


@given(driver1_results=driver_race_results_strategy(min_races=1, max_races=24),
       driver2_results=driver_race_results_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_driver_pairing_points_ratio_sums_to_100(driver1_results, driver2_results):
    """
    Property 11: Driver Pairing Effectiveness
    
    For any two drivers' race results from the same team, the points ratio
    between drivers should sum to 100%, and the imbalance flag should be set
    correctly when the ratio exceeds 70:30.
    
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    # Property: points_ratio should sum to 100% (or be "0.0:0.0" for no data)
    points_ratio = pairing['points_ratio']
    
    if points_ratio != "0.0:0.0":
        # Parse the ratio
        parts = points_ratio.split(':')
        assert len(parts) == 2, "points_ratio should have exactly two parts"
        
        driver1_pct = float(parts[0])
        driver2_pct = float(parts[1])
        
        # Property: Percentages should sum to 100 (with small tolerance for rounding)
        ratio_sum = driver1_pct + driver2_pct
        assert abs(ratio_sum - 100.0) < 0.2, \
            f"Points ratio should sum to 100%, got {driver1_pct}:{driver2_pct} = {ratio_sum}%"
        
        # Property: Each percentage should be between 0 and 100
        assert 0 <= driver1_pct <= 100, \
            f"Driver 1 percentage should be 0-100%, got {driver1_pct}%"
        assert 0 <= driver2_pct <= 100, \
            f"Driver 2 percentage should be 0-100%, got {driver2_pct}%"
        
        # Property: Imbalance flag should be set correctly
        # When either driver has >70% of points, flag should be "imbalanced"
        if driver1_pct > 70 or driver2_pct > 70:
            assert pairing['balance_flag'] == 'imbalanced', \
                f"With ratio {driver1_pct}:{driver2_pct}, balance_flag should be 'imbalanced', got '{pairing['balance_flag']}'"
        else:
            assert pairing['balance_flag'] == 'balanced', \
                f"With ratio {driver1_pct}:{driver2_pct}, balance_flag should be 'balanced', got '{pairing['balance_flag']}'"
    else:
        # Property: When no points data, balance_flag should be "no data"
        assert pairing['balance_flag'] == 'no data', \
            f"With no points data, balance_flag should be 'no data', got '{pairing['balance_flag']}'"
        
        # Property: Both drivers should have 0 points
        assert pairing['driver1_points'] == 0, \
            f"With no data, driver1_points should be 0, got {pairing['driver1_points']}"
        assert pairing['driver2_points'] == 0, \
            f"With no data, driver2_points should be 0, got {pairing['driver2_points']}"


@given(driver1_results=driver_race_results_strategy(min_races=1, max_races=24),
       driver2_results=driver_race_results_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_driver_pairing_quali_gap_non_negative(driver1_results, driver2_results):
    """
    Property: For any two drivers' race results, the quali_gap should be non-negative.
    
    **Validates: Requirements 9.2**
    """
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    # Property: quali_gap is non-negative
    assert pairing['quali_gap'] >= 0, \
        f"quali_gap should be non-negative, got {pairing['quali_gap']}"


@given(driver1_results=driver_race_results_strategy(min_races=1, max_races=24),
       driver2_results=driver_race_results_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_driver_pairing_race_gap_non_negative(driver1_results, driver2_results):
    """
    Property: For any two drivers' race results, the race_gap should be non-negative.
    
    **Validates: Requirements 9.3**
    """
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    # Property: race_gap is non-negative
    assert pairing['race_gap'] >= 0, \
        f"race_gap should be non-negative, got {pairing['race_gap']}"


@given(driver1_results=driver_race_results_strategy(min_races=1, max_races=24),
       driver2_results=driver_race_results_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_driver_pairing_balance_flag_valid(driver1_results, driver2_results):
    """
    Property: For any two drivers' race results, the balance_flag should be
    one of: "balanced", "imbalanced", or "no data".
    
    **Validates: Requirements 9.1**
    """
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    # Property: balance_flag is valid
    valid_flags = {'balanced', 'imbalanced', 'no data'}
    assert pairing['balance_flag'] in valid_flags, \
        f"balance_flag should be one of {valid_flags}, got '{pairing['balance_flag']}'"


@given(driver1_results=driver_race_results_strategy(min_races=1, max_races=24),
       driver2_results=driver_race_results_strategy(min_races=1, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_driver_pairing_points_non_negative(driver1_results, driver2_results):
    """
    Property: For any two drivers' race results, both driver points should be non-negative.
    
    **Validates: Requirements 9.1**
    """
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    # Property: Points are non-negative
    assert pairing['driver1_points'] >= 0, \
        f"driver1_points should be non-negative, got {pairing['driver1_points']}"
    assert pairing['driver2_points'] >= 0, \
        f"driver2_points should be non-negative, got {pairing['driver2_points']}"


def test_property_driver_pairing_imbalanced_flag():
    """
    Property: When points ratio exceeds 70:30, balance_flag should be "imbalanced".
    
    **Validates: Requirements 9.1**
    """
    # Create results where driver 1 dominates (>70% of points)
    driver1_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1', 'Driver': {'driverId': 'driver1'}}]
        }
        for i in range(1, 6)
    ]
    
    driver2_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': '10', 'points': '1', 'status': 'Finished', 'grid': '10', 'Driver': {'driverId': 'driver2'}}]
        }
        for i in range(1, 6)
    ]
    
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    # Driver 1: 125 points, Driver 2: 5 points
    # Ratio: 96.2:3.8 (highly imbalanced)
    assert pairing['balance_flag'] == 'imbalanced', \
        f"balance_flag should be 'imbalanced' with 96:4 ratio, got '{pairing['balance_flag']}'"


def test_property_driver_pairing_balanced_flag():
    """
    Property: When points ratio is within 70:30, balance_flag should be "balanced".
    
    **Validates: Requirements 9.1**
    """
    # Create results where drivers are balanced (60:40)
    driver1_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': str(i), 'points': str(25 - i*5), 'status': 'Finished', 'grid': str(i), 'Driver': {'driverId': 'driver1'}}]
        }
        for i in range(1, 6)
    ]
    
    driver2_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': str(i+1), 'points': str(20 - i*5), 'status': 'Finished', 'grid': str(i+1), 'Driver': {'driverId': 'driver2'}}]
        }
        for i in range(1, 6)
    ]
    
    pairing = calculate_analytics_driver_pairing(
        driver1_results, driver2_results,
        "Driver 1", "Driver 2"
    )
    
    # Driver 1: 75 points, Driver 2: 50 points
    # Ratio: 60:40 (balanced)
    assert pairing['balance_flag'] == 'balanced', \
        f"balance_flag should be 'balanced' with 60:40 ratio, got '{pairing['balance_flag']}'"


# ============================================================================
# Property 12: Circuit-Specific Performance
# **Validates: Requirements 10.1, 10.2, 10.3**
# ============================================================================

@given(race_results=race_results_list_strategy(min_races=0, max_races=10))
@settings(max_examples=100, deadline=None)
def test_property_circuit_performance_rates_in_range(race_results):
    """
    Feature: advanced-analytics, Property 12: Circuit-Specific Performance
    
    For any driver's race results at a circuit, win rate, podium rate, and 
    points rate should all be percentages between 0 and 100.
    
    **Validates: Requirements 10.1, 10.2, 10.3**
    """
    perf = calculate_analytics_circuit_performance(race_results, 'Test Circuit', min_appearances=3)
    
    assert 0 <= perf['win_rate'] <= 100, \
        f"Win rate should be 0-100, got {perf['win_rate']}"
    assert 0 <= perf['podium_rate'] <= 100, \
        f"Podium rate should be 0-100, got {perf['podium_rate']}"
    assert 0 <= perf['points_rate'] <= 100, \
        f"Points rate should be 0-100, got {perf['points_rate']}"


@given(race_results=race_results_list_strategy(min_races=1, max_races=10))
@settings(max_examples=100, deadline=None)
def test_property_circuit_performance_avg_finish_positive(race_results):
    """
    Feature: advanced-analytics, Property 12: Circuit-Specific Performance
    
    For any driver's race results with at least one finish, average finish 
    position should be positive (or None if no finishes).
    
    **Validates: Requirements 10.1, 10.2**
    """
    perf = calculate_analytics_circuit_performance(race_results, 'Test Circuit', min_appearances=3)
    
    if perf['avg_finish'] is not None:
        assert perf['avg_finish'] > 0, \
            f"Average finish should be positive, got {perf['avg_finish']}"


@given(race_results=race_results_list_strategy(min_races=0, max_races=10))
@settings(max_examples=100, deadline=None)
def test_property_circuit_performance_low_sample_warning(race_results):
    """
    Feature: advanced-analytics, Property 12: Circuit-Specific Performance
    
    For any driver's race results, low_sample_warning should be True when 
    appearances are below the minimum threshold.
    
    **Validates: Requirements 10.3**
    """
    min_appearances = 3
    perf = calculate_analytics_circuit_performance(race_results, 'Test Circuit', min_appearances=min_appearances)
    
    if perf['appearances'] < min_appearances:
        assert perf['low_sample_warning'] == True, \
            f"Should have low sample warning with {perf['appearances']} appearances (min {min_appearances})"
    else:
        assert perf['low_sample_warning'] == False, \
            f"Should not have low sample warning with {perf['appearances']} appearances (min {min_appearances})"


@given(race_results=race_results_list_strategy(min_races=1, max_races=10))
@settings(max_examples=100, deadline=None)
def test_property_circuit_performance_appearances_count(race_results):
    """
    Feature: advanced-analytics, Property 12: Circuit-Specific Performance
    
    For any driver's race results, appearances count should match the number 
    of race results provided.
    
    **Validates: Requirements 10.1**
    """
    perf = calculate_analytics_circuit_performance(race_results, 'Test Circuit', min_appearances=3)
    
    assert perf['appearances'] == len(race_results), \
        f"Appearances should be {len(race_results)}, got {perf['appearances']}"


def test_property_circuit_performance_all_wins():
    """
    Feature: advanced-analytics, Property 12: Circuit-Specific Performance
    
    When a driver wins all races at a circuit, win rate should be 100%,
    podium rate should be 100%, and points rate should be 100%.
    
    **Validates: Requirements 10.2, 10.3**
    """
    # Create race results with all wins
    race_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': str(i)}]
        }
        for i in range(1, 6)
    ]
    
    perf = calculate_analytics_circuit_performance(race_results, 'Monaco', min_appearances=3)
    
    assert perf['win_rate'] == 100.0, \
        f"All wins should give 100% win rate, got {perf['win_rate']}"
    assert perf['podium_rate'] == 100.0, \
        f"All wins should give 100% podium rate, got {perf['podium_rate']}"
    assert perf['points_rate'] == 100.0, \
        f"All wins should give 100% points rate, got {perf['points_rate']}"
    assert perf['avg_finish'] == 1.0, \
        f"All wins should give avg finish of 1.0, got {perf['avg_finish']}"


def test_property_circuit_performance_no_wins():
    """
    Feature: advanced-analytics, Property 12: Circuit-Specific Performance
    
    When a driver never wins at a circuit, win rate should be 0%.
    
    **Validates: Requirements 10.3**
    """
    # Create race results with no wins (positions 2-10)
    race_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': str(i+1), 'points': '18', 'status': 'Finished', 'grid': str(i)}]
        }
        for i in range(1, 6)
    ]
    
    perf = calculate_analytics_circuit_performance(race_results, 'Monaco', min_appearances=3)
    
    assert perf['win_rate'] == 0.0, \
        f"No wins should give 0% win rate, got {perf['win_rate']}"


def test_property_circuit_performance_all_podiums():
    """
    Feature: advanced-analytics, Property 12: Circuit-Specific Performance
    
    When a driver finishes on podium (positions 1-3) in all races,
    podium rate should be 100%.
    
    **Validates: Requirements 10.3**
    """
    # Create race results with all podiums (positions 1-3)
    race_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': str((i % 3) + 1), 'points': '15', 'status': 'Finished', 'grid': str(i)}]
        }
        for i in range(1, 6)
    ]
    
    perf = calculate_analytics_circuit_performance(race_results, 'Monaco', min_appearances=3)
    
    assert perf['podium_rate'] == 100.0, \
        f"All podiums should give 100% podium rate, got {perf['podium_rate']}"


def test_property_circuit_performance_all_dnf():
    """
    Feature: advanced-analytics, Property 12: Circuit-Specific Performance
    
    When a driver DNFs in all races at a circuit, all rates should be 0%
    and avg_finish should be None.
    
    **Validates: Requirements 10.2, 10.3**
    """
    # Create race results with all DNFs
    race_results = [
        {
            'raceName': f'Race {i}',
            'date': f'2024-03-{i:02d}',
            'round': str(i),
            'Results': [{'position': 'R', 'points': '0', 'status': 'Engine', 'grid': str(i)}]
        }
        for i in range(1, 6)
    ]
    
    perf = calculate_analytics_circuit_performance(race_results, 'Monaco', min_appearances=3)
    
    assert perf['win_rate'] == 0.0, \
        f"All DNFs should give 0% win rate, got {perf['win_rate']}"
    assert perf['podium_rate'] == 0.0, \
        f"All DNFs should give 0% podium rate, got {perf['podium_rate']}"
    assert perf['points_rate'] == 0.0, \
        f"All DNFs should give 0% points rate, got {perf['points_rate']}"
    assert perf['avg_finish'] is None, \
        f"All DNFs should give None avg finish, got {perf['avg_finish']}"


def test_property_circuit_performance_mixed_results():
    """
    Feature: advanced-analytics, Property 12: Circuit-Specific Performance
    
    Test with mixed results to verify correct calculation of all metrics.
    
    **Validates: Requirements 10.1, 10.2, 10.3**
    """
    # Create race results: 1 win, 1 podium (P3), 1 points (P5), 1 no points (P12), 1 DNF
    race_results = [
        {
            'raceName': 'Race 1',
            'date': '2024-03-01',
            'round': '1',
            'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '2'}]
        },
        {
            'raceName': 'Race 2',
            'date': '2024-03-02',
            'round': '2',
            'Results': [{'position': '3', 'points': '15', 'status': 'Finished', 'grid': '4'}]
        },
        {
            'raceName': 'Race 3',
            'date': '2024-03-03',
            'round': '3',
            'Results': [{'position': '5', 'points': '10', 'status': 'Finished', 'grid': '5'}]
        },
        {
            'raceName': 'Race 4',
            'date': '2024-03-04',
            'round': '4',
            'Results': [{'position': '12', 'points': '0', 'status': 'Finished', 'grid': '10'}]
        },
        {
            'raceName': 'Race 5',
            'date': '2024-03-05',
            'round': '5',
            'Results': [{'position': 'R', 'points': '0', 'status': 'Engine', 'grid': '1'}]
        }
    ]
    
    perf = calculate_analytics_circuit_performance(race_results, 'Monaco', min_appearances=3)
    
    # 1 win out of 5 races = 20%
    assert perf['win_rate'] == 20.0, \
        f"1 win in 5 races should give 20% win rate, got {perf['win_rate']}"
    
    # 2 podiums (P1, P3) out of 5 races = 40%
    assert perf['podium_rate'] == 40.0, \
        f"2 podiums in 5 races should give 40% podium rate, got {perf['podium_rate']}"
    
    # 3 points finishes (P1, P3, P5) out of 5 races = 60%
    assert perf['points_rate'] == 60.0, \
        f"3 points finishes in 5 races should give 60% points rate, got {perf['points_rate']}"
    
    # Average of finished races: (1 + 3 + 5 + 12) / 4 = 5.25
    assert perf['avg_finish'] == 5.25, \
        f"Average finish should be 5.25, got {perf['avg_finish']}"
    
    # 5 total appearances
    assert perf['appearances'] == 5, \
        f"Should have 5 appearances, got {perf['appearances']}"


def test_property_circuit_performance_empty_results():
    """
    Feature: advanced-analytics, Property 12: Circuit-Specific Performance
    
    When no race results are provided, function should return appropriate
    default values with low sample warning.
    
    **Validates: Requirements 10.1, 10.3**
    """
    perf = calculate_analytics_circuit_performance([], 'Monaco', min_appearances=3)
    
    assert perf['appearances'] == 0, \
        f"Empty results should give 0 appearances, got {perf['appearances']}"
    assert perf['avg_finish'] is None, \
        f"Empty results should give None avg finish, got {perf['avg_finish']}"
    assert perf['win_rate'] == 0.0, \
        f"Empty results should give 0% win rate, got {perf['win_rate']}"
    assert perf['podium_rate'] == 0.0, \
        f"Empty results should give 0% podium rate, got {perf['podium_rate']}"
    assert perf['points_rate'] == 0.0, \
        f"Empty results should give 0% points rate, got {perf['points_rate']}"
    assert perf['low_sample_warning'] == True, \
        f"Empty results should have low sample warning, got {perf['low_sample_warning']}"


# ============================================================================
# Property 13: Circuit Difficulty Rating
# **Validates: Requirements 11.1, 11.2, 11.3, 11.4**
# ============================================================================

@composite
def circuit_race_data_strategy(draw):
    """Generate race data with circuit information."""
    circuit_name = draw(st.sampled_from(['Monaco', 'Silverstone', 'Monza', 'Spa', 'Suzuka']))
    num_results = draw(st.integers(min_value=5, max_value=20))
    
    results = []
    for i in range(num_results):
        is_dnf = draw(st.booleans())
        if is_dnf:
            position = 'R'
            status = draw(st.sampled_from(['Engine', 'Accident', 'Collision', 'Gearbox']))
            grid = draw(st.integers(min_value=1, max_value=20))
        else:
            position = draw(st.integers(min_value=1, max_value=20))
            status = 'Finished'
            grid = draw(st.integers(min_value=1, max_value=20))
        
        results.append({
            'position': str(position) if isinstance(position, int) else position,
            'grid': str(grid),
            'status': status
        })
    
    return {
        'raceName': f'{circuit_name} Grand Prix',
        'date': '2024-01-01',
        'round': '1',
        'Circuit': {'circuitName': circuit_name},
        'Results': results
    }


@given(races=st.lists(circuit_race_data_strategy(), min_size=1, max_size=10))
@settings(max_examples=100, deadline=None)
def test_property_circuit_difficulty_score_range(races):
    """
    Feature: advanced-analytics, Property 13: Circuit Difficulty Rating
    
    For any collection of race results, difficulty scores should be in the 
    range 0-100 for all circuits.
    
    **Validates: Requirements 11.1, 11.2, 11.4**
    """
    df = calculate_analytics_circuit_difficulty(races, ['2024'])
    
    if len(df) > 0:
        for _, row in df.iterrows():
            assert 0 <= row['difficulty_score'] <= 100, \
                f"Difficulty score should be 0-100, got {row['difficulty_score']} for {row['circuit_name']}"


@given(races=st.lists(circuit_race_data_strategy(), min_size=1, max_size=10))
@settings(max_examples=100, deadline=None)
def test_property_circuit_difficulty_dnf_rate_range(races):
    """
    Feature: advanced-analytics, Property 13: Circuit Difficulty Rating
    
    For any collection of race results, DNF rates should be percentages 
    between 0 and 100.
    
    **Validates: Requirements 11.1**
    """
    df = calculate_analytics_circuit_difficulty(races, ['2024'])
    
    if len(df) > 0:
        for _, row in df.iterrows():
            assert 0 <= row['dnf_rate'] <= 100, \
                f"DNF rate should be 0-100, got {row['dnf_rate']} for {row['circuit_name']}"


@given(races=st.lists(circuit_race_data_strategy(), min_size=1, max_size=10))
@settings(max_examples=100, deadline=None)
def test_property_circuit_difficulty_position_change_non_negative(races):
    """
    Feature: advanced-analytics, Property 13: Circuit Difficulty Rating
    
    For any collection of race results, average position change should be 
    non-negative (absolute value).
    
    **Validates: Requirements 11.2**
    """
    df = calculate_analytics_circuit_difficulty(races, ['2024'])
    
    if len(df) > 0:
        for _, row in df.iterrows():
            assert row['avg_position_change'] >= 0, \
                f"Average position change should be non-negative, got {row['avg_position_change']} for {row['circuit_name']}"


@given(races=st.lists(circuit_race_data_strategy(), min_size=1, max_size=10))
@settings(max_examples=100, deadline=None)
def test_property_circuit_difficulty_dataframe_structure(races):
    """
    Feature: advanced-analytics, Property 13: Circuit Difficulty Rating
    
    For any collection of race results, the output should be a DataFrame with 
    required columns.
    
    **Validates: Requirements 11.1, 11.2, 11.4**
    """
    df = calculate_analytics_circuit_difficulty(races, ['2024'])
    
    assert isinstance(df, pd.DataFrame), "Output should be a DataFrame"
    
    required_columns = ['circuit_name', 'dnf_rate', 'avg_position_change', 'difficulty_score', 'races_analyzed']
    for col in required_columns:
        assert col in df.columns, f"DataFrame should have '{col}' column"


def test_property_circuit_difficulty_empty_input():
    """
    Feature: advanced-analytics, Property 13: Circuit Difficulty Rating
    
    For empty input, should return an empty DataFrame with correct columns.
    
    **Validates: Requirements 11.1, 11.2, 11.4**
    """
    df = calculate_analytics_circuit_difficulty([], [])
    
    assert isinstance(df, pd.DataFrame), "Output should be a DataFrame"
    assert len(df) == 0, "DataFrame should be empty"
    
    required_columns = ['circuit_name', 'dnf_rate', 'avg_position_change', 'difficulty_score', 'races_analyzed']
    for col in required_columns:
        assert col in df.columns, f"DataFrame should have '{col}' column"


# ============================================================================
# Property 14: Multi-Driver Comparison
# **Validates: Requirements 12.1, 12.2**
# ============================================================================

@composite
def drivers_data_strategy(draw, min_drivers=3, max_drivers=10):
    """
    Generate a dictionary mapping driver names to their race results.
    
    Args:
        min_drivers: Minimum number of drivers
        max_drivers: Maximum number of drivers
    
    Returns:
        Dict[str, list]: Mapping of driver_name to race_results list
    """
    num_drivers = draw(st.integers(min_value=min_drivers, max_value=max_drivers))
    drivers_data = {}
    
    for i in range(num_drivers):
        driver_name = f"Driver_{i+1}"
        # Generate race results for this driver
        race_results = draw(race_results_list_strategy(min_races=5, max_races=24))
        drivers_data[driver_name] = race_results
    
    return drivers_data


@given(drivers_data=drivers_data_strategy(min_drivers=3, max_drivers=10))
@settings(max_examples=100, deadline=None)
def test_property_multi_driver_comparison_all_drivers_included(drivers_data):
    """
    Feature: advanced-analytics, Property 14: Multi-Driver Comparison
    
    For any collection of 3 or more drivers' race results, the comparison
    should retrieve data for all selected drivers.
    
    **Validates: Requirements 12.1, 12.2**
    """
    result_df = calculate_analytics_multi_driver_comparison(drivers_data)
    
    # Property: DataFrame should have one row per driver
    assert len(result_df) == len(drivers_data), \
        f"Should have {len(drivers_data)} rows (one per driver), got {len(result_df)}"
    
    # Property: All driver names should be present
    result_driver_names = set(result_df['driver_name'].tolist())
    expected_driver_names = set(drivers_data.keys())
    
    assert result_driver_names == expected_driver_names, \
        f"Driver names mismatch. Expected {expected_driver_names}, got {result_driver_names}"


@given(drivers_data=drivers_data_strategy(min_drivers=3, max_drivers=10))
@settings(max_examples=100, deadline=None)
def test_property_multi_driver_comparison_standardized_metrics(drivers_data):
    """
    Feature: advanced-analytics, Property 14: Multi-Driver Comparison
    
    For any collection of drivers' race results, standardized metrics
    (average finish, points per race, consistency score, DNF rate) should
    be calculated for each driver.
    
    **Validates: Requirements 12.2**
    """
    result_df = calculate_analytics_multi_driver_comparison(drivers_data)
    
    # Property: DataFrame should have required metric columns
    required_columns = ['driver_name', 'avg_finish', 'points_per_race', 'consistency_score', 'dnf_rate']
    for col in required_columns:
        assert col in result_df.columns, \
            f"DataFrame should have '{col}' column"
    
    # Property: Each driver should have metrics calculated
    for idx, row in result_df.iterrows():
        driver_name = row['driver_name']
        
        # avg_finish should be positive or None
        if pd.notna(row['avg_finish']):
            assert row['avg_finish'] > 0, \
                f"{driver_name}: avg_finish should be positive, got {row['avg_finish']}"
            assert row['avg_finish'] <= 20, \
                f"{driver_name}: avg_finish should be <= 20, got {row['avg_finish']}"
        
        # points_per_race should be non-negative
        assert row['points_per_race'] >= 0, \
            f"{driver_name}: points_per_race should be non-negative, got {row['points_per_race']}"
        assert row['points_per_race'] <= 25, \
            f"{driver_name}: points_per_race should be <= 25, got {row['points_per_race']}"
        
        # consistency_score should be 0-100 or None
        if pd.notna(row['consistency_score']):
            assert 0 <= row['consistency_score'] <= 100, \
                f"{driver_name}: consistency_score should be 0-100, got {row['consistency_score']}"
        
        # dnf_rate should be 0-100
        assert 0 <= row['dnf_rate'] <= 100, \
            f"{driver_name}: dnf_rate should be 0-100, got {row['dnf_rate']}"


@given(drivers_data=drivers_data_strategy(min_drivers=3, max_drivers=10))
@settings(max_examples=100, deadline=None)
def test_property_multi_driver_comparison_avg_finish_calculation(drivers_data):
    """
    Feature: advanced-analytics, Property 14: Multi-Driver Comparison
    
    For any driver's race results, the average finish should be calculated
    correctly as the mean of finishing positions (excluding DNFs).
    
    **Validates: Requirements 12.2**
    """
    result_df = calculate_analytics_multi_driver_comparison(drivers_data)
    
    for idx, row in result_df.iterrows():
        driver_name = row['driver_name']
        race_results = drivers_data[driver_name]
        
        # Manually calculate expected average finish
        finished_positions = []
        for race in race_results:
            results = race.get('Results', [])
            if results:
                result = results[0]
                status = result.get('status', 'Finished')
                position = result.get('position', 'R')
                
                # Only include finished races
                if status == 'Finished' and position != 'R':
                    try:
                        pos_int = int(position)
                        if pos_int > 0:
                            finished_positions.append(pos_int)
                    except (ValueError, TypeError):
                        pass
        
        if finished_positions:
            expected_avg = sum(finished_positions) / len(finished_positions)
            
            # Property: Calculated average should match expected
            if pd.notna(row['avg_finish']):
                assert abs(row['avg_finish'] - expected_avg) < 0.01, \
                    f"{driver_name}: avg_finish {row['avg_finish']} doesn't match expected {expected_avg}"


@given(drivers_data=drivers_data_strategy(min_drivers=3, max_drivers=10))
@settings(max_examples=100, deadline=None)
def test_property_multi_driver_comparison_points_per_race_calculation(drivers_data):
    """
    Feature: advanced-analytics, Property 14: Multi-Driver Comparison
    
    For any driver's race results, points per race should be calculated
    correctly as total points divided by total races.
    
    **Validates: Requirements 12.2**
    """
    result_df = calculate_analytics_multi_driver_comparison(drivers_data)
    
    for idx, row in result_df.iterrows():
        driver_name = row['driver_name']
        race_results = drivers_data[driver_name]
        
        # Manually calculate expected points per race
        total_points = 0
        for race in race_results:
            results = race.get('Results', [])
            if results:
                result = results[0]
                points_str = result.get('points', '0')
                try:
                    total_points += float(points_str)
                except (ValueError, TypeError):
                    pass
        
        races_count = len(race_results)
        if races_count > 0:
            expected_ppr = total_points / races_count
            
            # Property: Calculated points per race should match expected
            assert abs(row['points_per_race'] - expected_ppr) < 0.01, \
                f"{driver_name}: points_per_race {row['points_per_race']} doesn't match expected {expected_ppr}"


@given(drivers_data=drivers_data_strategy(min_drivers=3, max_drivers=10))
@settings(max_examples=100, deadline=None)
def test_property_multi_driver_comparison_dnf_rate_calculation(drivers_data):
    """
    Feature: advanced-analytics, Property 14: Multi-Driver Comparison
    
    For any driver's race results, DNF rate should be calculated correctly
    as percentage of races ending in DNF.
    
    **Validates: Requirements 12.2**
    """
    result_df = calculate_analytics_multi_driver_comparison(drivers_data)
    
    for idx, row in result_df.iterrows():
        driver_name = row['driver_name']
        race_results = drivers_data[driver_name]
        
        # Manually calculate expected DNF rate
        dnf_count = 0
        total_races = len(race_results)
        
        for race in race_results:
            results = race.get('Results', [])
            if results:
                result = results[0]
                status = result.get('status', 'Finished')
                
                # Check if it's a DNF
                dnf_statuses = ['Engine', 'Gearbox', 'Accident', 'Collision', 'Hydraulics', 
                               'Electrical', 'Spun off', 'Retired', 'Mechanical', 'Brakes', 
                               'Suspension', 'Fuel pressure', 'Overheating']
                if status in dnf_statuses or status.startswith('+'):
                    dnf_count += 1
        
        if total_races > 0:
            expected_dnf_rate = (dnf_count / total_races) * 100
            
            # Property: Calculated DNF rate should match expected
            assert abs(row['dnf_rate'] - expected_dnf_rate) < 0.1, \
                f"{driver_name}: dnf_rate {row['dnf_rate']} doesn't match expected {expected_dnf_rate}"


def test_property_multi_driver_comparison_empty_input():
    """
    Feature: advanced-analytics, Property 14: Multi-Driver Comparison
    
    For empty input, should return an empty DataFrame with correct columns.
    
    **Validates: Requirements 12.1**
    """
    result_df = calculate_analytics_multi_driver_comparison({})
    
    # Property: Should return empty DataFrame
    assert isinstance(result_df, pd.DataFrame), \
        "Should return a DataFrame"
    assert len(result_df) == 0, \
        "DataFrame should be empty for empty input"


def test_property_multi_driver_comparison_minimum_drivers():
    """
    Feature: advanced-analytics, Property 14: Multi-Driver Comparison
    
    For 3 drivers (minimum), should calculate metrics for all drivers.
    
    **Validates: Requirements 12.1, 12.2**
    """
    # Create data for exactly 3 drivers
    drivers_data = {
        'Driver_A': [
            {
                'raceName': 'Race 1',
                'date': '2024-03-01',
                'round': '1',
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            },
            {
                'raceName': 'Race 2',
                'date': '2024-03-08',
                'round': '2',
                'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '2'}]
            },
            {
                'raceName': 'Race 3',
                'date': '2024-03-15',
                'round': '3',
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            },
            {
                'raceName': 'Race 4',
                'date': '2024-03-22',
                'round': '4',
                'Results': [{'position': '3', 'points': '15', 'status': 'Finished', 'grid': '3'}]
            },
            {
                'raceName': 'Race 5',
                'date': '2024-03-29',
                'round': '5',
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            }
        ],
        'Driver_B': [
            {
                'raceName': 'Race 1',
                'date': '2024-03-01',
                'round': '1',
                'Results': [{'position': '3', 'points': '15', 'status': 'Finished', 'grid': '3'}]
            },
            {
                'raceName': 'Race 2',
                'date': '2024-03-08',
                'round': '2',
                'Results': [{'position': '4', 'points': '12', 'status': 'Finished', 'grid': '4'}]
            },
            {
                'raceName': 'Race 3',
                'date': '2024-03-15',
                'round': '3',
                'Results': [{'position': '5', 'points': '10', 'status': 'Finished', 'grid': '5'}]
            },
            {
                'raceName': 'Race 4',
                'date': '2024-03-22',
                'round': '4',
                'Results': [{'position': '6', 'points': '8', 'status': 'Finished', 'grid': '6'}]
            },
            {
                'raceName': 'Race 5',
                'date': '2024-03-29',
                'round': '5',
                'Results': [{'position': '7', 'points': '6', 'status': 'Finished', 'grid': '7'}]
            }
        ],
        'Driver_C': [
            {
                'raceName': 'Race 1',
                'date': '2024-03-01',
                'round': '1',
                'Results': [{'position': '10', 'points': '1', 'status': 'Finished', 'grid': '10'}]
            },
            {
                'raceName': 'Race 2',
                'date': '2024-03-08',
                'round': '2',
                'Results': [{'position': 'R', 'points': '0', 'status': 'Engine', 'grid': '8'}]
            },
            {
                'raceName': 'Race 3',
                'date': '2024-03-15',
                'round': '3',
                'Results': [{'position': '12', 'points': '0', 'status': 'Finished', 'grid': '12'}]
            },
            {
                'raceName': 'Race 4',
                'date': '2024-03-22',
                'round': '4',
                'Results': [{'position': '11', 'points': '0', 'status': 'Finished', 'grid': '11'}]
            },
            {
                'raceName': 'Race 5',
                'date': '2024-03-29',
                'round': '5',
                'Results': [{'position': '9', 'points': '2', 'status': 'Finished', 'grid': '9'}]
            }
        ]
    }
    
    result_df = calculate_analytics_multi_driver_comparison(drivers_data)
    
    # Property: Should have exactly 3 rows
    assert len(result_df) == 3, \
        f"Should have 3 rows for 3 drivers, got {len(result_df)}"
    
    # Property: All drivers should be present
    driver_names = set(result_df['driver_name'].tolist())
    assert driver_names == {'Driver_A', 'Driver_B', 'Driver_C'}, \
        f"Should have all 3 drivers, got {driver_names}"
    
    # Property: Driver_A should have best metrics (lowest avg_finish, highest points_per_race)
    driver_a_row = result_df[result_df['driver_name'] == 'Driver_A'].iloc[0]
    driver_b_row = result_df[result_df['driver_name'] == 'Driver_B'].iloc[0]
    driver_c_row = result_df[result_df['driver_name'] == 'Driver_C'].iloc[0]
    
    assert driver_a_row['avg_finish'] < driver_b_row['avg_finish'], \
        "Driver_A should have better avg_finish than Driver_B"
    assert driver_a_row['points_per_race'] > driver_b_row['points_per_race'], \
        "Driver_A should have higher points_per_race than Driver_B"
    
    # Property: Driver_C should have a DNF (DNF rate > 0)
    assert driver_c_row['dnf_rate'] > 0, \
        "Driver_C should have DNF rate > 0"


def test_property_multi_driver_comparison_maximum_drivers():
    """
    Feature: advanced-analytics, Property 14: Multi-Driver Comparison
    
    For 10 drivers (maximum per requirements), should calculate metrics for all drivers.
    
    **Validates: Requirements 12.5**
    """
    # Create data for exactly 10 drivers
    drivers_data = {}
    for i in range(10):
        driver_name = f'Driver_{i+1}'
        drivers_data[driver_name] = [
            {
                'raceName': f'Race {j}',
                'date': f'2024-03-{j:02d}',
                'round': str(j),
                'Results': [{'position': str((i+j) % 20 + 1), 'points': '10', 'status': 'Finished', 'grid': '5'}]
            }
            for j in range(1, 6)
        ]
    
    result_df = calculate_analytics_multi_driver_comparison(drivers_data)
    
    # Property: Should have exactly 10 rows
    assert len(result_df) == 10, \
        f"Should have 10 rows for 10 drivers, got {len(result_df)}"
    
    # Property: All drivers should be present
    driver_names = set(result_df['driver_name'].tolist())
    expected_names = {f'Driver_{i+1}' for i in range(10)}
    assert driver_names == expected_names, \
        f"Should have all 10 drivers"


def test_property_multi_driver_comparison_custom_metrics():
    """
    Feature: advanced-analytics, Property 14: Multi-Driver Comparison
    
    When custom metrics are specified, only those metrics should be calculated.
    
    **Validates: Requirements 12.2**
    """
    # Create data for 3 drivers
    drivers_data = {
        'Driver_A': [
            {
                'raceName': 'Race 1',
                'date': '2024-03-01',
                'round': '1',
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            },
            {
                'raceName': 'Race 2',
                'date': '2024-03-08',
                'round': '2',
                'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '2'}]
            },
            {
                'raceName': 'Race 3',
                'date': '2024-03-15',
                'round': '3',
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            },
            {
                'raceName': 'Race 4',
                'date': '2024-03-22',
                'round': '4',
                'Results': [{'position': '3', 'points': '15', 'status': 'Finished', 'grid': '3'}]
            },
            {
                'raceName': 'Race 5',
                'date': '2024-03-29',
                'round': '5',
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            }
        ]
    }
    
    # Test with only avg_finish and points_per_race
    result_df = calculate_analytics_multi_driver_comparison(drivers_data, metrics=['avg_finish', 'points_per_race'])
    
    # Property: Should have driver_name column plus requested metrics
    assert 'driver_name' in result_df.columns, "Should have driver_name column"
    assert 'avg_finish' in result_df.columns, "Should have avg_finish column"
    assert 'points_per_race' in result_df.columns, "Should have points_per_race column"
    
    # Property: Should not have unrequested metrics
    assert 'consistency_score' not in result_df.columns, "Should not have consistency_score column"
    assert 'dnf_rate' not in result_df.columns, "Should not have dnf_rate column"


# ============================================================================
# Property 15: Season-Over-Season Comparison
# **Validates: Requirements 13.1, 13.2, 13.4, 13.5**
# ============================================================================

@composite
def season_results_strategy(draw, min_seasons=2, max_seasons=5):
    """
    Generate a dictionary mapping seasons to race results lists.
    
    This ensures we have multiple seasons for comparison.
    """
    num_seasons = draw(st.integers(min_value=min_seasons, max_value=max_seasons))
    season_results = {}
    
    # Generate seasons from 2005 to 2024 to test both old and new scoring systems
    base_year = draw(st.integers(min_value=2005, max_value=2020))
    
    for i in range(num_seasons):
        season = str(base_year + i)
        num_races = draw(st.integers(min_value=5, max_value=22))
        
        races = []
        for j in range(num_races):
            race_name = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
            month = draw(st.integers(min_value=1, max_value=12))
            day = draw(st.integers(min_value=1, max_value=28))
            race_date = f"{base_year + i:04d}-{month:02d}-{day:02d}"
            
            # Generate position - either a valid position (1-20) or 'R' for retirement
            is_dnf = draw(st.booleans())
            if is_dnf:
                position = 'R'
                points = '0'
                status = draw(st.sampled_from(['Engine', 'Gearbox', 'Accident', 'Collision']))
            else:
                position_int = draw(st.integers(min_value=1, max_value=20))
                position = str(position_int)
                # Points based on position (simplified F1 points system)
                points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
                points = str(points_map.get(position_int, 0))
                status = 'Finished'
            
            grid = draw(st.integers(min_value=1, max_value=20))
            
            race = {
                'raceName': race_name,
                'date': race_date,
                'round': str(j + 1),
                'season': season,
                'Results': [{
                    'position': position,
                    'points': points,
                    'status': status,
                    'grid': str(grid)
                }]
            }
            
            races.append(race)
        
        season_results[season] = races
    
    return season_results


@given(season_results=season_results_strategy(min_seasons=2, max_seasons=5))
@settings(max_examples=100, deadline=None)
def test_property_season_comparison_one_row_per_season(season_results):
    """
    Feature: advanced-analytics, Property 15: Season-Over-Season Comparison
    
    For any entity's race results across multiple seasons, the comparison
    should produce a DataFrame with exactly one row per season.
    
    **Validates: Requirements 13.1, 13.2**
    """
    from app import calculate_analytics_season_comparison
    
    result_df = calculate_analytics_season_comparison(season_results, entity_type="driver")
    
    # Property: One row per season
    assert len(result_df) == len(season_results), \
        f"Expected {len(season_results)} rows (one per season), got {len(result_df)}"
    
    # Property: All seasons should be present
    result_seasons = set(result_df['season'].astype(str))
    expected_seasons = set(season_results.keys())
    assert result_seasons == expected_seasons, \
        f"Expected seasons {expected_seasons}, got {result_seasons}"


@given(season_results=season_results_strategy(min_seasons=2, max_seasons=5))
@settings(max_examples=100, deadline=None)
def test_property_season_comparison_correct_columns(season_results):
    """
    Feature: advanced-analytics, Property 15: Season-Over-Season Comparison
    
    For any entity's race results across multiple seasons, the DataFrame
    should have the correct columns including season, metrics, and yoy_change_pct.
    
    **Validates: Requirements 13.1, 13.2, 13.4**
    """
    from app import calculate_analytics_season_comparison
    
    result_df = calculate_analytics_season_comparison(season_results, entity_type="driver")
    
    # Property: Required columns exist
    required_columns = {'season', 'avg_finish', 'total_points', 'points_per_race', 
                       'consistency_score', 'yoy_change_pct', 'normalized_points_per_race'}
    actual_columns = set(result_df.columns)
    
    assert required_columns.issubset(actual_columns), \
        f"Missing columns: {required_columns - actual_columns}"


@given(season_results=season_results_strategy(min_seasons=2, max_seasons=5))
@settings(max_examples=100, deadline=None)
def test_property_season_comparison_yoy_change_calculation(season_results):
    """
    Feature: advanced-analytics, Property 15: Season-Over-Season Comparison
    
    For any entity's race results across multiple seasons, the year-over-year
    percentage change should be calculated correctly as:
    ((current_ppr - previous_ppr) / previous_ppr) * 100
    
    **Validates: Requirements 13.4**
    """
    from app import calculate_analytics_season_comparison
    
    result_df = calculate_analytics_season_comparison(season_results, entity_type="driver")
    
    if len(result_df) > 1:
        # Property: First season should have None for yoy_change_pct
        first_yoy = result_df.iloc[0]['yoy_change_pct']
        assert pd.isna(first_yoy), \
            f"First season should have None for yoy_change_pct, got {first_yoy}"
        
        # Property: Subsequent seasons should have calculated yoy_change_pct
        for i in range(1, len(result_df)):
            prev_ppr = result_df.iloc[i-1]['points_per_race']
            curr_ppr = result_df.iloc[i]['points_per_race']
            yoy_change = result_df.iloc[i]['yoy_change_pct']
            
            if prev_ppr > 0:
                # Calculate expected yoy change
                expected_yoy = ((curr_ppr - prev_ppr) / prev_ppr) * 100
                
                # Property: yoy_change should match calculation
                if pd.notna(yoy_change):
                    assert abs(yoy_change - expected_yoy) < 0.2, \
                        f"Season {i}: yoy_change {yoy_change} doesn't match expected {expected_yoy}"
            else:
                # If previous points per race is 0, yoy_change should be None
                assert pd.isna(yoy_change), \
                    f"Season {i}: yoy_change should be None when prev_ppr is 0, got {yoy_change}"


@given(season_results=season_results_strategy(min_seasons=2, max_seasons=5))
@settings(max_examples=100, deadline=None)
def test_property_season_comparison_points_normalization(season_results):
    """
    Feature: advanced-analytics, Property 15: Season-Over-Season Comparison
    
    For any entity's race results across multiple seasons, points should be
    normalized when scoring systems differ between seasons. Pre-2010 seasons
    (10 points for win) should be multiplied by 2.5 to normalize to modern
    system (25 points for win).
    
    **Validates: Requirements 13.5**
    """
    from app import calculate_analytics_season_comparison
    
    result_df = calculate_analytics_season_comparison(season_results, entity_type="driver")
    
    # Property: normalized_points_per_race column should exist
    assert 'normalized_points_per_race' in result_df.columns, \
        "Should have normalized_points_per_race column"
    
    for idx, row in result_df.iterrows():
        season_year = int(row['season'])
        points_per_race = row['points_per_race']
        normalized_ppr = row['normalized_points_per_race']
        
        # Property: Pre-2010 seasons should have normalized points = points * 2.5
        if season_year < 2010:
            expected_normalized = points_per_race * 2.5
            assert abs(normalized_ppr - expected_normalized) < 0.01, \
                f"Season {season_year}: normalized_ppr {normalized_ppr} should be {expected_normalized} (ppr * 2.5)"
        else:
            # Property: 2010+ seasons should have normalized points = points (no change)
            assert abs(normalized_ppr - points_per_race) < 0.01, \
                f"Season {season_year}: normalized_ppr {normalized_ppr} should equal ppr {points_per_race}"


@given(season_results=season_results_strategy(min_seasons=2, max_seasons=5))
@settings(max_examples=100, deadline=None)
def test_property_season_comparison_metrics_calculation(season_results):
    """
    Feature: advanced-analytics, Property 15: Season-Over-Season Comparison
    
    For any entity's race results across multiple seasons, key metrics
    (avg_finish, total_points, points_per_race) should be calculated correctly
    for each season.
    
    **Validates: Requirements 13.1, 13.2**
    """
    from app import calculate_analytics_season_comparison
    
    result_df = calculate_analytics_season_comparison(season_results, entity_type="driver")
    
    for idx, row in result_df.iterrows():
        season = row['season']
        races = season_results[season]
        
        # Calculate expected total points
        expected_total_points = 0
        finished_positions = []
        
        for race in races:
            results = race.get('Results', [])
            if results:
                result = results[0]
                points = float(result.get('points', 0))
                expected_total_points += points
                
                status = result.get('status', 'Finished')
                position = result.get('position', 'R')
                
                # Track finished positions for avg_finish calculation
                if status == 'Finished' and position != 'R':
                    try:
                        pos_int = int(position)
                        if pos_int > 0:
                            finished_positions.append(pos_int)
                    except (ValueError, TypeError):
                        pass
        
        # Property: total_points should match sum of points from all races
        assert abs(row['total_points'] - expected_total_points) < 0.1, \
            f"Season {season}: total_points {row['total_points']} doesn't match expected {expected_total_points}"
        
        # Property: points_per_race should be total_points / num_races
        expected_ppr = expected_total_points / len(races) if len(races) > 0 else 0
        assert abs(row['points_per_race'] - expected_ppr) < 0.01, \
            f"Season {season}: points_per_race {row['points_per_race']} doesn't match expected {expected_ppr}"
        
        # Property: avg_finish should match average of finished positions
        if finished_positions:
            expected_avg_finish = sum(finished_positions) / len(finished_positions)
            if pd.notna(row['avg_finish']):
                assert abs(row['avg_finish'] - expected_avg_finish) < 0.01, \
                    f"Season {season}: avg_finish {row['avg_finish']} doesn't match expected {expected_avg_finish}"
        else:
            # If no finished races, avg_finish should be None
            assert pd.isna(row['avg_finish']), \
                f"Season {season}: avg_finish should be None when no finished races, got {row['avg_finish']}"


@given(season_results=season_results_strategy(min_seasons=2, max_seasons=5))
@settings(max_examples=100, deadline=None)
def test_property_season_comparison_chronological_order(season_results):
    """
    Feature: advanced-analytics, Property 15: Season-Over-Season Comparison
    
    For any entity's race results across multiple seasons, the DataFrame
    should be sorted chronologically by season.
    
    **Validates: Requirements 13.1**
    """
    from app import calculate_analytics_season_comparison
    
    result_df = calculate_analytics_season_comparison(season_results, entity_type="driver")
    
    if len(result_df) > 1:
        # Property: Seasons should be in chronological order
        seasons = result_df['season'].astype(int).tolist()
        sorted_seasons = sorted(seasons)
        
        assert seasons == sorted_seasons, \
            f"Seasons should be chronologically ordered, got {seasons}, expected {sorted_seasons}"


def test_property_season_comparison_empty_input():
    """
    Feature: advanced-analytics, Property 15: Season-Over-Season Comparison
    
    For empty input, should return an empty DataFrame.
    
    **Validates: Requirements 13.1**
    """
    from app import calculate_analytics_season_comparison
    
    result_df = calculate_analytics_season_comparison({}, entity_type="driver")
    
    # Property: Empty input should produce empty DataFrame
    assert len(result_df) == 0, \
        f"Empty input should produce empty DataFrame, got {len(result_df)} rows"


def test_property_season_comparison_single_season():
    """
    Feature: advanced-analytics, Property 15: Season-Over-Season Comparison
    
    For a single season, should calculate metrics but yoy_change_pct should be None.
    
    **Validates: Requirements 13.1, 13.4**
    """
    from app import calculate_analytics_season_comparison
    
    season_results = {
        '2024': [
            {
                'raceName': 'Race 1',
                'date': '2024-03-01',
                'round': '1',
                'season': '2024',
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            },
            {
                'raceName': 'Race 2',
                'date': '2024-03-08',
                'round': '2',
                'season': '2024',
                'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '2'}]
            },
            {
                'raceName': 'Race 3',
                'date': '2024-03-15',
                'round': '3',
                'season': '2024',
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            },
            {
                'raceName': 'Race 4',
                'date': '2024-03-22',
                'round': '4',
                'season': '2024',
                'Results': [{'position': '3', 'points': '15', 'status': 'Finished', 'grid': '3'}]
            },
            {
                'raceName': 'Race 5',
                'date': '2024-03-29',
                'round': '5',
                'season': '2024',
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            }
        ]
    }
    
    result_df = calculate_analytics_season_comparison(season_results, entity_type="driver")
    
    # Property: Should have one row
    assert len(result_df) == 1, \
        f"Single season should produce one row, got {len(result_df)}"
    
    # Property: yoy_change_pct should be None for single season
    yoy_change = result_df.iloc[0]['yoy_change_pct']
    assert pd.isna(yoy_change), \
        f"Single season should have None for yoy_change_pct, got {yoy_change}"


def test_property_season_comparison_pre_2010_normalization():
    """
    Feature: advanced-analytics, Property 15: Season-Over-Season Comparison
    
    For seasons before 2010, points should be normalized by multiplying by 2.5
    to account for the old scoring system (10 points for win vs 25 points).
    
    **Validates: Requirements 13.5**
    """
    from app import calculate_analytics_season_comparison
    
    # Create data with pre-2010 and post-2010 seasons
    season_results = {
        '2008': [
            {
                'raceName': 'Race 1',
                'date': '2008-03-01',
                'round': '1',
                'season': '2008',
                'Results': [{'position': '1', 'points': '10', 'status': 'Finished', 'grid': '1'}]
            },
            {
                'raceName': 'Race 2',
                'date': '2008-03-08',
                'round': '2',
                'season': '2008',
                'Results': [{'position': '2', 'points': '8', 'status': 'Finished', 'grid': '2'}]
            }
        ],
        '2010': [
            {
                'raceName': 'Race 1',
                'date': '2010-03-01',
                'round': '1',
                'season': '2010',
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            },
            {
                'raceName': 'Race 2',
                'date': '2010-03-08',
                'round': '2',
                'season': '2010',
                'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '2'}]
            }
        ]
    }
    
    result_df = calculate_analytics_season_comparison(season_results, entity_type="driver")
    
    # Find 2008 and 2010 rows
    row_2008 = result_df[result_df['season'] == '2008'].iloc[0]
    row_2010 = result_df[result_df['season'] == '2010'].iloc[0]
    
    # Property: 2008 normalized points should be points_per_race * 2.5
    expected_2008_normalized = row_2008['points_per_race'] * 2.5
    assert abs(row_2008['normalized_points_per_race'] - expected_2008_normalized) < 0.01, \
        f"2008 normalized_ppr {row_2008['normalized_points_per_race']} should be {expected_2008_normalized}"
    
    # Property: 2010 normalized points should equal points_per_race (no change)
    assert abs(row_2010['normalized_points_per_race'] - row_2010['points_per_race']) < 0.01, \
        f"2010 normalized_ppr {row_2010['normalized_points_per_race']} should equal ppr {row_2010['points_per_race']}"


def test_property_season_comparison_entity_type_parameter():
    """
    Feature: advanced-analytics, Property 15: Season-Over-Season Comparison
    
    The function should accept both "driver" and "constructor" entity types
    and process them correctly.
    
    **Validates: Requirements 13.1, 13.2**
    """
    from app import calculate_analytics_season_comparison
    
    season_results = {
        '2024': [
            {
                'raceName': 'Race 1',
                'date': '2024-03-01',
                'round': '1',
                'season': '2024',
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            },
            {
                'raceName': 'Race 2',
                'date': '2024-03-08',
                'round': '2',
                'season': '2024',
                'Results': [{'position': '2', 'points': '18', 'status': 'Finished', 'grid': '2'}]
            }
        ]
    }
    
    # Test with driver entity type
    result_driver = calculate_analytics_season_comparison(season_results, entity_type="driver")
    assert len(result_driver) == 1, "Should process driver entity type"
    
    # Test with constructor entity type
    result_constructor = calculate_analytics_season_comparison(season_results, entity_type="constructor")
    assert len(result_constructor) == 1, "Should process constructor entity type"
    
    # Property: Both should produce same structure (same columns)
    assert set(result_driver.columns) == set(result_constructor.columns), \
        "Driver and constructor comparisons should have same column structure"


# ============================================================================
# Property 16: Percentile Rankings
# **Validates: Requirements 14.1, 14.2, 14.3, 14.4**
# ============================================================================

@composite
def all_drivers_results_strategy(draw, num_drivers=10, min_races=5, max_races=24):
    """
    Generate a dictionary of all drivers' results for percentile ranking tests.
    
    Args:
        num_drivers: Number of drivers to generate
        min_races: Minimum races per driver
        max_races: Maximum races per driver
    """
    all_drivers = {}
    
    for i in range(num_drivers):
        driver_name = f"Driver{i+1}"
        num_races = draw(st.integers(min_value=min_races, max_value=max_races))
        
        races = []
        for j in range(num_races):
            race_name = f"Race {j+1}"
            year = draw(st.integers(min_value=2020, max_value=2024))
            month = draw(st.integers(min_value=1, max_value=12))
            day = draw(st.integers(min_value=1, max_value=28))
            race_date = f"{year:04d}-{month:02d}-{day:02d}"
            
            # Generate position - either a valid position (1-20) or 'R' for retirement
            is_dnf = draw(st.booleans())
            if is_dnf:
                position = 'R'
                points = '0'
                status = draw(st.sampled_from(['Engine', 'Gearbox', 'Accident', 'Collision']))
            else:
                position_int = draw(st.integers(min_value=1, max_value=20))
                position = str(position_int)
                # Points based on position (simplified F1 points system)
                points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
                points = str(points_map.get(position_int, 0))
                status = 'Finished'
            
            grid = draw(st.integers(min_value=1, max_value=20))
            
            race = {
                'raceName': race_name,
                'date': race_date,
                'round': str(j + 1),
                'Results': [{
                    'position': position,
                    'points': points,
                    'status': status,
                    'grid': str(grid)
                }]
            }
            
            races.append(race)
        
        all_drivers[driver_name] = races
    
    return all_drivers


@given(all_drivers_results=all_drivers_results_strategy(num_drivers=10, min_races=10, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_percentile_rankings_range(all_drivers_results):
    """
    Feature: advanced-analytics, Property 16: Percentile Rankings
    
    For any driver's results and the full field's results for a season,
    the percentile rankings should be between 0-100 for all metrics.
    
    **Validates: Requirements 14.1, 14.2, 14.3, 14.4**
    """
    from app import calculate_analytics_percentile_rankings
    
    # Pick the first driver as the target driver
    if not all_drivers_results:
        return
    
    target_driver_name = list(all_drivers_results.keys())[0]
    driver_results = all_drivers_results[target_driver_name]
    
    result = calculate_analytics_percentile_rankings(
        driver_results,
        all_drivers_results,
        "2024"
    )
    
    # Property: All percentile values should be in range 0-100
    assert 0 <= result['avg_finish_percentile'] <= 100, \
        f"avg_finish_percentile should be 0-100, got {result['avg_finish_percentile']}"
    
    assert 0 <= result['points_percentile'] <= 100, \
        f"points_percentile should be 0-100, got {result['points_percentile']}"
    
    assert 0 <= result['consistency_percentile'] <= 100, \
        f"consistency_percentile should be 0-100, got {result['consistency_percentile']}"
    
    # Property: field_size should be positive
    assert result['field_size'] > 0, \
        f"field_size should be positive, got {result['field_size']}"


@given(all_drivers_results=all_drivers_results_strategy(num_drivers=10, min_races=10, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_percentile_rankings_field_size(all_drivers_results):
    """
    Feature: advanced-analytics, Property 16: Percentile Rankings
    
    The field_size should match the number of drivers who competed in at least
    50% of the season races.
    
    **Validates: Requirements 14.4**
    """
    from app import calculate_analytics_percentile_rankings
    
    if not all_drivers_results:
        return
    
    target_driver_name = list(all_drivers_results.keys())[0]
    driver_results = all_drivers_results[target_driver_name]
    
    result = calculate_analytics_percentile_rankings(
        driver_results,
        all_drivers_results,
        "2024"
    )
    
    # Calculate expected field size (drivers with >= 50% of races)
    total_races = len(driver_results)
    min_races = max(1, total_races // 2)
    
    expected_field_size = sum(
        1 for results in all_drivers_results.values()
        if len(results) >= min_races
    )
    
    # Property: field_size should match qualified drivers count
    assert result['field_size'] == expected_field_size, \
        f"field_size {result['field_size']} should match expected {expected_field_size}"


@given(all_drivers_results=all_drivers_results_strategy(num_drivers=10, min_races=10, max_races=24))
@settings(max_examples=100, deadline=None)
def test_property_percentile_rankings_relative_to_field(all_drivers_results):
    """
    Feature: advanced-analytics, Property 16: Percentile Rankings
    
    Percentile rankings should be calculated relative to all drivers who
    competed in at least 50% of season races.
    
    **Validates: Requirements 14.4**
    """
    from app import calculate_analytics_percentile_rankings
    
    if not all_drivers_results:
        return
    
    target_driver_name = list(all_drivers_results.keys())[0]
    driver_results = all_drivers_results[target_driver_name]
    
    result = calculate_analytics_percentile_rankings(
        driver_results,
        all_drivers_results,
        "2024"
    )
    
    # Property: If field_size is 1 (only target driver qualifies), percentiles should be 0
    if result['field_size'] == 1:
        # With only one driver, they are at the 0th percentile (no one is worse)
        assert result['avg_finish_percentile'] == 0.0, \
            f"Single driver should have 0th percentile for avg_finish, got {result['avg_finish_percentile']}"
        assert result['points_percentile'] == 0.0, \
            f"Single driver should have 0th percentile for points, got {result['points_percentile']}"
        assert result['consistency_percentile'] == 0.0, \
            f"Single driver should have 0th percentile for consistency, got {result['consistency_percentile']}"


def test_property_percentile_rankings_best_driver():
    """
    Feature: advanced-analytics, Property 16: Percentile Rankings
    
    A driver with the best average finish, most points, and best consistency
    should have the highest percentile for all metrics.
    
    **Validates: Requirements 14.1, 14.2, 14.3**
    """
    from app import calculate_analytics_percentile_rankings
    
    # Create a field where Driver1 is clearly the best
    # Give drivers varying positions to ensure different consistency scores
    all_drivers_results = {
        'Driver1': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            }
            for i in range(1, 11)
        ],
        'Driver2': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': str(5 + (i % 3)), 'points': '10', 'status': 'Finished', 'grid': '5'}]
            }
            for i in range(1, 11)
        ],
        'Driver3': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': str(10 + (i % 5)), 'points': '1', 'status': 'Finished', 'grid': '10'}]
            }
            for i in range(1, 11)
        ]
    }
    
    driver_results = all_drivers_results['Driver1']
    
    result = calculate_analytics_percentile_rankings(
        driver_results,
        all_drivers_results,
        "2024"
    )
    
    # Property: Best driver should have highest percentile for avg_finish and points
    # With 3 drivers, 2 out of 3 are worse = 66.7th percentile
    expected_percentile = round((2 / 3) * 100, 1)
    
    assert result['avg_finish_percentile'] == expected_percentile, \
        f"Best driver should have {expected_percentile}th percentile for avg_finish, got {result['avg_finish_percentile']}"
    
    assert result['points_percentile'] == expected_percentile, \
        f"Best driver should have {expected_percentile}th percentile for points, got {result['points_percentile']}"
    
    # Property: Driver1 has perfect consistency (std_dev=0), which should be best
    # Driver1 should have highest consistency percentile
    assert result['consistency_percentile'] >= expected_percentile, \
        f"Best driver should have at least {expected_percentile}th percentile for consistency, got {result['consistency_percentile']}"


def test_property_percentile_rankings_worst_driver():
    """
    Feature: advanced-analytics, Property 16: Percentile Rankings
    
    A driver with the worst average finish, fewest points, and worst consistency
    should have 0th percentile for all metrics.
    
    **Validates: Requirements 14.1, 14.2, 14.3**
    """
    from app import calculate_analytics_percentile_rankings
    
    # Create a field where Driver3 is clearly the worst
    all_drivers_results = {
        'Driver1': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            }
            for i in range(1, 11)
        ],
        'Driver2': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '5', 'points': '10', 'status': 'Finished', 'grid': '5'}]
            }
            for i in range(1, 11)
        ],
        'Driver3': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '20', 'points': '0', 'status': 'Finished', 'grid': '20'}]
            }
            for i in range(1, 11)
        ]
    }
    
    driver_results = all_drivers_results['Driver3']
    
    result = calculate_analytics_percentile_rankings(
        driver_results,
        all_drivers_results,
        "2024"
    )
    
    # Property: Worst driver should have 0th percentile for all metrics
    # (0% of other drivers are worse)
    assert result['avg_finish_percentile'] == 0.0, \
        f"Worst driver should have 0th percentile for avg_finish, got {result['avg_finish_percentile']}"
    
    assert result['points_percentile'] == 0.0, \
        f"Worst driver should have 0th percentile for points, got {result['points_percentile']}"
    
    # Note: Consistency percentile might not be 0 if the worst driver is consistent
    # (consistently bad is still consistent), so we don't assert on consistency here


def test_property_percentile_rankings_empty_input():
    """
    Feature: advanced-analytics, Property 16: Percentile Rankings
    
    Empty input should return 0 for all percentiles and field_size.
    
    **Validates: Requirements 14.1, 14.2, 14.3, 14.4**
    """
    from app import calculate_analytics_percentile_rankings
    
    result = calculate_analytics_percentile_rankings(
        [],
        {},
        "2024"
    )
    
    # Property: Empty input should return zeros
    assert result['avg_finish_percentile'] == 0.0, \
        f"Empty input should have 0 for avg_finish_percentile, got {result['avg_finish_percentile']}"
    
    assert result['points_percentile'] == 0.0, \
        f"Empty input should have 0 for points_percentile, got {result['points_percentile']}"
    
    assert result['consistency_percentile'] == 0.0, \
        f"Empty input should have 0 for consistency_percentile, got {result['consistency_percentile']}"
    
    assert result['field_size'] == 0, \
        f"Empty input should have 0 for field_size, got {result['field_size']}"


def test_property_percentile_rankings_excludes_insufficient_races():
    """
    Feature: advanced-analytics, Property 16: Percentile Rankings
    
    Drivers who competed in fewer than 50% of season races should be excluded
    from the field when calculating percentiles.
    
    **Validates: Requirements 14.4**
    """
    from app import calculate_analytics_percentile_rankings
    
    # Create a field where some drivers have insufficient races
    all_drivers_results = {
        'Driver1': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            }
            for i in range(1, 11)  # 10 races
        ],
        'Driver2': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '5', 'points': '10', 'status': 'Finished', 'grid': '5'}]
            }
            for i in range(1, 11)  # 10 races
        ],
        'Driver3': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '10', 'points': '1', 'status': 'Finished', 'grid': '10'}]
            }
            for i in range(1, 4)  # Only 3 races (< 50% of 10)
        ]
    }
    
    driver_results = all_drivers_results['Driver1']
    
    result = calculate_analytics_percentile_rankings(
        driver_results,
        all_drivers_results,
        "2024"
    )
    
    # Property: field_size should only include drivers with >= 50% races
    # Driver1 and Driver2 have 10 races (>= 5), Driver3 has 3 races (< 5)
    assert result['field_size'] == 2, \
        f"field_size should be 2 (excluding Driver3 with insufficient races), got {result['field_size']}"


def test_property_percentile_rankings_middle_driver():
    """
    Feature: advanced-analytics, Property 16: Percentile Rankings
    
    A driver in the middle of the field should have percentiles around 50.
    
    **Validates: Requirements 14.1, 14.2, 14.3**
    """
    from app import calculate_analytics_percentile_rankings
    
    # Create a field with 5 drivers where Driver3 is in the middle
    all_drivers_results = {
        'Driver1': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '1', 'points': '25', 'status': 'Finished', 'grid': '1'}]
            }
            for i in range(1, 11)
        ],
        'Driver2': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '3', 'points': '15', 'status': 'Finished', 'grid': '3'}]
            }
            for i in range(1, 11)
        ],
        'Driver3': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '5', 'points': '10', 'status': 'Finished', 'grid': '5'}]
            }
            for i in range(1, 11)
        ],
        'Driver4': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '10', 'points': '1', 'status': 'Finished', 'grid': '10'}]
            }
            for i in range(1, 11)
        ],
        'Driver5': [
            {
                'raceName': f'Race {i}',
                'date': f'2024-03-{i:02d}',
                'round': str(i),
                'Results': [{'position': '15', 'points': '0', 'status': 'Finished', 'grid': '15'}]
            }
            for i in range(1, 11)
        ]
    }
    
    driver_results = all_drivers_results['Driver3']
    
    result = calculate_analytics_percentile_rankings(
        driver_results,
        all_drivers_results,
        "2024"
    )
    
    # Property: Middle driver should have percentiles around 40-60
    # Driver3 is better than Driver4 and Driver5 (2 out of 5 = 40%)
    assert 30 <= result['avg_finish_percentile'] <= 60, \
        f"Middle driver should have avg_finish_percentile around 40, got {result['avg_finish_percentile']}"
    
    assert 30 <= result['points_percentile'] <= 60, \
        f"Middle driver should have points_percentile around 40, got {result['points_percentile']}"
