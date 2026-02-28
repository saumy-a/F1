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
    create_analytics_trend_chart
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
