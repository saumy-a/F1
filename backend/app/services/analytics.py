"""
Analytics calculation functions for F1 data.

This module contains 15 analytics calculation functions extracted from the Streamlit app.
All functions produce identical outputs to the original Streamlit implementation.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from app.utils.helpers import safe_int, safe_float, safe_divide, is_dnf, safe_correlation


def calculate_performance_trends(
    race_results: list,
    metric: str = "position"
) -> pd.DataFrame:
    """
    Calculate performance trends over time.
    
    Args:
        race_results: List of race result dicts from API
        metric: Which metric to track ("position" or "points")
    
    Returns:
        DataFrame with columns: race_name, race_date, round, metric_value
    """
    if not race_results:
        return pd.DataFrame(columns=['race_name', 'race_date', 'round', 'metric_value'])
    
    trends_data = []
    
    for race in race_results:
        race_name = race.get('raceName', 'Unknown')
        race_date = race.get('date', '')
        race_round = safe_int(race.get('round', 0))
        
        results = race.get('Results', [])
        if results:
            result = results[0]  # Driver's result in this race
            
            if metric == "position":
                # Get finishing position
                position = result.get('position', 'R')
                metric_value = safe_int(position, default=None)
            else:  # points
                # Get points scored
                points = result.get('points', '0')
                metric_value = safe_float(points, default=None)
                
            trends_data.append({
                'race_name': race_name,
                'race_date': race_date,
                'round': race_round,
                'metric_value': metric_value
            })
    
    return pd.DataFrame(trends_data)


def calculate_consistency_score(
    race_results: list,
    min_races: int = 5
) -> Optional[Dict[str, float]]:
    """
    Calculate consistency metrics for a driver.
    
    Args:
        race_results: List of race result dicts from API
        min_races: Minimum completed races required
    
    Returns:
        Dict with keys: consistency_score (0-100), std_dev, avg_position,
        completed_races, total_races, or None if insufficient data
    """
    if not race_results:
        return None
    
    # Extract finishing positions for completed races only
    positions = []
    total_races = len(race_results)
    
    for race in race_results:
        results = race.get('Results', [])
        if results:
            result = results[0]
            status = result.get('status', '')
            position = result.get('position', 'R')
            
            # Only include finished races (exclude DNFs)
            if not is_dnf(status) and position != 'R':
                pos_int = safe_int(position, default=None)
                if pos_int is not None and pos_int > 0:
                    positions.append(pos_int)
    
    completed_races = len(positions)
    
    # Check if we have enough data
    if completed_races < min_races:
        return None
    
    # Calculate statistics
    avg_position = np.mean(positions)
    std_dev = np.std(positions)
    
    # Calculate consistency score (0-100 scale)
    # Lower std_dev = higher consistency
    # Formula: 100 - (std_dev * 10), capped at 0
    consistency_score = max(0, 100 - (std_dev * 10))
    
    return {
        'consistency_score': round(consistency_score, 1),
        'std_dev': round(std_dev, 2),
        'avg_position': round(avg_position, 2),
        'completed_races': completed_races,
        'total_races': total_races
    }


def calculate_dnf_rate(
    race_results: list,
    time_period: str = "season"
) -> Dict[str, Any]:
    """
    Calculate DNF rate and categorization.
    
    Args:
        race_results: List of race result dicts from API
        time_period: Time period for calculation (currently unused, for future extension)
    
    Returns:
        Dict with keys: dnf_percentage, dnf_count, total_races,
        dnf_causes (dict of cause: count)
    """
    if not race_results:
        return {
            'dnf_percentage': 0.0,
            'dnf_count': 0,
            'total_races': 0,
            'dnf_causes': {}
        }
    
    total_races = len(race_results)
    dnf_count = 0
    dnf_causes = {}
    
    for race in race_results:
        results = race.get('Results', [])
        if results:
            result = results[0]
            status = result.get('status', 'Finished')
            
            if is_dnf(status):
                dnf_count += 1
                
                # Categorize DNF cause
                # Group similar causes together
                if status in ['Engine', 'Gearbox', 'Transmission', 'Clutch', 
                             'Hydraulics', 'Electrical', 'Mechanical', 'Brakes',
                             'Suspension', 'Fuel pressure', 'Overheating']:
                    cause = 'Mechanical'
                elif status in ['Accident', 'Collision', 'Spun off']:
                    cause = 'Accident'
                else:
                    cause = 'Other'
                
                dnf_causes[cause] = dnf_causes.get(cause, 0) + 1
    
    # Calculate percentage
    dnf_percentage = safe_divide(dnf_count * 100, total_races, default=0.0)
    
    return {
        'dnf_percentage': round(dnf_percentage, 1),
        'dnf_count': dnf_count,
        'total_races': total_races,
        'dnf_causes': dnf_causes
    }


def calculate_points_per_race(
    race_results: list,
    exclude_dnf: bool = False
) -> Dict[str, float]:
    """
    Calculate points per race averages.
    
    Args:
        race_results: List of race result dicts from API
        exclude_dnf: Whether to exclude DNF races from calculation
    
    Returns:
        Dict with keys: points_per_race, total_points, races_counted
    """
    if not race_results:
        return {
            'points_per_race': 0.0,
            'total_points': 0.0,
            'races_counted': 0
        }
    
    total_points = 0.0
    races_counted = 0
    
    for race in race_results:
        results = race.get('Results', [])
        if results:
            result = results[0]
            status = result.get('status', 'Finished')
            points = safe_float(result.get('points', '0'), default=0.0)
            
            # If excluding DNFs, skip DNF races
            if exclude_dnf and is_dnf(status):
                continue
            
            total_points += points
            races_counted += 1
    
    # Calculate points per race
    points_per_race = safe_divide(total_points, races_counted, default=0.0)
    
    return {
        'points_per_race': round(points_per_race, 2),
        'total_points': round(total_points, 1),
        'races_counted': races_counted
    }


def calculate_qualifying_race_correlation(
    race_results: list,
    min_races: int = 5
) -> Dict[str, Any]:
    """
    Calculate correlation between qualifying and race performance.
    
    Args:
        race_results: List of race result dicts from API
        min_races: Minimum races required for correlation
    
    Returns:
        Dict with keys: correlation_coefficient, avg_position_change,
        classification, scatter_data (list of {grid, finish} dicts),
        races_analyzed, missing_data_count, or None if insufficient data
    """
    if not race_results:
        return None
    
    # Extract grid and finish positions
    grid_positions = []
    finish_positions = []
    scatter_data = []
    missing_data_count = 0
    
    for race in race_results:
        results = race.get('Results', [])
        if results:
            result = results[0]
            grid = result.get('grid', None)
            position = result.get('position', None)
            status = result.get('status', 'Finished')
            
            # Track races with missing qualifying or race data
            if not grid or not position or is_dnf(status):
                if not grid or not position:
                    missing_data_count += 1
                continue
            
            # Only include races with valid grid and finish data
            grid_int = safe_int(grid, default=None)
            position_int = safe_int(position, default=None)
            
            if grid_int is not None and position_int is not None:
                grid_positions.append(grid_int)
                finish_positions.append(position_int)
                scatter_data.append({
                    'grid': grid_int,
                    'finish': position_int,
                    'race_name': race.get('raceName', 'Unknown')
                })
            else:
                missing_data_count += 1
    
    # Check if we have enough data
    if len(grid_positions) < min_races:
        return {
            'correlation_coefficient': None,
            'avg_position_change': 0.0,
            'classification': 'insufficient data',
            'scatter_data': scatter_data,
            'races_analyzed': len(grid_positions),
            'missing_data_count': missing_data_count,
            'insufficient_data': True
        }
    
    # Calculate correlation coefficient
    correlation = safe_correlation(grid_positions, finish_positions)
    
    # Calculate average position change (negative = gained positions)
    position_changes = [finish - grid for grid, finish in zip(grid_positions, finish_positions)]
    avg_position_change = sum(position_changes) / len(position_changes) if position_changes else 0.0
    
    # Classify driver performance based on correlation
    if correlation is None:
        classification = "insufficient data"
    elif correlation < -0.3:
        classification = "strong race performer"
    elif correlation > 0.7:
        classification = "qualifying-dependent performer"
    else:
        classification = "balanced performer"
    
    return {
        'correlation_coefficient': round(correlation, 3) if correlation is not None else None,
        'avg_position_change': round(avg_position_change, 2),
        'classification': classification,
        'scatter_data': scatter_data,
        'races_analyzed': len(grid_positions),
        'missing_data_count': missing_data_count,
        'insufficient_data': False
    }


def calculate_form_indicator(
    race_results: list,
    n_races: int = 5
) -> Dict[str, Any]:
    """
    Calculate recent form indicators.
    
    Args:
        race_results: List of race result dicts from API (most recent first)
        n_races: Number of recent races to analyze
    
    Returns:
        Dict with keys: avg_position, total_points, trend_direction,
        trend_slope, races_analyzed
    """
    if not race_results:
        return None
    
    # Take only the most recent n races
    recent_races = race_results[:n_races]
    
    positions = []
    total_points = 0.0
    races_analyzed = 0
    
    for race in recent_races:
        results = race.get('Results', [])
        if results:
            result = results[0]
            position = result.get('position', None)
            points = safe_float(result.get('points', '0'), default=0.0)
            status = result.get('status', 'Finished')
            
            # Only include finished races for position analysis
            if position and not is_dnf(status):
                position_int = safe_int(position, default=None)
                if position_int is not None:
                    positions.append(position_int)
                    total_points += points
                    races_analyzed += 1
    
    if not positions:
        return None
    
    # Calculate average position
    avg_position = sum(positions) / len(positions)
    
    # Calculate trend using linear regression
    # x = race index (0, 1, 2, ...), y = position
    # Negative slope = improving (lower positions over time)
    # Positive slope = declining (higher positions over time)
    if len(positions) >= 2:
        x = list(range(len(positions)))
        # Use numpy for linear regression
        slope, _ = np.polyfit(x, positions, 1)
        
        # Classify trend based on slope
        # Threshold of 0.3 positions per race
        if abs(slope) < 0.3:
            trend_direction = "stable"
        elif slope < 0:
            trend_direction = "improving"
        else:
            trend_direction = "declining"
    else:
        slope = 0.0
        trend_direction = "stable"
    
    return {
        'avg_position': round(avg_position, 2),
        'total_points': round(total_points, 1),
        'trend_direction': trend_direction,
        'trend_slope': round(slope, 3),
        'races_analyzed': races_analyzed
    }


def calculate_team_reliability(
    constructor_results: list,
    season: str
) -> Dict[str, Any]:
    """
    Calculate team reliability metrics.
    
    Args:
        constructor_results: List of constructor race results from API
        season: Season year for context
    
    Returns:
        Dict with keys: both_finished_pct, avg_finish_position,
        mechanical_dnf_rate, total_races
    """
    if not constructor_results:
        return {
            'both_finished_pct': 0.0,
            'avg_finish_position': 0.0,
            'mechanical_dnf_rate': 0.0,
            'total_races': 0
        }
    
    total_races = len(constructor_results)
    both_finished_count = 0
    total_positions = []
    mechanical_dnf_count = 0
    total_driver_entries = 0
    
    for race in constructor_results:
        results = race.get('Results', [])
        
        if not results:
            continue
        
        # Track finishes and positions for both drivers
        finished_count = 0
        race_positions = []
        
        for result in results:
            status = result.get('status', 'Finished')
            position = result.get('position', None)
            
            total_driver_entries += 1
            
            # Check if driver finished
            if not is_dnf(status):
                finished_count += 1
                # Add position to average calculation
                position_int = safe_int(position, default=None)
                if position_int is not None and position_int > 0:
                    race_positions.append(position_int)
            else:
                # Check if it's a mechanical DNF
                if status in ['Engine', 'Gearbox', 'Transmission', 'Clutch', 
                             'Hydraulics', 'Electrical', 'Mechanical', 'Brakes',
                             'Suspension', 'Fuel pressure', 'Overheating']:
                    mechanical_dnf_count += 1
        
        # Check if both drivers finished (assuming 2 drivers per team)
        if finished_count >= 2:
            both_finished_count += 1
        
        # Add all positions from this race
        total_positions.extend(race_positions)
    
    # Calculate metrics
    both_finished_pct = safe_divide(both_finished_count * 100, total_races, default=0.0)
    avg_finish_position = safe_divide(sum(total_positions), len(total_positions), default=0.0) if total_positions else 0.0
    mechanical_dnf_rate = safe_divide(mechanical_dnf_count * 100, total_driver_entries, default=0.0)
    
    return {
        'both_finished_pct': round(both_finished_pct, 1),
        'avg_finish_position': round(avg_finish_position, 2),
        'mechanical_dnf_rate': round(mechanical_dnf_rate, 1),
        'total_races': total_races
    }


def calculate_constructor_development(
    constructor_results: list,
    window_size: int = 3
) -> pd.DataFrame:
    """
    Calculate rolling development trends for a constructor.
    
    Args:
        constructor_results: List of constructor race results from API
        window_size: Rolling window size for averages
    
    Returns:
        DataFrame with columns: race_name, round, rolling_avg_points,
        rolling_avg_position, trend_classification
    """
    if not constructor_results:
        return pd.DataFrame(columns=['race_name', 'round', 'rolling_avg_points', 
                                    'rolling_avg_position', 'trend_classification'])
    
    # Extract race-by-race data
    race_data = []
    
    for race in constructor_results:
        race_name = race.get('raceName', 'Unknown')
        race_round = safe_int(race.get('round', 0))
        results = race.get('Results', [])
        
        # Calculate total points and average position for this race
        race_points = 0.0
        race_positions = []
        
        for result in results:
            points = safe_float(result.get('points', '0'), default=0.0)
            position = result.get('position', None)
            status = result.get('status', 'Finished')
            
            race_points += points
            
            # Only include finished positions in average
            if not is_dnf(status) and position:
                position_int = safe_int(position, default=None)
                if position_int is not None and position_int > 0:
                    race_positions.append(position_int)
        
        avg_position = safe_divide(sum(race_positions), len(race_positions), default=0.0) if race_positions else 0.0
        
        race_data.append({
            'race_name': race_name,
            'round': race_round,
            'points': race_points,
            'avg_position': avg_position
        })
    
    # Create DataFrame
    df = pd.DataFrame(race_data)
    
    if df.empty:
        return df
    
    # Calculate rolling averages
    df['rolling_avg_points'] = df['points'].rolling(window=window_size, min_periods=1).mean()
    df['rolling_avg_position'] = df['avg_position'].rolling(window=window_size, min_periods=1).mean()
    
    # Calculate overall trend classification using linear regression on rolling averages
    if len(df) >= window_size:
        # Use the rolling average points for trend analysis
        x = list(range(len(df)))
        y = df['rolling_avg_points'].values
        
        # Calculate slope
        slope, _ = np.polyfit(x, y, 1)
        
        # Classify trend (for points, positive slope = improving)
        if abs(slope) < 0.5:
            trend_classification = "stable"
        elif slope > 0:
            trend_classification = "improving"
        else:
            trend_classification = "declining"
    else:
        trend_classification = "insufficient data"
    
    # Add trend classification to all rows
    df['trend_classification'] = trend_classification
    
    return df


def calculate_driver_pairing(
    driver1_results: list,
    driver2_results: list,
    driver1_name: str,
    driver2_name: str
) -> Dict[str, Any]:
    """
    Calculate driver pairing effectiveness metrics.
    
    Args:
        driver1_results: Race results for first driver
        driver2_results: Race results for second driver
        driver1_name: Name of first driver
        driver2_name: Name of second driver
    
    Returns:
        Dict with keys: points_ratio, quali_gap, race_gap, balance_flag,
        driver1_points, driver2_points
    """
    # Calculate total points for each driver
    driver1_points = 0.0
    driver2_points = 0.0
    
    for race in driver1_results:
        results = race.get('Results', [])
        if results:
            points = safe_float(results[0].get('points', '0'), default=0.0)
            driver1_points += points
    
    for race in driver2_results:
        results = race.get('Results', [])
        if results:
            points = safe_float(results[0].get('points', '0'), default=0.0)
            driver2_points += points
    
    # Calculate points ratio
    total_points = driver1_points + driver2_points
    if total_points > 0:
        driver1_pct = (driver1_points / total_points) * 100
        driver2_pct = (driver2_points / total_points) * 100
        points_ratio = f"{driver1_pct:.1f}:{driver2_pct:.1f}"
        
        # Check if pairing is imbalanced (>70:30 ratio)
        if driver1_pct > 70 or driver2_pct > 70:
            balance_flag = "imbalanced"
        else:
            balance_flag = "balanced"
    else:
        points_ratio = "0.0:0.0"
        balance_flag = "no data"
    
    # Calculate average qualifying gap
    quali_gaps = []
    for race1, race2 in zip(driver1_results, driver2_results):
        results1 = race1.get('Results', [])
        results2 = race2.get('Results', [])
        
        if results1 and results2:
            grid1 = safe_int(results1[0].get('grid', None), default=None)
            grid2 = safe_int(results2[0].get('grid', None), default=None)
            
            if grid1 is not None and grid2 is not None:
                quali_gaps.append(abs(grid1 - grid2))
    
    avg_quali_gap = safe_divide(sum(quali_gaps), len(quali_gaps), default=0.0) if quali_gaps else 0.0
    
    # Calculate average race finishing gap
    race_gaps = []
    for race1, race2 in zip(driver1_results, driver2_results):
        results1 = race1.get('Results', [])
        results2 = race2.get('Results', [])
        
        if results1 and results2:
            status1 = results1[0].get('status', 'Finished')
            status2 = results2[0].get('status', 'Finished')
            
            # Only compare if both finished
            if not is_dnf(status1) and not is_dnf(status2):
                pos1 = safe_int(results1[0].get('position', None), default=None)
                pos2 = safe_int(results2[0].get('position', None), default=None)
                
                if pos1 is not None and pos2 is not None:
                    race_gaps.append(abs(pos1 - pos2))
    
    avg_race_gap = safe_divide(sum(race_gaps), len(race_gaps), default=0.0) if race_gaps else 0.0
    
    return {
        'points_ratio': points_ratio,
        'quali_gap': round(avg_quali_gap, 2),
        'race_gap': round(avg_race_gap, 2),
        'balance_flag': balance_flag,
        'driver1_points': round(driver1_points, 1),
        'driver2_points': round(driver2_points, 1),
        'driver1_name': driver1_name,
        'driver2_name': driver2_name
    }


def calculate_circuit_performance(
    driver_results: list,
    circuit_name: str,
    min_appearances: int = 3
) -> Dict[str, Any]:
    """
    Calculate driver performance at a specific circuit.
    
    Args:
        driver_results: All race results for driver (filtered to circuit)
        circuit_name: Name of the circuit
        min_appearances: Minimum races for reliable statistics
    
    Returns:
        Dict with keys: avg_finish, win_rate, podium_rate, points_rate,
        appearances, low_sample_warning
    """
    if not driver_results:
        return {
            'avg_finish': None,
            'win_rate': 0.0,
            'podium_rate': 0.0,
            'points_rate': 0.0,
            'appearances': 0,
            'low_sample_warning': True,
            'circuit_name': circuit_name
        }
    
    # Extract race results
    positions = []
    wins = 0
    podiums = 0
    points_finishes = 0
    total_races = len(driver_results)
    
    for race in driver_results:
        results = race.get('Results', [])
        if results:
            result = results[0]
            status = result.get('status', 'Finished')
            
            # Only count finished races for average position
            if not is_dnf(status):
                position = safe_int(result.get('position', None), default=None)
                if position is not None:
                    positions.append(position)
                    
                    # Count wins (position 1)
                    if position == 1:
                        wins += 1
                    
                    # Count podiums (positions 1-3)
                    if position <= 3:
                        podiums += 1
                    
                    # Count points finishes (positions 1-10 in modern F1)
                    if position <= 10:
                        points_finishes += 1
    
    # Calculate metrics
    avg_finish = safe_divide(sum(positions), len(positions), default=None) if positions else None
    win_rate = safe_divide(wins, total_races, default=0.0) * 100
    podium_rate = safe_divide(podiums, total_races, default=0.0) * 100
    points_rate = safe_divide(points_finishes, total_races, default=0.0) * 100
    
    # Check if sample size is too small
    low_sample_warning = total_races < min_appearances
    
    return {
        'avg_finish': round(avg_finish, 2) if avg_finish is not None else None,
        'win_rate': round(win_rate, 1),
        'podium_rate': round(podium_rate, 1),
        'points_rate': round(points_rate, 1),
        'appearances': total_races,
        'low_sample_warning': low_sample_warning,
        'circuit_name': circuit_name
    }


def calculate_circuit_difficulty(
    all_races_data: list,
    seasons: list
) -> pd.DataFrame:
    """
    Calculate difficulty ratings for all circuits.
    
    Args:
        all_races_data: Race results across multiple seasons
        seasons: List of season years included
    
    Returns:
        DataFrame with columns: circuit_name, dnf_rate, avg_position_change,
        difficulty_score (0-100), races_analyzed
    """
    if not all_races_data:
        return pd.DataFrame(columns=[
            'circuit_name', 'dnf_rate', 'avg_position_change',
            'difficulty_score', 'races_analyzed'
        ])
    
    # Group races by circuit
    circuit_data = {}
    
    for race in all_races_data:
        circuit_name = race.get('Circuit', {}).get('circuitName', 'Unknown')
        
        if circuit_name not in circuit_data:
            circuit_data[circuit_name] = {
                'total_entries': 0,
                'dnf_count': 0,
                'position_changes': [],
                'race_count': 0
            }
        
        circuit_data[circuit_name]['race_count'] += 1
        
        # Analyze results for this race
        results = race.get('Results', [])
        for result in results:
            circuit_data[circuit_name]['total_entries'] += 1
            
            status = result.get('status', 'Finished')
            if is_dnf(status):
                circuit_data[circuit_name]['dnf_count'] += 1
            
            # Calculate position change (grid to finish)
            grid = safe_int(result.get('grid', None), default=None)
            position = safe_int(result.get('position', None), default=None)
            
            if grid is not None and position is not None and not is_dnf(status):
                position_change = grid - position  # Positive = gained positions
                circuit_data[circuit_name]['position_changes'].append(abs(position_change))
    
    # Calculate metrics for each circuit
    circuit_metrics = []
    
    for circuit_name, data in circuit_data.items():
        # DNF rate
        dnf_rate = safe_divide(data['dnf_count'], data['total_entries'], default=0.0) * 100
        
        # Average position change (absolute value)
        avg_position_change = safe_divide(
            sum(data['position_changes']),
            len(data['position_changes']),
            default=0.0
        ) if data['position_changes'] else 0.0
        
        # Calculate difficulty score (0-100)
        # Formula: (dnf_rate * 0.6) + (abs(avg_pos_change) * 4.0)
        # Higher DNF rate and more position changes = higher difficulty
        raw_score = (dnf_rate * 0.6) + (avg_position_change * 4.0)
        difficulty_score = min(100, max(0, raw_score))
        
        circuit_metrics.append({
            'circuit_name': circuit_name,
            'dnf_rate': round(dnf_rate, 1),
            'avg_position_change': round(avg_position_change, 2),
            'difficulty_score': round(difficulty_score, 1),
            'races_analyzed': data['race_count']
        })
    
    # Create DataFrame and sort by difficulty score (descending)
    df = pd.DataFrame(circuit_metrics)
    df = df.sort_values('difficulty_score', ascending=False).reset_index(drop=True)
    
    return df


def calculate_multi_driver_comparison(
    drivers_data: Dict[str, list],
    metrics: list = None
) -> pd.DataFrame:
    """
    Compare multiple drivers across standardized metrics.
    
    Args:
        drivers_data: Dict mapping driver_name to race_results list
        metrics: List of metrics to compare (default: all)
    
    Returns:
        DataFrame with columns: driver_name, avg_finish, points_per_race,
        consistency_score, dnf_rate, [other metrics]
    """
    if not drivers_data:
        return pd.DataFrame()
    
    # Default metrics to calculate
    if metrics is None:
        metrics = ['avg_finish', 'points_per_race', 'consistency_score', 'dnf_rate']
    
    comparison_data = []
    
    for driver_name, race_results in drivers_data.items():
        if not race_results:
            continue
        
        driver_metrics = {'driver_name': driver_name}
        
        # Calculate average finish position (excluding DNFs)
        if 'avg_finish' in metrics:
            finished_races = []
            for race in race_results:
                results = race.get('Results', [])
                if results:
                    result = results[0]
                    status = result.get('status', 'Finished')
                    position = result.get('position', 'R')
                    
                    if not is_dnf(status):
                        pos_int = safe_int(position, default=None)
                        if pos_int is not None:
                            finished_races.append(pos_int)
            
            if finished_races:
                driver_metrics['avg_finish'] = round(sum(finished_races) / len(finished_races), 2)
            else:
                driver_metrics['avg_finish'] = None
        
        # Calculate points per race
        if 'points_per_race' in metrics:
            total_points = 0
            for race in race_results:
                results = race.get('Results', [])
                if results:
                    result = results[0]
                    total_points += safe_float(result.get('points', 0))
            
            races_count = len(race_results)
            driver_metrics['points_per_race'] = round(
                safe_divide(total_points, races_count, default=0.0), 2
            )
        
        # Calculate consistency score
        if 'consistency_score' in metrics:
            consistency = calculate_consistency_score(race_results, min_races=5)
            if consistency:
                driver_metrics['consistency_score'] = consistency['consistency_score']
            else:
                driver_metrics['consistency_score'] = None
        
        # Calculate DNF rate
        if 'dnf_rate' in metrics:
            dnf_data = calculate_dnf_rate(race_results)
            driver_metrics['dnf_rate'] = dnf_data['dnf_percentage']
        
        comparison_data.append(driver_metrics)
    
    return pd.DataFrame(comparison_data)


def calculate_season_comparison(
    entity_results_by_season: Dict[str, list],
    entity_type: str = "driver"
) -> pd.DataFrame:
    """
    Compare performance across multiple seasons.
    
    Args:
        entity_results_by_season: Dict mapping season to race_results list
        entity_type: Type of entity being compared ("driver" or "constructor")
    
    Returns:
        DataFrame with columns: season, avg_finish, total_points,
        points_per_race, consistency_score, yoy_change_pct
    """
    if not entity_results_by_season:
        return pd.DataFrame()
    
    season_data = []
    
    # Sort seasons chronologically
    sorted_seasons = sorted(entity_results_by_season.keys())
    
    for season in sorted_seasons:
        race_results = entity_results_by_season[season]
        
        if not race_results:
            continue
        
        season_metrics = {'season': season}
        
        # Calculate average finish position (excluding DNFs)
        finished_races = []
        for race in race_results:
            results = race.get('Results', [])
            if results:
                result = results[0]
                status = result.get('status', 'Finished')
                position = result.get('position', 'R')
                
                if not is_dnf(status):
                    pos_int = safe_int(position, default=None)
                    if pos_int is not None:
                        finished_races.append(pos_int)
        
        if finished_races:
            season_metrics['avg_finish'] = round(sum(finished_races) / len(finished_races), 2)
        else:
            season_metrics['avg_finish'] = None
        
        # Calculate total points
        total_points = 0
        for race in race_results:
            results = race.get('Results', [])
            if results:
                result = results[0]
                total_points += safe_float(result.get('points', 0))
        
        season_metrics['total_points'] = round(total_points, 1)
        
        # Calculate points per race
        races_count = len(race_results)
        season_metrics['points_per_race'] = round(
            safe_divide(total_points, races_count, default=0.0), 2
        )
        
        # Calculate consistency score
        consistency = calculate_consistency_score(race_results, min_races=5)
        if consistency:
            season_metrics['consistency_score'] = consistency['consistency_score']
        else:
            season_metrics['consistency_score'] = None
        
        season_data.append(season_metrics)
    
    # Create DataFrame
    df = pd.DataFrame(season_data)
    
    # Calculate year-over-year percentage change for points per race
    if len(df) > 1:
        yoy_changes = [None]  # First season has no previous year
        
        for i in range(1, len(df)):
            prev_ppr = df.iloc[i-1]['points_per_race']
            curr_ppr = df.iloc[i]['points_per_race']
            
            if prev_ppr > 0:
                yoy_change = ((curr_ppr - prev_ppr) / prev_ppr) * 100
                yoy_changes.append(round(yoy_change, 1))
            else:
                yoy_changes.append(None)
        
        df['yoy_change_pct'] = yoy_changes
    else:
        df['yoy_change_pct'] = None
    
    # Normalize points for different scoring systems
    # F1 scoring systems changed in 2010 (25 points for win)
    # Before 2010: 10 points for win
    # We'll normalize to the modern system (25 points for win)
    df['normalized_points_per_race'] = df.apply(
        lambda row: _normalize_points_for_season(
            row['points_per_race'],
            row['season']
        ),
        axis=1
    )
    
    return df


def _normalize_points_for_season(points_per_race: float, season: str) -> float:
    """
    Normalize points to modern scoring system (25 points for win).
    
    Args:
        points_per_race: Points per race in the original scoring system
        season: Season year
    
    Returns:
        Normalized points per race
    """
    try:
        season_year = int(season)
        
        # Pre-2010: 10 points for win, multiply by 2.5 to normalize
        if season_year < 2010:
            return round(points_per_race * 2.5, 2)
        
        # 2010 onwards: 25 points for win (modern system)
        return points_per_race
    except (ValueError, TypeError):
        return points_per_race


def calculate_percentile_rankings(
    driver_results: list,
    all_drivers_results: Dict[str, list],
    season: str
) -> Dict[str, float]:
    """
    Calculate percentile rankings for a driver within the field.
    
    Args:
        driver_results: Race results for target driver
        all_drivers_results: Dict mapping all driver names to their results
        season: Season year for context
    
    Returns:
        Dict with keys: avg_finish_percentile, points_percentile,
        consistency_percentile, field_size
    """
    if not driver_results or not all_drivers_results:
        return {
            'avg_finish_percentile': 0.0,
            'points_percentile': 0.0,
            'consistency_percentile': 0.0,
            'field_size': 0
        }
    
    # Filter drivers who competed in at least 50% of season races
    total_races = len(driver_results)
    min_races = max(1, total_races // 2)
    
    qualified_drivers = {
        name: results
        for name, results in all_drivers_results.items()
        if len(results) >= min_races
    }
    
    field_size = len(qualified_drivers)
    
    if field_size == 0:
        return {
            'avg_finish_percentile': 0.0,
            'points_percentile': 0.0,
            'consistency_percentile': 0.0,
            'field_size': 0
        }
    
    # Calculate metrics for all qualified drivers
    driver_metrics = {}
    
    for name, results in qualified_drivers.items():
        # Average finish position (excluding DNFs)
        finished_races = []
        for race in results:
            race_results = race.get('Results', [])
            if race_results:
                result = race_results[0]
                status = result.get('status', 'Finished')
                position = result.get('position', 'R')
                
                if not is_dnf(status):
                    pos_int = safe_int(position, default=None)
                    if pos_int is not None:
                        finished_races.append(pos_int)
        
        avg_finish = safe_divide(
            sum(finished_races),
            len(finished_races),
            default=999.0
        ) if finished_races else 999.0
        
        # Total points
        total_points = 0
        for race in results:
            race_results = race.get('Results', [])
            if race_results:
                result = race_results[0]
                total_points += safe_float(result.get('points', 0))
        
        # Consistency score
        consistency = calculate_consistency_score(results, min_races=5)
        consistency_score = consistency['consistency_score'] if consistency else 0.0
        
        driver_metrics[name] = {
            'avg_finish': avg_finish,
            'total_points': total_points,
            'consistency_score': consistency_score
        }
    
    # Find target driver's name
    target_driver_name = None
    for name in qualified_drivers.keys():
        if qualified_drivers[name] == driver_results:
            target_driver_name = name
            break
    
    # If we can't find the target driver by reference, use the first driver
    # with matching result count (fallback)
    if target_driver_name is None:
        for name, results in qualified_drivers.items():
            if len(results) == len(driver_results):
                target_driver_name = name
                break
    
    if target_driver_name is None or target_driver_name not in driver_metrics:
        return {
            'avg_finish_percentile': 0.0,
            'points_percentile': 0.0,
            'consistency_percentile': 0.0,
            'field_size': field_size
        }
    
    target_metrics = driver_metrics[target_driver_name]
    
    # Calculate percentiles
    # For avg_finish: lower is better, so we count how many drivers have worse (higher) avg
    avg_finish_values = [m['avg_finish'] for m in driver_metrics.values()]
    drivers_worse_finish = sum(1 for v in avg_finish_values if v > target_metrics['avg_finish'])
    avg_finish_percentile = (drivers_worse_finish / field_size) * 100
    
    # For points: higher is better, so we count how many drivers have fewer points
    points_values = [m['total_points'] for m in driver_metrics.values()]
    drivers_fewer_points = sum(1 for v in points_values if v < target_metrics['total_points'])
    points_percentile = (drivers_fewer_points / field_size) * 100
    
    # For consistency: higher is better, so we count how many drivers have lower consistency
    consistency_values = [m['consistency_score'] for m in driver_metrics.values()]
    drivers_less_consistent = sum(1 for v in consistency_values if v < target_metrics['consistency_score'])
    consistency_percentile = (drivers_less_consistent / field_size) * 100
    
    return {
        'avg_finish_percentile': round(avg_finish_percentile, 1),
        'points_percentile': round(points_percentile, 1),
        'consistency_percentile': round(consistency_percentile, 1),
        'field_size': field_size
    }


def calculate_championship_projection(
    current_standings: list,
    remaining_races: int,
    year: str
) -> Dict[str, Any]:
    """
    Calculate championship projection based on current standings and remaining races.
    
    Note: This function is a placeholder as it doesn't exist in the original Streamlit app.
    It provides a basic projection based on current points per race averages.
    
    Args:
        current_standings: Current driver standings
        remaining_races: Number of races remaining in season
        year: Season year
    
    Returns:
        Dict with projection data for top drivers
    """
    if not current_standings or remaining_races <= 0:
        return {
            'projections': [],
            'remaining_races': remaining_races,
            'max_points_available': 0
        }
    
    # Maximum points per race (25 for win + 1 for fastest lap)
    max_points_per_race = 26
    max_points_available = remaining_races * max_points_per_race
    
    projections = []
    
    for standing in current_standings[:10]:  # Top 10 drivers
        driver = standing.get('Driver', {})
        driver_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
        current_points = float(standing.get('points', 0))
        
        # Simple projection: current points + (average points per race * remaining races)
        # This is a basic linear projection
        races_completed = int(standing.get('position', 1))  # Approximate
        avg_points_per_race = safe_divide(current_points, races_completed, default=0.0)
        
        projected_points = current_points + (avg_points_per_race * remaining_races)
        max_possible_points = current_points + max_points_available
        
        projections.append({
            'driver_name': driver_name,
            'current_points': round(current_points, 1),
            'projected_points': round(projected_points, 1),
            'max_possible_points': round(max_possible_points, 1),
            'avg_points_per_race': round(avg_points_per_race, 2)
        })
    
    # Sort by projected points
    projections.sort(key=lambda x: x['projected_points'], reverse=True)
    
    return {
        'projections': projections,
        'remaining_races': remaining_races,
        'max_points_available': max_points_available
    }
