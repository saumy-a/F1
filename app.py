"""
Formula 1 Dashboard - Main Application

A production-ready real-time Formula 1 dashboard application that provides
live F1 race data, driver standings, constructor standings, and race schedules.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from typing import Optional, Dict, Any
import time
import numpy as np
from scipy import stats


# ============================================================================
# DATA ACCESS LAYER
# ============================================================================

# API Configuration
# Using Jolpica F1 API (community-maintained Ergast replacement)
# Alternative: "http://ergast.com/api/f1" (deprecated as of 2024)
ERGAST_API_BASE_URL = "https://api.jolpi.ca/ergast/f1"
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


# ============================================================================
# ANALYTICS HELPER FUNCTIONS
# ============================================================================

def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int with DNF handling.
    
    Args:
        value: Value to convert (may be string, int, or DNF indicator)
        default: Default value to return if conversion fails
        
    Returns:
        Integer value or default if conversion fails
    """
    try:
        if value == 'R' or value == 'W':  # DNF indicators
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float.
    
    Args:
        value: Value to convert
        default: Default value to return if conversion fails
        
    Returns:
        Float value or default if conversion fails
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely perform division with zero-denominator handling.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value to return if denominator is zero
        
    Returns:
        Division result or default if denominator is zero
    """
    if denominator == 0:
        return default
    return numerator / denominator


def is_dnf(status: str) -> bool:
    """
    Check if race status indicates DNF (Did Not Finish).
    
    Args:
        status: Race status string from API
        
    Returns:
        True if status indicates DNF, False otherwise
    """
    dnf_statuses = [
        'Accident', 'Engine', 'Gearbox', 'Transmission', 'Clutch',
        'Hydraulics', 'Electrical', 'Collision', 'Spun off', 'Retired',
        'Mechanical', 'Brakes', 'Suspension', 'Fuel pressure', 'Overheating'
    ]
    return status in dnf_statuses or status.startswith('+')


def safe_correlation(x: list, y: list) -> Optional[float]:
    """
    Safely calculate Pearson correlation coefficient with variance checking.
    
    Args:
        x: First variable (list of numeric values)
        y: Second variable (list of numeric values)
        
    Returns:
        Correlation coefficient (-1 to 1) or None if calculation fails
    """
    if len(x) < 2 or len(y) < 2:
        return None
    
    if len(x) != len(y):
        return None
    
    # Check for sufficient variance
    if np.std(x) == 0 or np.std(y) == 0:
        st.warning("Cannot calculate correlation: one or both variables have zero variance.")
        return None
    
    try:
        correlation = np.corrcoef(x, y)[0, 1]
        return correlation
    except Exception:
        return None


# ============================================================================
# DATA ACCESS LAYER (continued)
# ============================================================================


def fetch_with_retry(url: str, max_retries: int = MAX_RETRIES, timeout: int = REQUEST_TIMEOUT) -> Optional[Dict[str, Any]]:
    """
    Fetch data from URL with retry logic and error handling.
    
    Args:
        url: The URL to fetch data from
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        
    Returns:
        JSON response as dictionary, or None if request fails
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raise exception for 4xx/5xx status codes
            return response.json()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
                continue
            else:
                st.error(f"⏱️ Request timed out after {max_retries} attempts. Please try again later.")
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code >= 500:
                # Server error - retry
                if attempt < max_retries - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                else:
                    st.error(f"🔴 Server error: Unable to fetch data from F1 API. Please try again later.")
                    return None
            else:
                # Client error (4xx) - don't retry
                st.error(f"⚠️ Data not available: {e.response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"🌐 Network error: Unable to connect to F1 API. Please check your internet connection.")
            return None
        except ValueError:
            # JSON decode error
            st.error(f"❌ Invalid data received from API. Please try again later.")
            return None
    
    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_latest_race(year: str = "current") -> Optional[Dict[str, Any]]:
    """
    Fetch the latest race results from Ergast F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023") or "current" for current season
    
    Returns:
        Dictionary containing race results, or None if request fails
    """
    url = f"{ERGAST_API_BASE_URL}/{year}/last/results.json"
    data = fetch_with_retry(url)
    
    if data and 'MRData' in data and 'RaceTable' in data['MRData']:
        races = data['MRData']['RaceTable'].get('Races', [])
        if races:
            return races[0]
    
    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_driver_standings(year: str = "current") -> Optional[list]:
    """
    Fetch driver championship standings from Ergast F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023") or "current" for current season
    
    Returns:
        List of driver standings, or None if request fails
    """
    url = f"{ERGAST_API_BASE_URL}/{year}/driverStandings.json"
    data = fetch_with_retry(url)
    
    if data and 'MRData' in data and 'StandingsTable' in data['MRData']:
        standings_lists = data['MRData']['StandingsTable'].get('StandingsLists', [])
        if standings_lists:
            return standings_lists[0].get('DriverStandings', [])
    
    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_constructor_standings(year: str = "current") -> Optional[list]:
    """
    Fetch constructor championship standings from Ergast F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023") or "current" for current season
    
    Returns:
        List of constructor standings, or None if request fails
    """
    url = f"{ERGAST_API_BASE_URL}/{year}/constructorStandings.json"
    data = fetch_with_retry(url)
    
    if data and 'MRData' in data and 'StandingsTable' in data['MRData']:
        standings_lists = data['MRData']['StandingsTable'].get('StandingsLists', [])
        if standings_lists:
            return standings_lists[0].get('ConstructorStandings', [])
    
    return None


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_next_race(year: str = "current") -> Optional[Dict[str, Any]]:
    """
    Fetch next scheduled race details from Ergast F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023") or "current" for current season
    
    Returns:
        Dictionary containing next race details, or None if no upcoming race or request fails
    """
    url = f"{ERGAST_API_BASE_URL}/{year}/next.json"
    data = fetch_with_retry(url)
    
    if data and 'MRData' in data and 'RaceTable' in data['MRData']:
        races = data['MRData']['RaceTable'].get('Races', [])
        if races:
            return races[0]
    
    return None


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_all_races(year: str = "current") -> Optional[list]:
    """
    Fetch all races for a given season from Ergast F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023") or "current" for current season
    
    Returns:
        List of all races in the season, or None if request fails
    """
    # Use a high limit to ensure we get all races (max ~25 races per season)
    url = f"{ERGAST_API_BASE_URL}/{year}/results.json?limit=1000"
    data = fetch_with_retry(url)
    
    if data and 'MRData' in data and 'RaceTable' in data['MRData']:
        races = data['MRData']['RaceTable'].get('Races', [])
        if races:
            return races
    
    return None


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_race_schedule(year: str = "current") -> Optional[list]:
    """
    Fetch the full race schedule for a given season from Ergast F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023") or "current" for current season
    
    Returns:
        List of all scheduled races in the season, or None if request fails
    """
    url = f"{ERGAST_API_BASE_URL}/{year}.json"
    data = fetch_with_retry(url)
    
    if data and 'MRData' in data and 'RaceTable' in data['MRData']:
        races = data['MRData']['RaceTable'].get('Races', [])
        if races:
            return races
    
    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_driver_standings_by_round(year: str = "current", round_num: int = None) -> Optional[list]:
    """
    Fetch driver standings after a specific round.
    
    Args:
        year: Season year (e.g., "2024", "2023") or "current" for current season
        round_num: Round number (1-based), or None for latest standings
    
    Returns:
        List of driver standings after the specified round, or None if request fails
    """
    if round_num is not None:
        url = f"{ERGAST_API_BASE_URL}/{year}/{round_num}/driverStandings.json"
    else:
        url = f"{ERGAST_API_BASE_URL}/{year}/driverStandings.json"
    
    data = fetch_with_retry(url)
    
    if data and 'MRData' in data and 'StandingsTable' in data['MRData']:
        standings_lists = data['MRData']['StandingsTable'].get('StandingsLists', [])
        if standings_lists:
            return standings_lists[0].get('DriverStandings', [])
    
    return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_driver_details(driver_id: str, year: str = "current") -> Optional[Dict[str, Any]]:
    """
    Fetch detailed information about a specific driver.

    Args:
        driver_id: Driver ID (e.g., "max_verstappen", "hamilton")
        year: Season year or "current"

    Returns:
        Dictionary containing driver details, or None if request fails
    """
    url = f"{ERGAST_API_BASE_URL}/{year}/drivers/{driver_id}.json"
    data = fetch_with_retry(url)

    if data and 'MRData' in data and 'DriverTable' in data['MRData']:
        drivers = data['MRData']['DriverTable'].get('Drivers', [])
        if drivers:
            return drivers[0]

    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_driver_race_results(driver_id: str, year: str = "current") -> Optional[list]:
    """
    Fetch all race results for a specific driver in a season.

    Args:
        driver_id: Driver ID (e.g., "max_verstappen", "hamilton")
        year: Season year or "current"

    Returns:
        List of race results, or None if request fails
    """
    url = f"{ERGAST_API_BASE_URL}/{year}/drivers/{driver_id}/results.json?limit=100"
    data = fetch_with_retry(url)

    if data and 'MRData' in data and 'RaceTable' in data['MRData']:
        races = data['MRData']['RaceTable'].get('Races', [])
        return races

    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_constructor_details(constructor_id: str, year: str = "current") -> Optional[Dict[str, Any]]:
    """
    Fetch detailed information about a specific constructor.

    Args:
        constructor_id: Constructor ID (e.g., "red_bull", "mercedes")
        year: Season year or "current"

    Returns:
        Dictionary containing constructor details, or None if request fails
    """
    url = f"{ERGAST_API_BASE_URL}/{year}/constructors/{constructor_id}.json"
    data = fetch_with_retry(url)

    if data and 'MRData' in data and 'ConstructorTable' in data['MRData']:
        constructors = data['MRData']['ConstructorTable'].get('Constructors', [])
        if constructors:
            return constructors[0]

    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_constructor_race_results(constructor_id: str, year: str = "current") -> Optional[list]:
    """
    Fetch all race results for a specific constructor in a season.

    Args:
        constructor_id: Constructor ID (e.g., "red_bull", "mercedes")
        year: Season year or "current"

    Returns:
        List of race results, or None if request fails
    """
    url = f"{ERGAST_API_BASE_URL}/{year}/constructors/{constructor_id}/results.json?limit=200"
    data = fetch_with_retry(url)

    if data and 'MRData' in data and 'RaceTable' in data['MRData']:
        races = data['MRData']['RaceTable'].get('Races', [])
        return races

    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_constructor_drivers(constructor_id: str, year: str = "current") -> Optional[list]:
    """
    Fetch all drivers for a specific constructor in a season.

    Args:
        constructor_id: Constructor ID (e.g., "red_bull", "mercedes")
        year: Season year or "current"

    Returns:
        List of drivers, or None if request fails
    """
    url = f"{ERGAST_API_BASE_URL}/{year}/constructors/{constructor_id}/drivers.json"
    data = fetch_with_retry(url)

    if data and 'MRData' in data and 'DriverTable' in data['MRData']:
        drivers = data['MRData']['DriverTable'].get('Drivers', [])
        return drivers

    return None



# ============================================================================
# DATA TRANSFORMATION LAYER
# ============================================================================

def format_driver_name(given_name: str, family_name: str) -> str:
    """
    Format driver name for display.
    
    Args:
        given_name: Driver's given name
        family_name: Driver's family name
        
    Returns:
        Formatted driver name as "Given Family"
    """
    return f"{given_name} {family_name}"


def parse_race_results(race_data: Optional[Dict[str, Any]]) -> Optional[pd.DataFrame]:
    """
    Parse race results into a pandas DataFrame.
    
    Args:
        race_data: Race data dictionary from Ergast API
        
    Returns:
        DataFrame with columns: position, driver, constructor, points
        Returns None if race_data is None or invalid
    """
    if not race_data or 'Results' not in race_data:
        return None
    
    results = []
    for result in race_data['Results']:
        try:
            driver = result.get('Driver', {})
            constructor = result.get('Constructor', {})
            
            results.append({
                'position': int(result.get('position', 0)),
                'driver': format_driver_name(
                    driver.get('givenName', ''),
                    driver.get('familyName', '')
                ),
                'constructor': constructor.get('name', 'Unknown'),
                'points': float(result.get('points', 0))
            })
        except (ValueError, KeyError, TypeError):
            # Skip invalid entries
            continue
    
    if not results:
        return None
    
    return pd.DataFrame(results)


def parse_driver_standings(standings_data: Optional[list]) -> Optional[pd.DataFrame]:
    """
    Parse driver standings into a pandas DataFrame.
    
    Args:
        standings_data: List of driver standings from Ergast API
        
    Returns:
        DataFrame with columns: position, driver, team, points, wins
        Returns None if standings_data is None or invalid
    """
    if not standings_data:
        return None
    
    standings = []
    for standing in standings_data:
        try:
            driver = standing.get('Driver', {})
            constructors = standing.get('Constructors', [])
            team = constructors[0].get('name', 'Unknown') if constructors else 'Unknown'
            
            standings.append({
                'position': int(standing.get('position', 0)),
                'driver': format_driver_name(
                    driver.get('givenName', ''),
                    driver.get('familyName', '')
                ),
                'team': team,
                'points': float(standing.get('points', 0)),
                'wins': int(standing.get('wins', 0))
            })
        except (ValueError, KeyError, TypeError):
            # Skip invalid entries
            continue
    
    if not standings:
        return None
    
    return pd.DataFrame(standings)


def parse_constructor_standings(standings_data: Optional[list]) -> Optional[pd.DataFrame]:
    """
    Parse constructor standings into a pandas DataFrame.
    
    Args:
        standings_data: List of constructor standings from Ergast API
        
    Returns:
        DataFrame with columns: position, constructor, points, wins
        Returns None if standings_data is None or invalid
    """
    if not standings_data:
        return None
    
    standings = []
    for standing in standings_data:
        try:
            constructor = standing.get('Constructor', {})
            
            standings.append({
                'position': int(standing.get('position', 0)),
                'constructor': constructor.get('name', 'Unknown'),
                'points': float(standing.get('points', 0)),
                'wins': int(standing.get('wins', 0))
            })
        except (ValueError, KeyError, TypeError):
            # Skip invalid entries
            continue
    
    if not standings:
        return None
    
    return pd.DataFrame(standings)


def extract_podium_finishers(race_data: Optional[Dict[str, Any]]) -> Optional[pd.DataFrame]:
    """
    Extract podium finishers (top 3) from race results.
    
    Args:
        race_data: Race data dictionary from Ergast API
        
    Returns:
        DataFrame with top 3 finishers, or None if race_data is None or invalid
    """
    df = parse_race_results(race_data)
    
    if df is None or df.empty:
        return None
    
    # Return top 3 finishers
    return df.head(3)


def build_championship_progression(year: str = "current") -> Optional[pd.DataFrame]:
    """
    Build championship progression data showing points accumulation over races.
    
    Args:
        year: Season year (e.g., "2024", "2023") or "current" for current season
        
    Returns:
        DataFrame with columns: round, race_name, driver, points
        Returns None if data cannot be fetched
    """
    # Fetch all races to get the number of completed races
    races = fetch_all_races(year)
    
    if not races:
        return None
    
    progression_data = []
    
    # For each completed race, fetch the standings after that round
    for race in races:
        round_num = int(race.get('round', 0))
        race_name = race.get('raceName', f'Round {round_num}')
        
        # Fetch standings after this round
        standings = fetch_driver_standings_by_round(year, round_num)
        
        if standings:
            for standing in standings:
                try:
                    driver = standing.get('Driver', {})
                    driver_name = format_driver_name(
                        driver.get('givenName', ''),
                        driver.get('familyName', '')
                    )
                    points = float(standing.get('points', 0))
                    
                    progression_data.append({
                        'round': round_num,
                        'race_name': race_name,
                        'driver': driver_name,
                        'points': points
                    })
                except (ValueError, KeyError, TypeError):
                    continue
    
    if not progression_data:
        return None
    
    return pd.DataFrame(progression_data)


def calculate_countdown(race_date: str, race_time: str = None) -> str:
    """
    Calculate countdown to a race.
    
    Args:
        race_date: Race date in YYYY-MM-DD format
        race_time: Race time in HH:MM:SS format (optional)
        
    Returns:
        Formatted countdown string (e.g., "5 days, 3 hours" or "Race completed")
    """
    from datetime import datetime, timezone
    
    try:
        # Parse race date and time
        if race_time:
            # Remove 'Z' if present and parse
            race_time_clean = race_time.replace('Z', '')
            race_datetime_str = f"{race_date} {race_time_clean}"
            race_datetime = datetime.strptime(race_datetime_str, "%Y-%m-%d %H:%M:%S")
            # Assume UTC timezone
            race_datetime = race_datetime.replace(tzinfo=timezone.utc)
        else:
            # If no time provided, assume end of day
            race_datetime = datetime.strptime(race_date, "%Y-%m-%d")
            race_datetime = race_datetime.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        
        # Get current time in UTC
        now = datetime.now(timezone.utc)
        
        # Calculate difference
        time_diff = race_datetime - now
        
        if time_diff.total_seconds() < 0:
            return "✅ Completed"
        
        # Calculate days, hours, minutes
        days = time_diff.days
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        
        if days > 0:
            return f"⏱️ {days}d {hours}h"
        elif hours > 0:
            return f"⏱️ {hours}h {minutes}m"
        else:
            return f"⏱️ {minutes}m"
            
    except (ValueError, TypeError):
        return "⏱️ TBA"

def get_driver_id_from_name(driver_name: str, standings_data: Optional[list]) -> Optional[str]:
    """
    Get driver ID from driver name using standings data.

    Args:
        driver_name: Full driver name (e.g., "Max Verstappen")
        standings_data: Driver standings data from API

    Returns:
        Driver ID string, or None if not found
    """
    if not standings_data:
        return None

    for standing in standings_data:
        driver = standing.get('Driver', {})
        full_name = format_driver_name(
            driver.get('givenName', ''),
            driver.get('familyName', '')
        )
        if full_name == driver_name:
            return driver.get('driverId')

    return None


def get_constructor_id_from_name(constructor_name: str, standings_data: Optional[list]) -> Optional[str]:
    """
    Get constructor ID from constructor name using standings data.

    Args:
        constructor_name: Constructor name (e.g., "Red Bull")
        standings_data: Constructor standings data from API

    Returns:
        Constructor ID string, or None if not found
    """
    if not standings_data:
        return None

    for standing in standings_data:
        constructor = standing.get('Constructor', {})
        if constructor.get('name') == constructor_name:
            return constructor.get('constructorId')

    return None


def calculate_driver_statistics(race_results: Optional[list]) -> Dict[str, Any]:
    """
    Calculate detailed statistics from driver race results.

    Args:
        race_results: List of race results from API

    Returns:
        Dictionary with statistics (races, wins, podiums, points, etc.)
    """
    if not race_results:
        return {
            'total_races': 0,
            'wins': 0,
            'podiums': 0,
            'total_points': 0,
            'avg_finish': 0,
            'dnf_count': 0,
            'pole_positions': 0,
            'fastest_laps': 0
        }

    total_races = 0
    wins = 0
    podiums = 0
    total_points = 0
    finish_positions = []
    dnf_count = 0
    pole_positions = 0
    fastest_laps = 0

    for race in race_results:
        results = race.get('Results', [])
        if results:
            result = results[0]  # Driver's result in this race
            total_races += 1

            # Count wins
            position = result.get('position')
            if position == '1':
                wins += 1

            # Count podiums
            if position in ['1', '2', '3']:
                podiums += 1

            # Sum points
            points = float(result.get('points', 0))
            total_points += points

            # Track finish positions for average
            try:
                pos_int = int(position)
                finish_positions.append(pos_int)
            except (ValueError, TypeError):
                # DNF or other status
                dnf_count += 1

            # Count pole positions
            grid = result.get('grid')
            if grid == '1':
                pole_positions += 1

            # Count fastest laps
            fastest_lap = result.get('FastestLap', {})
            if fastest_lap.get('rank') == '1':
                fastest_laps += 1

    # Calculate average finish position
    avg_finish = sum(finish_positions) / len(finish_positions) if finish_positions else 0

    return {
        'total_races': total_races,
        'wins': wins,
        'podiums': podiums,
        'total_points': total_points,
        'avg_finish': avg_finish,
        'dnf_count': dnf_count,
        'pole_positions': pole_positions,
        'fastest_laps': fastest_laps
    }


def calculate_constructor_statistics(race_results: Optional[list]) -> Dict[str, Any]:
    """
    Calculate detailed statistics from constructor race results.

    Args:
        race_results: List of race results from API

    Returns:
        Dictionary with statistics (races, wins, podiums, points, etc.)
    """
    if not race_results:
        return {
            'total_races': 0,
            'wins': 0,
            'podiums': 0,
            'total_points': 0,
            'one_two_finishes': 0,
            'dnf_count': 0
        }

    total_races = len(race_results)
    wins = 0
    podiums = 0
    total_points = 0
    one_two_finishes = 0
    dnf_count = 0

    for race in race_results:
        results = race.get('Results', [])

        # Track positions for this constructor in this race
        constructor_positions = []

        for result in results:
            # Sum points for all drivers
            points = float(result.get('points', 0))
            total_points += points

            # Track positions
            position = result.get('position')
            try:
                pos_int = int(position)
                constructor_positions.append(pos_int)

                # Count wins
                if pos_int == 1:
                    wins += 1

                # Count podiums
                if pos_int <= 3:
                    podiums += 1
            except (ValueError, TypeError):
                # DNF or other status
                dnf_count += 1

        # Check for 1-2 finish
        if len(constructor_positions) >= 2:
            sorted_positions = sorted(constructor_positions)
            if sorted_positions[0] == 1 and sorted_positions[1] == 2:
                one_two_finishes += 1

    return {
        'total_races': total_races,
        'wins': wins,
        'podiums': podiums,
        'total_points': total_points,
        'one_two_finishes': one_two_finishes,
        'dnf_count': dnf_count
    }


# ============================================================================
# ANALYTICS CALCULATION LAYER
# ============================================================================

@st.cache_data(ttl=3600)
def calculate_analytics_performance_trends(
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
                metric_value = safe_float(points, default=0.0)
            
            trends_data.append({
                'race_name': race_name,
                'race_date': race_date,
                'round': race_round,
                'metric_value': metric_value
            })
    
    return pd.DataFrame(trends_data)


@st.cache_data(ttl=3600)
def calculate_analytics_consistency_score(
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
        st.warning(f"Insufficient data: {completed_races} completed races found. "
                  f"Minimum {min_races} races required for consistency analysis.")
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


@st.cache_data(ttl=3600)
def calculate_analytics_dnf_rate(
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


@st.cache_data(ttl=3600)
def calculate_analytics_points_per_race(
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


@st.cache_data(ttl=3600)
def calculate_analytics_qualifying_race_correlation(
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


@st.cache_data(ttl=3600)
def calculate_analytics_form_indicator(
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
        import numpy as np
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


@st.cache_data(ttl=3600)
def calculate_analytics_team_reliability(
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


@st.cache_data(ttl=3600)
def calculate_analytics_constructor_development(
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


@st.cache_data(ttl=3600)
def calculate_analytics_driver_pairing(
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


@st.cache_data(ttl=3600)
def calculate_analytics_circuit_performance(
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


@st.cache_data(ttl=3600)
def calculate_analytics_circuit_difficulty(
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


@st.cache_data(ttl=3600)
def calculate_analytics_multi_driver_comparison(
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
            consistency = calculate_analytics_consistency_score(race_results, min_races=5)
            if consistency:
                driver_metrics['consistency_score'] = consistency['consistency_score']
            else:
                driver_metrics['consistency_score'] = None
        
        # Calculate DNF rate
        if 'dnf_rate' in metrics:
            dnf_data = calculate_analytics_dnf_rate(race_results)
            driver_metrics['dnf_rate'] = dnf_data['dnf_percentage']
        
        comparison_data.append(driver_metrics)
    
    return pd.DataFrame(comparison_data)


@st.cache_data(ttl=3600)
def calculate_analytics_season_comparison(
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
        consistency = calculate_analytics_consistency_score(race_results, min_races=5)
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


@st.cache_data(ttl=3600)
def calculate_analytics_percentile_rankings(
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
        consistency = calculate_analytics_consistency_score(results, min_races=5)
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


# ============================================================================
# UI HELPER FUNCTIONS
# ============================================================================

def create_horizontal_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str) -> Any:
    """
    Create a Plotly horizontal bar chart with F1-themed styling.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis (values)
        y_col: Column name for y-axis (labels)
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        orientation='h',
        title=title,
        labels={x_col: 'Points', y_col: ''},
        color=x_col,
        color_continuous_scale=['#E10600', '#FF1E00', '#FF4500', '#FF6B00']  # F1 red gradient
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font=dict(size=16, color='#E10600'),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif"
        )
    )
    
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Points: %{x}<extra></extra>',
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5
    )
    
    return fig


def create_championship_progression_chart(df: pd.DataFrame, selected_drivers: list = None) -> Any:
    """
    Create a Plotly line chart showing championship points progression over races.
    
    Args:
        df: DataFrame with columns: round, race_name, driver, points
        selected_drivers: List of driver names to display, or None for all drivers
        
    Returns:
        Plotly figure object
    """
    if df is None or df.empty:
        return None
    
    # Filter by selected drivers if specified
    if selected_drivers:
        df = df[df['driver'].isin(selected_drivers)].copy()
    
    if df.empty:
        return None
    
    # Create line chart
    fig = px.line(
        df,
        x='round',
        y='points',
        color='driver',
        title='Championship Points Progression',
        labels={'round': 'Race Round', 'points': 'Total Points', 'driver': 'Driver'},
        markers=True,
        hover_data={'race_name': True, 'round': True, 'points': True, 'driver': True}
    )
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font=dict(size=16, color='#E10600'),
        legend=dict(
            title="Drivers",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif"
        ),
        xaxis=dict(
            tickmode='linear',
            tick0=1,
            dtick=1,
            title='Race Round'
        ),
        yaxis=dict(
            title='Championship Points'
        )
    )
    
    fig.update_traces(
        hovertemplate='<b>%{customdata[3]}</b><br>' +
                      'Round %{customdata[1]}: %{customdata[0]}<br>' +
                      'Points: %{y}<extra></extra>',
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    return fig


# ============================================================================
# ANALYTICS VISUALIZATION LAYER
# ============================================================================

def create_analytics_trend_chart(
    trend_data: pd.DataFrame,
    metric_name: str,
    driver_name: str,
    team_color: str = None
) -> go.Figure:
    """
    Create line chart for performance trends.
    
    Args:
        trend_data: DataFrame with race_name, round, metric_value columns
        metric_name: Display name for the metric
        driver_name: Driver name for title
        team_color: Optional team color for line
    
    Returns:
        Plotly Figure object with interactive line chart
    """
    if trend_data.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Use team color if provided, otherwise use F1 red
    line_color = team_color if team_color else '#E10600'
    
    # Create the line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=trend_data['round'],
        y=trend_data['metric_value'],
        mode='lines+markers',
        name=driver_name,
        line=dict(color=line_color, width=3),
        marker=dict(size=8, color=line_color),
        customdata=trend_data[['race_name', 'race_date']].values,
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>' +
            'Date: %{customdata[1]}<br>' +
            f'{metric_name}: %{{y}}<br>' +
            '<extra></extra>'
        )
    ))
    
    # Update layout with F1 styling
    fig.update_layout(
        title=f"{driver_name} - {metric_name} Trend",
        xaxis_title="Race Round",
        yaxis_title=metric_name,
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font=dict(size=16, color='#E10600'),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif"
        ),
        xaxis=dict(
            tickmode='linear',
            tick0=1,
            dtick=1,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.2)'
        ),
        height=400
    )
    
    return fig


def create_analytics_scatter_chart(
    scatter_data: list,
    x_label: str,
    y_label: str,
    title: str,
    correlation: float = None
) -> go.Figure:
    """
    Create scatter plot with optional trend line.
    
    Args:
        scatter_data: List of dicts with 'grid' and 'finish' keys (or x/y keys)
        x_label: X-axis label
        y_label: Y-axis label
        title: Chart title
        correlation: Optional correlation coefficient for trend line
    
    Returns:
        Plotly Figure object with scatter plot
    """
    if not scatter_data:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Extract x and y values (handle both 'grid'/'finish' and 'x'/'y' keys)
    x_values = []
    y_values = []
    
    for point in scatter_data:
        if 'grid' in point and 'finish' in point:
            x_values.append(safe_int(point['grid']))
            y_values.append(safe_int(point['finish']))
        elif 'x' in point and 'y' in point:
            x_values.append(safe_float(point['x']))
            y_values.append(safe_float(point['y']))
    
    if not x_values or not y_values:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for scatter plot",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Create the scatter plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='markers',
        marker=dict(
            size=10,
            color='#E10600',
            opacity=0.6,
            line=dict(width=1, color='#8B0000')
        ),
        name='Data Points',
        hovertemplate=(
            f'{x_label}: %{{x}}<br>' +
            f'{y_label}: %{{y}}<br>' +
            '<extra></extra>'
        )
    ))
    
    # Add trend line if correlation is provided
    if correlation is not None and len(x_values) >= 2:
        # Calculate linear regression
        x_array = np.array(x_values)
        y_array = np.array(y_values)
        
        # Only add trend line if there's variance in both variables
        if np.std(x_array) > 0 and np.std(y_array) > 0:
            z = np.polyfit(x_array, y_array, 1)
            p = np.poly1d(z)
            
            # Create trend line points
            x_trend = np.linspace(min(x_values), max(x_values), 100)
            y_trend = p(x_trend)
            
            fig.add_trace(go.Scatter(
                x=x_trend,
                y=y_trend,
                mode='lines',
                line=dict(color='#FF6B00', width=2, dash='dash'),
                name=f'Trend Line (r={correlation:.2f})',
                hovertemplate='Trend Line<extra></extra>'
            ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font=dict(size=16, color='#E10600'),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif"
        ),
        xaxis=dict(
            gridcolor='rgba(128,128,128,0.2)',
            zeroline=False
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.2)',
            zeroline=False
        ),
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )
    
    # Add correlation annotation if provided
    if correlation is not None:
        fig.add_annotation(
            text=f"Correlation: {correlation:.3f}",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            font=dict(size=14, color='#E10600'),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#E10600',
            borderwidth=1,
            borderpad=4
        )
    
    return fig


def create_analytics_radar_chart(
    comparison_data: pd.DataFrame,
    metrics: list,
    entity_names: list
) -> go.Figure:
    """
    Create radar chart for multi-entity comparison.
    
    Args:
        comparison_data: DataFrame with entity names and metric columns
        metrics: List of metric names to display
        entity_names: List of entity names (drivers/teams)
    
    Returns:
        Plotly Figure object with radar chart
    """
    if comparison_data.empty or not metrics or not entity_names:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for comparison",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Create the radar chart
    fig = go.Figure()
    
    # Define colors for different entities
    colors = [
        '#E10600', '#FF6B00', '#00D2BE', '#0090FF', '#DC0000',
        '#006F62', '#2B4562', '#C92D4B', '#005AFF', '#F58020'
    ]
    
    # Add a trace for each entity
    for idx, entity_name in enumerate(entity_names):
        if entity_name not in comparison_data['driver_name'].values and \
           entity_name not in comparison_data['constructor_name'].values:
            continue
        
        # Get the row for this entity
        if 'driver_name' in comparison_data.columns:
            entity_row = comparison_data[comparison_data['driver_name'] == entity_name]
        else:
            entity_row = comparison_data[comparison_data['constructor_name'] == entity_name]
        
        if entity_row.empty:
            continue
        
        # Extract metric values
        values = []
        for metric in metrics:
            if metric in entity_row.columns:
                val = entity_row[metric].values[0]
                values.append(safe_float(val, 0.0))
            else:
                values.append(0.0)
        
        # Close the radar chart by repeating the first value
        values_closed = values + [values[0]]
        metrics_closed = metrics + [metrics[0]]
        
        # Add trace
        color = colors[idx % len(colors)]
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=metrics_closed,
            fill='toself',
            name=entity_name,
            line=dict(color=color, width=2),
            marker=dict(size=6, color=color),
            opacity=0.6,
            hovertemplate=(
                f'<b>{entity_name}</b><br>' +
                '%{theta}: %{r:.2f}<br>' +
                '<extra></extra>'
            )
        ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(128,128,128,0.2)'
            ),
            angularaxis=dict(
                gridcolor='rgba(128,128,128,0.2)'
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.1
        ),
        title="Multi-Entity Performance Comparison",
        title_font=dict(size=16, color='#E10600'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif"
        ),
        height=600
    )
    
    return fig


def create_analytics_grouped_bar_chart(
    comparison_data: pd.DataFrame,
    x_col: str,
    y_cols: list,
    title: str
) -> go.Figure:
    """
    Create grouped bar chart for metric comparison.
    
    Args:
        comparison_data: DataFrame with comparison data
        x_col: Column name for x-axis (categories)
        y_cols: List of column names for grouped bars
        title: Chart title
    
    Returns:
        Plotly Figure object with grouped bar chart
    """
    if comparison_data.empty or not y_cols:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for comparison",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Verify x_col exists
    if x_col not in comparison_data.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Column '{x_col}' not found in data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Create the grouped bar chart
    fig = go.Figure()
    
    # Define colors for different metrics
    colors = [
        '#E10600', '#FF6B00', '#00D2BE', '#0090FF', '#DC0000',
        '#006F62', '#2B4562', '#C92D4B', '#005AFF', '#F58020'
    ]
    
    # Add a bar trace for each metric
    for idx, y_col in enumerate(y_cols):
        if y_col not in comparison_data.columns:
            continue
        
        color = colors[idx % len(colors)]
        
        fig.add_trace(go.Bar(
            x=comparison_data[x_col],
            y=comparison_data[y_col],
            name=y_col,
            marker=dict(
                color=color,
                line=dict(color='rgba(0,0,0,0.2)', width=1)
            ),
            hovertemplate=(
                f'<b>%{{x}}</b><br>' +
                f'{y_col}: %{{y:.2f}}<br>' +
                '<extra></extra>'
            )
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title="Value",
        barmode='group',
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font=dict(size=16, color='#E10600'),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif"
        ),
        xaxis=dict(
            gridcolor='rgba(128,128,128,0.2)',
            tickangle=-45
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.2)'
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500
    )
    
    return fig


def create_analytics_horizontal_percentile_chart(
    percentile_data: Dict[str, float],
    driver_name: str
) -> go.Figure:
    """
    Create horizontal bar chart showing percentile rankings.
    
    Args:
        percentile_data: Dict mapping metric names to percentile values
        driver_name: Driver name for title
    
    Returns:
        Plotly Figure object with horizontal bar chart
    """
    if not percentile_data:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No percentile data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter out non-percentile fields (like 'field_size')
    metrics = []
    percentiles = []
    
    for metric, value in percentile_data.items():
        if metric != 'field_size' and isinstance(value, (int, float)):
            # Format metric name for display
            display_name = metric.replace('_percentile', '').replace('_', ' ').title()
            metrics.append(display_name)
            percentiles.append(value)
    
    if not metrics:
        fig = go.Figure()
        fig.add_annotation(
            text="No valid percentile metrics found",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Create color scale based on percentile value (higher is better)
    colors = []
    for p in percentiles:
        if p >= 75:
            colors.append('#00D400')  # Green for top quartile
        elif p >= 50:
            colors.append('#FFD700')  # Gold for above median
        elif p >= 25:
            colors.append('#FF8C00')  # Orange for below median
        else:
            colors.append('#E10600')  # Red for bottom quartile
    
    # Create the horizontal bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=percentiles,
        y=metrics,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.2)', width=1)
        ),
        text=[f"{p:.1f}%" for p in percentiles],
        textposition='outside',
        hovertemplate=(
            '<b>%{y}</b><br>' +
            'Percentile: %{x:.1f}%<br>' +
            '<extra></extra>'
        )
    ))
    
    # Add reference lines for quartiles
    for quartile, label in [(25, '25th'), (50, '50th (Median)'), (75, '75th')]:
        fig.add_vline(
            x=quartile,
            line_dash="dash",
            line_color="rgba(128,128,128,0.5)",
            line_width=1,
            annotation_text=label,
            annotation_position="top"
        )
    
    # Update layout
    fig.update_layout(
        title=f"{driver_name} - Percentile Rankings",
        xaxis_title="Percentile (%)",
        yaxis_title="Metric",
        hovermode='y unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font=dict(size=16, color='#E10600'),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif"
        ),
        xaxis=dict(
            range=[0, 105],  # Extend slightly beyond 100 for text labels
            gridcolor='rgba(128,128,128,0.2)',
            ticksuffix='%'
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.2)'
        ),
        showlegend=False,
        height=400
    )
    
    # Add field size annotation if available
    if 'field_size' in percentile_data:
        fig.add_annotation(
            text=f"Field Size: {percentile_data['field_size']} drivers",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            font=dict(size=12, color='#666666'),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(128,128,128,0.5)',
            borderwidth=1,
            borderpad=4
        )
    
    return fig


# ============================================================================
# PAGE RENDERING FUNCTIONS
# ============================================================================

def render_all_races_page(year: str = "current"):
    """Render all races for the selected season."""
    st.header("🏁 All Races")
    
    with st.spinner("Loading all races..."):
        races = fetch_all_races(year)
        
        if races:
            st.success(f"Found {len(races)} races in this season")
            
            # Create a DataFrame with all races
            race_list = []
            for race in races:
                circuit = race.get('Circuit', {})
                location = circuit.get('Location', {})
                
                # Get winner if results exist
                results = race.get('Results', [])
                winner = "N/A"
                winner_team = "N/A"
                if results:
                    winner_driver = results[0].get('Driver', {})
                    winner = format_driver_name(
                        winner_driver.get('givenName', ''),
                        winner_driver.get('familyName', '')
                    )
                    winner_constructor = results[0].get('Constructor', {})
                    winner_team = winner_constructor.get('name', 'N/A')
                
                race_list.append({
                    'Round': int(race.get('round', 0)),
                    'Race': race.get('raceName', 'Unknown'),
                    'Circuit': circuit.get('circuitName', 'Unknown'),
                    'Location': f"{location.get('locality', '')}, {location.get('country', '')}",
                    'Date': race.get('date', 'TBA'),
                    'Winner': winner,
                    'Team': winner_team
                })
            
            races_df = pd.DataFrame(race_list)
            
            # Display the table
            st.dataframe(
                races_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Round": st.column_config.NumberColumn("Round", format="%d"),
                    "Race": st.column_config.TextColumn("Race Name"),
                    "Circuit": st.column_config.TextColumn("Circuit"),
                    "Location": st.column_config.TextColumn("Location"),
                    "Date": st.column_config.DateColumn("Date"),
                    "Winner": st.column_config.TextColumn("Winner"),
                    "Team": st.column_config.TextColumn("Team")
                }
            )
            
            # Show race calendar visualization
            if not races_df.empty:
                st.divider()
                st.subheader("Race Calendar")
                
                # Create a simple bar chart showing races by month
                races_df['Month'] = pd.to_datetime(races_df['Date']).dt.strftime('%B')
                races_by_month = races_df.groupby('Month').size().reset_index(name='Count')
                
                fig = px.bar(
                    races_by_month,
                    x='Month',
                    y='Count',
                    title='Races by Month',
                    labels={'Count': 'Number of Races', 'Month': 'Month'},
                    color='Count',
                    color_continuous_scale=['#E10600', '#FF1E00', '#FF4500']
                )
                
                fig.update_layout(
                    showlegend=False,
                    height=300,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No race data available for this season.")


def render_race_calendar_page(year: str = "current"):
    """Render race calendar with countdown timers."""
    st.header("📅 Race Calendar")
    
    with st.spinner("Loading race schedule..."):
        races = fetch_race_schedule(year)
        
        if races:
            from datetime import datetime, timezone
            
            st.success(f"📊 {len(races)} races scheduled for this season")
            
            # Get current time for comparison
            now = datetime.now(timezone.utc)
            
            # Create a DataFrame with all races and countdown timers
            race_list = []
            for race in races:
                circuit = race.get('Circuit', {})
                location = circuit.get('Location', {})
                race_date = race.get('date', 'TBA')
                race_time = race.get('time', '')
                
                # Determine if race is upcoming or past
                try:
                    if race_time:
                        race_time_clean = race_time.replace('Z', '')
                        race_datetime_str = f"{race_date} {race_time_clean}"
                        race_datetime = datetime.strptime(race_datetime_str, "%Y-%m-%d %H:%M:%S")
                        race_datetime = race_datetime.replace(tzinfo=timezone.utc)
                    else:
                        race_datetime = datetime.strptime(race_date, "%Y-%m-%d")
                        race_datetime = race_datetime.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                    
                    is_upcoming = race_datetime > now
                except (ValueError, TypeError):
                    is_upcoming = True  # Default to upcoming if can't parse
                
                # Calculate countdown
                countdown = calculate_countdown(race_date, race_time)
                
                # Format date and time for display
                date_time_display = race_date
                if race_time:
                    date_time_display += f" {race_time[:5]} UTC"
                
                race_list.append({
                    'Round': int(race.get('round', 0)),
                    'Race': race.get('raceName', 'Unknown'),
                    'Circuit': circuit.get('circuitName', 'Unknown'),
                    'Location': f"{location.get('locality', '')}, {location.get('country', '')}",
                    'Date & Time': date_time_display,
                    'Countdown': countdown,
                    'Status': '🔜 Upcoming' if is_upcoming else '✅ Completed',
                    '_is_upcoming': is_upcoming  # Hidden column for filtering
                })
            
            races_df = pd.DataFrame(race_list)
            
            # Add filter options
            col1, col2 = st.columns([1, 3])
            with col1:
                filter_option = st.radio(
                    "Show races:",
                    options=["All Races", "Upcoming Only", "Completed Only"],
                    index=0,
                    horizontal=False
                )
            
            # Apply filter
            if filter_option == "Upcoming Only":
                display_df = races_df[races_df['_is_upcoming'] == True].copy()
            elif filter_option == "Completed Only":
                display_df = races_df[races_df['_is_upcoming'] == False].copy()
            else:
                display_df = races_df.copy()
            
            # Remove hidden column before display
            display_df = display_df.drop(columns=['_is_upcoming'])
            
            st.divider()
            
            # Display the table with styling
            if not display_df.empty:
                st.dataframe(
                    display_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "Round": st.column_config.NumberColumn("Round", format="%d", width="small"),
                        "Race": st.column_config.TextColumn("Race Name", width="medium"),
                        "Circuit": st.column_config.TextColumn("Circuit", width="medium"),
                        "Location": st.column_config.TextColumn("Location", width="medium"),
                        "Date & Time": st.column_config.TextColumn("Date & Time (UTC)", width="medium"),
                        "Countdown": st.column_config.TextColumn("Countdown", width="small"),
                        "Status": st.column_config.TextColumn("Status", width="small")
                    }
                )
                
                # Show summary metrics
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_races = len(races_df)
                    st.metric("Total Races", total_races)
                
                with col2:
                    upcoming_races = len(races_df[races_df['_is_upcoming'] == True])
                    st.metric("Upcoming Races", upcoming_races)
                
                with col3:
                    completed_races = len(races_df[races_df['_is_upcoming'] == False])
                    st.metric("Completed Races", completed_races)
                
                # Show next race highlight if there are upcoming races
                upcoming_df = races_df[races_df['_is_upcoming'] == True]
                if not upcoming_df.empty:
                    st.divider()
                    st.subheader("🏁 Next Race")
                    next_race = upcoming_df.iloc[0]
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Race", next_race['Race'])
                    with col2:
                        st.metric("Circuit", next_race['Circuit'])
                    with col3:
                        st.metric("Location", next_race['Location'])
                    with col4:
                        st.metric("Countdown", next_race['Countdown'])
                    
                    st.info(f"📍 {next_race['Date & Time']}")
            else:
                st.info("No races match the selected filter.")
        else:
            st.warning("⚠️ No race schedule available for this season.")



def render_overview_page(year: str = "current"):
    """Render the overview page with next race and latest results."""
    st.header("🏁 Race Overview")
    
    # Next Race Section
    st.subheader("Next Race" if year == "current" else f"Last Race of {year}")
    with st.spinner("Loading race information..."):
        next_race = fetch_next_race(year)
        
        if next_race:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Race",
                    value=next_race.get('raceName', 'Unknown')
                )
            
            with col2:
                circuit = next_race.get('Circuit', {})
                st.metric(
                    label="Circuit",
                    value=circuit.get('circuitName', 'Unknown')
                )
            
            with col3:
                race_date = next_race.get('date', 'TBA')
                race_time = next_race.get('time', '')
                date_time_str = f"{race_date}"
                if race_time:
                    date_time_str += f" {race_time[:5]}"
                st.metric(
                    label="Date & Time",
                    value=date_time_str
                )
            
            # Additional race details
            circuit = next_race.get('Circuit', {})
            location = circuit.get('Location', {})
            st.info(f"📍 {location.get('locality', '')}, {location.get('country', '')}")
        else:
            st.warning("⚠️ No upcoming race scheduled. Season may be complete or in off-season.")
    
    st.divider()
    
    # Latest Race Results Section
    st.subheader("Latest Race Results")
    with st.spinner("Loading latest race results..."):
        latest_race = fetch_latest_race(year)
        
        if latest_race:
            # Race winner
            st.markdown(f"**{latest_race.get('raceName', 'Unknown Race')}** - Round {latest_race.get('round', 'N/A')}")
            
            results_df = parse_race_results(latest_race)
            
            if results_df is not None and not results_df.empty:
                # Winner metrics
                winner = results_df.iloc[0]
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        label="🏆 Winner",
                        value=winner['driver']
                    )
                
                with col2:
                    st.metric(
                        label="Team",
                        value=winner['constructor']
                    )
                
                st.divider()
                
                # Podium table
                st.markdown("**🥇 Podium Finishers**")
                podium_df = extract_podium_finishers(latest_race)
                
                if podium_df is not None:
                    # Format the table for display
                    podium_display = podium_df.copy()
                    podium_display.columns = ['Position', 'Driver', 'Constructor', 'Points']
                    st.dataframe(
                        podium_display,
                        hide_index=True,
                        use_container_width=True
                    )
            else:
                st.warning("⚠️ No race results available.")
        else:
            st.warning("⚠️ Unable to load latest race results.")


def render_driver_standings_page(year: str = "current"):
    """Render driver standings with table and chart."""
    st.header("🏎️ Driver Championship Standings")
    
    # Check if we should show a driver profile
    if 'show_driver_profile' in st.session_state and st.session_state.show_driver_profile:
        driver_name = st.session_state.selected_driver_name
        
        # Back button
        if st.button("← Back to Standings"):
            st.session_state.show_driver_profile = False
            st.rerun()
        
        render_driver_profile_page(driver_name, year)
        return
    
    with st.spinner("Loading driver standings..."):
        standings_data = fetch_driver_standings(year)
        standings_df = parse_driver_standings(standings_data)
        
        if standings_df is not None and not standings_df.empty:
            # Team Filter Dropdown
            teams = ["All Teams"] + sorted(standings_df['team'].unique().tolist())
            selected_team = st.selectbox(
                "Filter by Team",
                options=teams,
                key="team_filter"
            )
            
            # Apply team filter
            if selected_team != "All Teams":
                filtered_df = standings_df[standings_df['team'] == selected_team].copy()
            else:
                filtered_df = standings_df.copy()
            
            st.divider()
            
            # Top 10 Drivers Chart
            st.subheader("Top 10 Drivers - Points Comparison")
            top_10 = filtered_df.head(10).copy()
            
            fig = create_horizontal_bar_chart(
                top_10,
                x_col='points',
                y_col='driver',
                title='Top 10 Drivers by Points'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Championship Progression Chart (Bonus Feature)
            st.subheader("📈 Championship Points Progression")
            
            with st.spinner("Loading championship progression data..."):
                progression_df = build_championship_progression(year)
                
                if progression_df is not None and not progression_df.empty:
                    # Multi-select for drivers
                    all_drivers = sorted(progression_df['driver'].unique().tolist())
                    
                    # Default to top 5 drivers from current standings
                    default_drivers = filtered_df.head(5)['driver'].tolist()
                    # Ensure default drivers are in the progression data
                    default_drivers = [d for d in default_drivers if d in all_drivers]
                    
                    selected_drivers = st.multiselect(
                        "Select drivers to display (default: top 5)",
                        options=all_drivers,
                        default=default_drivers,
                        key="progression_drivers"
                    )
                    
                    if selected_drivers:
                        progression_chart = create_championship_progression_chart(
                            progression_df,
                            selected_drivers=selected_drivers
                        )
                        
                        if progression_chart:
                            st.plotly_chart(progression_chart, use_container_width=True)
                            
                            # Show some insights
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                total_rounds = progression_df['round'].max()
                                st.metric("Total Races", total_rounds)
                            
                            with col2:
                                # Find driver with most points gained in last 5 races
                                if total_rounds >= 5:
                                    recent_rounds = progression_df[progression_df['round'] >= total_rounds - 4]
                                    for driver in selected_drivers:
                                        driver_recent = recent_rounds[recent_rounds['driver'] == driver]
                                        if len(driver_recent) >= 2:
                                            points_gained = driver_recent['points'].iloc[-1] - driver_recent['points'].iloc[0]
                                            st.metric(f"{driver} (Last 5 races)", f"+{points_gained:.0f} pts")
                                            break
                            
                            with col3:
                                # Show leader's current points
                                leader = filtered_df.iloc[0]
                                st.metric("Championship Leader", f"{leader['driver']}: {leader['points']:.0f} pts")
                        else:
                            st.info("No data available for selected drivers.")
                    else:
                        st.info("Please select at least one driver to view progression.")
                else:
                    st.info("Championship progression data not available for this season yet.")
            
            st.divider()
            
            # Full Standings Table
            st.subheader("Full Driver Standings")
            display_df = filtered_df.copy()
            display_df.columns = ['Position', 'Driver', 'Team', 'Points', 'Wins']
            
            # Add a column for profile links
            st.write("Click on a driver name to view their detailed profile:")
            
            # Create clickable driver names using buttons in columns
            for idx, row in display_df.iterrows():
                col_pos, col_driver, col_team, col_points, col_wins = st.columns([1, 3, 3, 2, 1])
                
                with col_pos:
                    st.write(f"**{row['Position']}**")
                
                with col_driver:
                    if st.button(f"🏎️ {row['Driver']}", key=f"driver_{idx}"):
                        st.session_state.show_driver_profile = True
                        st.session_state.selected_driver_name = row['Driver']
                        st.rerun()
                
                with col_team:
                    st.write(row['Team'])
                
                with col_points:
                    st.write(f"{row['Points']:.0f}")
                
                with col_wins:
                    st.write(row['Wins'])
            
            st.divider()
            
            # Driver Comparison
            st.subheader("Compare Drivers")
            col1, col2 = st.columns(2)
            
            driver_names = filtered_df['driver'].tolist()
            
            with col1:
                driver1 = st.selectbox(
                    "Select First Driver",
                    options=driver_names,
                    key="driver1"
                )
            
            with col2:
                driver2 = st.selectbox(
                    "Select Second Driver",
                    options=driver_names,
                    index=min(1, len(driver_names) - 1),
                    key="driver2"
                )
            
            # Display comparison
            if driver1 and driver2:
                driver1_data = filtered_df[filtered_df['driver'] == driver1].iloc[0]
                driver2_data = filtered_df[filtered_df['driver'] == driver2].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"### {driver1}")
                    st.metric("Points", f"{driver1_data['points']:.0f}")
                    st.metric("Wins", f"{driver1_data['wins']}")
                    st.metric("Position", f"{driver1_data['position']}")
                
                with col2:
                    st.markdown(f"### {driver2}")
                    st.metric("Points", f"{driver2_data['points']:.0f}")
                    st.metric("Wins", f"{driver2_data['wins']}")
                    st.metric("Position", f"{driver2_data['position']}")
        else:
            st.warning("⚠️ Unable to load driver standings.")


def render_constructor_standings_page(year: str = "current"):
    """Render constructor standings with table and chart."""
    st.header("🏁 Constructor Championship Standings")
    
    # Check if we should show a constructor profile
    if 'show_constructor_profile' in st.session_state and st.session_state.show_constructor_profile:
        constructor_name = st.session_state.selected_constructor_name
        
        # Back button
        if st.button("← Back to Standings"):
            st.session_state.show_constructor_profile = False
            st.rerun()
        
        render_constructor_profile_page(constructor_name, year)
        return
    
    with st.spinner("Loading constructor standings..."):
        standings_data = fetch_constructor_standings(year)
        standings_df = parse_constructor_standings(standings_data)
        
        if standings_df is not None and not standings_df.empty:
            # Constructor Points Chart
            st.subheader("Constructor Points Comparison")
            
            fig = create_horizontal_bar_chart(
                standings_df,
                x_col='points',
                y_col='constructor',
                title='Constructor Championship Points'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Full Constructor Standings Table
            st.subheader("Full Constructor Standings")
            display_df = standings_df.copy()
            display_df.columns = ['Position', 'Constructor', 'Points', 'Wins']
            
            # Add a column for profile links
            st.write("Click on a team name to view their detailed profile:")
            
            # Create clickable constructor names using buttons in columns
            for idx, row in display_df.iterrows():
                col_pos, col_constructor, col_points, col_wins = st.columns([1, 4, 2, 1])
                
                with col_pos:
                    st.write(f"**{row['Position']}**")
                
                with col_constructor:
                    if st.button(f"🏁 {row['Constructor']}", key=f"constructor_{idx}"):
                        st.session_state.show_constructor_profile = True
                        st.session_state.selected_constructor_name = row['Constructor']
                        st.rerun()
                
                with col_points:
                    st.write(f"{row['Points']:.0f}")
                
                with col_wins:
                    st.write(row['Wins'])
        else:
            st.warning("⚠️ Unable to load constructor standings.")

def render_driver_profile_page(driver_name: str, year: str = "current"):
    """Render detailed driver profile page with statistics."""
    st.header(f"🏎️ Driver Profile: {driver_name}")

    # Get driver ID from standings
    with st.spinner("Loading driver profile..."):
        standings_data = fetch_driver_standings(year)
        driver_id = get_driver_id_from_name(driver_name, standings_data)

        if not driver_id:
            st.error("❌ Unable to find driver information.")
            return

        # Fetch driver details
        driver_details = fetch_driver_details(driver_id, year)
        race_results = fetch_driver_race_results(driver_id, year)

        if not driver_details:
            st.error("❌ Unable to load driver details.")
            return

        # Display driver information
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            st.subheader("Driver Info")
            st.write(f"**Name:** {driver_details.get('givenName')} {driver_details.get('familyName')}")
            st.write(f"**Number:** {driver_details.get('permanentNumber', 'N/A')}")
            st.write(f"**Nationality:** {driver_details.get('nationality', 'Unknown')}")

            # Date of birth
            dob = driver_details.get('dateOfBirth', 'Unknown')
            st.write(f"**Date of Birth:** {dob}")

            # Wikipedia link
            wiki_url = driver_details.get('url')
            if wiki_url:
                st.markdown(f"[📖 Wikipedia]({wiki_url})")

        with col2:
            # Calculate statistics
            stats = calculate_driver_statistics(race_results)

            st.subheader(f"{year if year != 'current' else 'Current'} Season Statistics")

            # Display key metrics in columns
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.metric("Races", stats['total_races'])
                st.metric("Wins", stats['wins'])

            with metric_col2:
                st.metric("Podiums", stats['podiums'])
                st.metric("Points", f"{stats['total_points']:.0f}")

            with metric_col3:
                st.metric("Poles", stats['pole_positions'])
                st.metric("Fastest Laps", stats['fastest_laps'])

            with metric_col4:
                st.metric("DNFs", stats['dnf_count'])
                if stats['avg_finish'] > 0:
                    st.metric("Avg Finish", f"{stats['avg_finish']:.1f}")

        with col3:
            # Current standing
            if standings_data:
                standings_df = parse_driver_standings(standings_data)
                if standings_df is not None:
                    driver_standing = standings_df[standings_df['driver'] == driver_name]
                    if not driver_standing.empty:
                        st.subheader("Championship")
                        st.metric("Position", f"P{driver_standing.iloc[0]['position']}")
                        st.metric("Points", f"{driver_standing.iloc[0]['points']:.0f}")
                        st.metric("Wins", driver_standing.iloc[0]['wins'])

        st.divider()

        # Race results table
        if race_results:
            st.subheader("Race Results")

            race_data = []
            for race in race_results:
                results = race.get('Results', [])
                if results:
                    result = results[0]
                    race_data.append({
                        'Round': int(race.get('round', 0)),
                        'Race': race.get('raceName', 'Unknown'),
                        'Position': result.get('position', 'DNF'),
                        'Grid': result.get('grid', 'N/A'),
                        'Points': float(result.get('points', 0)),
                        'Status': result.get('status', 'Unknown')
                    })

            if race_data:
                race_df = pd.DataFrame(race_data)
                st.dataframe(
                    race_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "Round": st.column_config.NumberColumn("Round", format="%d"),
                        "Race": st.column_config.TextColumn("Race"),
                        "Position": st.column_config.TextColumn("Finish"),
                        "Grid": st.column_config.TextColumn("Grid"),
                        "Points": st.column_config.NumberColumn("Points", format="%.1f"),
                        "Status": st.column_config.TextColumn("Status")
                    }
                )

                # Visualizations
                st.divider()
                st.subheader("Performance Analysis")

                # Points per race chart
                fig = px.bar(
                    race_df,
                    x='Round',
                    y='Points',
                    title='Points Scored Per Race',
                    labels={'Round': 'Race Round', 'Points': 'Points'},
                    color='Points',
                    color_continuous_scale=['#E10600', '#FF1E00', '#FF4500']
                )

                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)

                # Finishing positions chart
                # Filter out DNFs for position chart
                finished_races = race_df[race_df['Position'].str.isnumeric()].copy()
                if not finished_races.empty:
                    finished_races['Position'] = finished_races['Position'].astype(int)

                    fig2 = px.line(
                        finished_races,
                        x='Round',
                        y='Position',
                        title='Finishing Positions Throughout Season',
                        labels={'Round': 'Race Round', 'Position': 'Finish Position'},
                        markers=True
                    )

                    fig2.update_layout(
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        yaxis=dict(autorange='reversed')  # Lower position number is better
                    )

                    st.plotly_chart(fig2, use_container_width=True)


def render_constructor_profile_page(constructor_name: str, year: str = "current"):
    """Render detailed constructor profile page with statistics."""
    st.header(f"🏁 Team Profile: {constructor_name}")

    # Get constructor ID from standings
    with st.spinner("Loading team profile..."):
        standings_data = fetch_constructor_standings(year)
        constructor_id = get_constructor_id_from_name(constructor_name, standings_data)

        if not constructor_id:
            st.error("❌ Unable to find team information.")
            return

        # Fetch constructor details
        constructor_details = fetch_constructor_details(constructor_id, year)
        race_results = fetch_constructor_race_results(constructor_id, year)
        drivers = fetch_constructor_drivers(constructor_id, year)

        if not constructor_details:
            st.error("❌ Unable to load team details.")
            return

        # Display constructor information
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            st.subheader("Team Info")
            st.write(f"**Name:** {constructor_details.get('name')}")
            st.write(f"**Nationality:** {constructor_details.get('nationality', 'Unknown')}")

            # Wikipedia link
            wiki_url = constructor_details.get('url')
            if wiki_url:
                st.markdown(f"[📖 Wikipedia]({wiki_url})")

            # Display drivers
            if drivers:
                st.write("**Drivers:**")
                for driver in drivers:
                    driver_name = format_driver_name(
                        driver.get('givenName', ''),
                        driver.get('familyName', '')
                    )
                    st.write(f"• {driver_name}")

        with col2:
            # Calculate statistics
            stats = calculate_constructor_statistics(race_results)

            st.subheader(f"{year if year != 'current' else 'Current'} Season Statistics")

            # Display key metrics in columns
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            with metric_col1:
                st.metric("Races", stats['total_races'])
                st.metric("Wins", stats['wins'])

            with metric_col2:
                st.metric("Podiums", stats['podiums'])
                st.metric("Points", f"{stats['total_points']:.0f}")

            with metric_col3:
                st.metric("1-2 Finishes", stats['one_two_finishes'])
                st.metric("DNFs", stats['dnf_count'])

        with col3:
            # Current standing
            if standings_data:
                standings_df = parse_constructor_standings(standings_data)
                if standings_df is not None:
                    constructor_standing = standings_df[standings_df['constructor'] == constructor_name]
                    if not constructor_standing.empty:
                        st.subheader("Championship")
                        st.metric("Position", f"P{constructor_standing.iloc[0]['position']}")
                        st.metric("Points", f"{constructor_standing.iloc[0]['points']:.0f}")
                        st.metric("Wins", constructor_standing.iloc[0]['wins'])

        st.divider()

        # Race results table
        if race_results:
            st.subheader("Race Results")

            race_data = []
            for race in race_results:
                results = race.get('Results', [])

                # Aggregate results for all drivers in this race
                race_points = 0
                best_position = None
                driver_results = []

                for result in results:
                    points = float(result.get('points', 0))
                    race_points += points

                    position = result.get('position')
                    try:
                        pos_int = int(position)
                        if best_position is None or pos_int < best_position:
                            best_position = pos_int
                    except (ValueError, TypeError):
                        pass

                    driver = result.get('Driver', {})
                    driver_name = format_driver_name(
                        driver.get('givenName', ''),
                        driver.get('familyName', '')
                    )
                    driver_results.append(f"{driver_name} (P{position})")

                race_data.append({
                    'Round': int(race.get('round', 0)),
                    'Race': race.get('raceName', 'Unknown'),
                    'Best Finish': f"P{best_position}" if best_position else 'N/A',
                    'Points': race_points,
                    'Drivers': ', '.join(driver_results)
                })

            if race_data:
                race_df = pd.DataFrame(race_data)
                st.dataframe(
                    race_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "Round": st.column_config.NumberColumn("Round", format="%d"),
                        "Race": st.column_config.TextColumn("Race"),
                        "Best Finish": st.column_config.TextColumn("Best Finish"),
                        "Points": st.column_config.NumberColumn("Points", format="%.1f"),
                        "Drivers": st.column_config.TextColumn("Driver Results")
                    }
                )

                # Visualizations
                st.divider()
                st.subheader("Performance Analysis")

                # Points per race chart
                fig = px.bar(
                    race_df,
                    x='Round',
                    y='Points',
                    title='Points Scored Per Race',
                    labels={'Round': 'Race Round', 'Points': 'Points'},
                    color='Points',
                    color_continuous_scale=['#E10600', '#FF1E00', '#FF4500']
                )

                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)



# ============================================================================
# ANALYTICS PAGE RENDERING
# ============================================================================

def render_analytics_main_page(year: str = "current"):
    """
    Main analytics page with subsection navigation.
    
    Displays:
    - Subsection selector (tabs)
    - Conditional rendering of selected subsection
    
    Args:
        year: Season year to analyze
    """
    st.header("📊 Advanced Analytics")
    st.markdown("Deep dive into F1 performance data with advanced statistical analysis")
    
    # Initialize session state for preserving user selections
    if 'analytics_driver' not in st.session_state:
        st.session_state.analytics_driver = None
    if 'analytics_team' not in st.session_state:
        st.session_state.analytics_team = None
    if 'analytics_circuit' not in st.session_state:
        st.session_state.analytics_circuit = None
    if 'analytics_season' not in st.session_state:
        st.session_state.analytics_season = year
    
    # Create subsection tabs
    analytics_tabs = st.tabs([
        "🏎️ Driver Analytics",
        "🏗️ Team Analytics", 
        "🏁 Circuit Analytics",
        "⚔️ Comparative Analytics",
        "📈 Statistical Insights"
    ])
    
    with analytics_tabs[0]:
        render_analytics_driver_subsection(year)
    
    with analytics_tabs[1]:
        render_analytics_team_subsection(year)
    
    with analytics_tabs[2]:
        render_analytics_circuit_subsection(year)
    
    with analytics_tabs[3]:
        render_analytics_comparative_subsection(year)
    
    with analytics_tabs[4]:
        render_analytics_statistical_subsection(year)


def render_analytics_driver_subsection(year: str = "current"):
    """
    Driver analytics subsection with all visualizations.
    
    Args:
        year: Season year to analyze
    """
    st.subheader("Driver Analytics")
    
    # Fetch driver standings to populate selector
    driver_standings = fetch_driver_standings(year)
    
    if not driver_standings:
        st.error("Unable to load driver standings. Please try again later.")
        return
    
    # Create driver options for selector
    driver_options = {}
    for standing in driver_standings:
        driver = standing.get('Driver', {})
        driver_id = driver.get('driverId', '')
        driver_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
        constructor = standing.get('Constructors', [{}])[0]
        team_name = constructor.get('name', 'Unknown')
        
        # Display format: "Max Verstappen (Red Bull)"
        display_name = f"{driver_name} ({team_name})"
        driver_options[display_name] = {
            'driver_id': driver_id,
            'driver_name': driver_name,
            'team_name': team_name
        }
    
    # Driver selector
    selected_display = st.selectbox(
        "Select Driver",
        options=list(driver_options.keys()),
        key="driver_analytics_selector",
        help="Select a driver to view detailed performance analytics"
    )
    
    if not selected_display or selected_display not in driver_options:
        return
    
    selected_driver = driver_options[selected_display]
    driver_id = selected_driver['driver_id']
    driver_name = selected_driver['driver_name']
    team_name = selected_driver['team_name']
    
    # Metric toggle for performance trends
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {driver_name} - {year} Season")
    with col2:
        metric_type = st.selectbox(
            "Trend Metric",
            options=["Position", "Points"],
            key="driver_analytics_metric",
            help="Select metric to display in performance trends"
        )
    
    # Fetch driver race results
    with st.spinner(f"Loading race data for {driver_name}..."):
        try:
            race_results = fetch_driver_race_results(driver_id, year)
        except Exception as e:
            st.error(f"❌ Error fetching race data: {str(e)}. The API may be temporarily unavailable. Please try again later.")
            return
    
    if not race_results:
        st.warning(f"⚠️ No race data available for {driver_name} in {year}. This driver may not have competed in this season, or the data is not yet available.")
        return
    
    # Check if we have sufficient data for any meaningful analysis
    if len(race_results) < 3:
        st.warning(f"⚠️ Limited data available: Only {len(race_results)} races found for {driver_name} in {year}. Most analytics require at least 5 races for meaningful results.")
        # Continue anyway to show what we can
    
    # Calculate all analytics (pass race_results directly - they're already in the right format)
    metric_param = "position" if metric_type == "Position" else "points"
    
    try:
        with st.spinner("Calculating analytics..."):
            # Performance trends
            trends = calculate_analytics_performance_trends(race_results, metric=metric_param)
            
            # Consistency metrics
            consistency = calculate_analytics_consistency_score(race_results)
            
            # Qualifying vs race correlation
            correlation = calculate_analytics_qualifying_race_correlation(race_results)
            
            # DNF rate
            dnf_data = calculate_analytics_dnf_rate(race_results)
            
            # Points per race
            points_data = calculate_analytics_points_per_race(race_results, exclude_dnf=False)
            points_data_no_dnf = calculate_analytics_points_per_race(race_results, exclude_dnf=True)
            
            # Form indicator
            form = calculate_analytics_form_indicator(race_results, n_races=5)
    except Exception as e:
        st.error(f"❌ Error calculating analytics: {str(e)}. Please try refreshing the page or selecting a different driver.")
        return
    
    # Display performance trends chart
    st.markdown("#### Performance Trends")
    if trends is not None and not trends.empty:
        trend_chart = create_analytics_trend_chart(
            trends,
            metric_name=metric_type,
            driver_name=driver_name,
            team_color=None  # Could add team color mapping here
        )
        st.plotly_chart(trend_chart, use_container_width=True)
    else:
        if not race_results:
            st.warning("⚠️ No race data available for performance trends.")
        else:
            st.info(f"ℹ️ Insufficient data for performance trends. Found {len(race_results)} races.")
    
    # Display consistency metrics
    st.markdown("#### Consistency Metrics")
    if consistency:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Consistency Score",
                f"{consistency['consistency_score']:.1f}/100",
                help="Higher score indicates more consistent performance (0-100 scale)"
            )
        with col2:
            st.metric(
                "Avg Position",
                f"{consistency['avg_position']:.1f}",
                help="Average finishing position in completed races"
            )
        with col3:
            st.metric(
                "Completed Races",
                f"{consistency['completed_races']}/{consistency['total_races']}",
                help="Number of races finished vs total races"
            )
    else:
        # More specific error message based on available data
        total_races = len(race_results) if race_results else 0
        if total_races == 0:
            st.warning("⚠️ No race data available for consistency analysis.")
        elif total_races < 5:
            st.warning(f"⚠️ Insufficient data for consistency metrics: Only {total_races} races found (minimum 5 completed races required).")
        else:
            st.warning("⚠️ Insufficient completed races for consistency metrics (minimum 5 required). Driver may have too many DNFs.")
    
    # Display qualifying vs race correlation
    st.markdown("#### Qualifying vs Race Performance")
    if correlation and not correlation.get('insufficient_data', False):
        # Show info message if there's missing data
        if correlation.get('missing_data_count', 0) > 0:
            st.info(f"ℹ️ Note: {correlation['missing_data_count']} races excluded due to missing qualifying or race data.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create scatter plot
            scatter_chart = create_analytics_scatter_chart(
                correlation['scatter_data'],
                x_label="Grid Position",
                y_label="Finish Position",
                title=f"{driver_name} - Qualifying vs Race",
                correlation=correlation['correlation_coefficient']
            )
            st.plotly_chart(scatter_chart, use_container_width=True)
        
        with col2:
            if correlation['correlation_coefficient'] is not None:
                st.metric(
                    "Correlation",
                    f"{correlation['correlation_coefficient']:.3f}",
                    help="Correlation between grid and finish position (-1 to 1)"
                )
            else:
                st.metric(
                    "Correlation",
                    "N/A",
                    help="Insufficient variance in data for correlation calculation"
                )
            st.metric(
                "Avg Position Change",
                f"{correlation['avg_position_change']:+.1f}",
                help="Average positions gained (+) or lost (-) from grid to finish"
            )
            st.info(f"**Classification:** {correlation['classification']}")
    elif correlation and correlation.get('insufficient_data', False):
        missing_count = correlation.get('missing_data_count', 0)
        races_found = correlation.get('races_analyzed', 0)
        
        if missing_count > 0:
            st.warning(f"⚠️ Insufficient data for correlation analysis: Only {races_found} races with complete qualifying and race data found (minimum 5 required). {missing_count} races had missing data.")
        else:
            st.warning(f"⚠️ Insufficient data for correlation analysis: Only {races_found} completed races found (minimum 5 required).")
    else:
        st.info("Insufficient data for correlation analysis.")
    
    # Display DNF rate analysis
    st.markdown("#### DNF Rate Analysis")
    if dnf_data:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "DNF Rate",
                f"{dnf_data['dnf_percentage']:.1f}%",
                help="Percentage of races ending in DNF"
            )
        with col2:
            st.metric(
                "DNF Count",
                f"{dnf_data['dnf_count']}/{dnf_data['total_races']}",
                help="Number of DNFs vs total races"
            )
        with col3:
            # Show most common DNF cause if available
            if dnf_data['dnf_causes']:
                most_common = max(dnf_data['dnf_causes'].items(), key=lambda x: x[1])
                st.metric(
                    "Most Common Cause",
                    most_common[0],
                    delta=f"{most_common[1]} times",
                    help="Most frequent DNF cause"
                )
        
        # Display DNF cause breakdown if available
        if dnf_data['dnf_causes']:
            st.markdown("**DNF Cause Breakdown:**")
            cause_df = pd.DataFrame([
                {"Cause": cause, "Count": count}
                for cause, count in dnf_data['dnf_causes'].items()
            ])
            st.dataframe(cause_df, hide_index=True, use_container_width=True)
    
    # Display points per race comparison
    st.markdown("#### Points Per Race")
    if points_data and points_data_no_dnf:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Points Per Race (All)",
                f"{points_data['points_per_race']:.2f}",
                help="Total points divided by all races"
            )
        with col2:
            st.metric(
                "Points Per Race (Finished)",
                f"{points_data_no_dnf['points_per_race']:.2f}",
                help="Total points divided by completed races only"
            )
        with col3:
            st.metric(
                "Total Points",
                f"{points_data['total_points']:.0f}",
                help="Total championship points scored"
            )
    
    # Display form indicator
    st.markdown("#### Recent Form (Last 5 Races)")
    if form:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Avg Position",
                f"{form['avg_position']:.1f}",
                help=f"Average finishing position in last {form['races_analyzed']} races"
            )
        with col2:
            st.metric(
                "Total Points",
                f"{form['total_points']:.0f}",
                help=f"Points scored in last {form['races_analyzed']} races"
            )
        with col3:
            # Display trend with arrow
            trend_dir = form['trend_direction']
            if trend_dir == 'improving':
                trend_emoji = "📈"
                trend_color = "green"
            elif trend_dir == 'declining':
                trend_emoji = "📉"
                trend_color = "red"
            else:
                trend_emoji = "➡️"
                trend_color = "gray"
            
            st.metric(
                "Trend",
                f"{trend_emoji} {trend_dir.capitalize()}",
                delta=f"Slope: {form['trend_slope']:.2f}",
                help="Performance trend based on linear regression"
            )
        
        if form['races_analyzed'] < 5:
            st.info(f"ℹ️ Form indicator based on {form['races_analyzed']} races (fewer than 5 available in season).")
    else:
        total_races = len(race_results) if race_results else 0
        if total_races == 0:
            st.warning("⚠️ No race data available for form indicator.")
        else:
            st.info(f"ℹ️ Insufficient data for form indicator. Found {total_races} races (at least 1 race required).")


def render_analytics_team_subsection(year: str = "current"):
    """
    Team analytics subsection with all visualizations.
    
    Args:
        year: Season year to analyze
    """
    st.subheader("Team Analytics")
    
    # Fetch constructor standings to populate selector
    constructor_standings = fetch_constructor_standings(year)
    
    if not constructor_standings:
        st.error("Unable to load constructor standings. Please try again later.")
        return
    
    # Create constructor options for selector
    constructor_options = {}
    for standing in constructor_standings:
        constructor = standing.get('Constructor', {})
        constructor_id = constructor.get('constructorId', '')
        constructor_name = constructor.get('name', 'Unknown')
        position = standing.get('position', 'N/A')
        points = standing.get('points', '0')
        
        # Display format: "Red Bull (P1 - 860 pts)"
        display_name = f"{constructor_name} (P{position} - {points} pts)"
        constructor_options[display_name] = {
            'constructor_id': constructor_id,
            'constructor_name': constructor_name,
            'position': position,
            'points': points
        }
    
    # Constructor selector
    selected_display = st.selectbox(
        "Select Constructor",
        options=list(constructor_options.keys()),
        key="team_analytics_selector",
        help="Select a constructor to view team performance analytics"
    )
    
    if not selected_display or selected_display not in constructor_options:
        return
    
    selected_constructor = constructor_options[selected_display]
    constructor_id = selected_constructor['constructor_id']
    constructor_name = selected_constructor['constructor_name']
    
    st.markdown(f"### {constructor_name} - {year} Season")
    
    # Fetch constructor race results
    with st.spinner(f"Loading race data for {constructor_name}..."):
        try:
            constructor_results = fetch_constructor_race_results(constructor_id, year)
        except Exception as e:
            st.error(f"❌ Error fetching race data: {str(e)}. The API may be temporarily unavailable. Please try again later.")
            return
    
    if not constructor_results:
        st.warning(f"⚠️ No race data available for {constructor_name} in {year}. This constructor may not have competed in this season, or the data is not yet available.")
        return
    
    # Check if we have sufficient data
    if len(constructor_results) < 3:
        st.warning(f"⚠️ Limited data available: Only {len(constructor_results)} races found for {constructor_name} in {year}. Most analytics require more races for meaningful results.")
    
    # Calculate all analytics
    try:
        with st.spinner("Calculating team analytics..."):
            # Team reliability metrics
            reliability = calculate_analytics_team_reliability(constructor_results, year)
            
            # Constructor development trends
            development = calculate_analytics_constructor_development(constructor_results, window_size=3)
            
            # Get driver pairing data - need to fetch individual driver results
            # Extract drivers from first race
            first_race = constructor_results[0] if constructor_results else None
            drivers = []
            if first_race:
                results = first_race.get('Results', [])
                for result in results:
                    driver = result.get('Driver', {})
                    driver_id = driver.get('driverId', '')
                    driver_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
                    if driver_id and driver_name:
                        drivers.append({'id': driver_id, 'name': driver_name})
            
            # Fetch individual driver results for pairing analysis
            driver_pairing = None
            if len(drivers) >= 2:
                driver1_results = fetch_driver_race_results(drivers[0]['id'], year)
                driver2_results = fetch_driver_race_results(drivers[1]['id'], year)
                
                if driver1_results and driver2_results:
                    driver_pairing = calculate_analytics_driver_pairing(
                        driver1_results,
                        driver2_results,
                        drivers[0]['name'],
                        drivers[1]['name']
                    )
    except Exception as e:
        st.error(f"❌ Error calculating analytics: {str(e)}. Please try refreshing the page or selecting a different constructor.")
        return
    
    # Display reliability metrics
    st.markdown("#### Team Reliability Metrics")
    if reliability:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Both Drivers Finished",
                f"{reliability['both_finished_pct']:.1f}%",
                help="Percentage of races where both drivers finished"
            )
        with col2:
            st.metric(
                "Avg Finish Position",
                f"{reliability['avg_finish_position']:.2f}",
                help="Average finishing position across both drivers"
            )
        with col3:
            st.metric(
                "Mechanical DNF Rate",
                f"{reliability['mechanical_dnf_rate']:.1f}%",
                help="Percentage of mechanical failures across both drivers"
            )
        
        st.info(f"📊 Analysis based on {reliability['total_races']} races")
    else:
        st.warning("⚠️ Unable to calculate reliability metrics.")
    
    # Display development trends chart
    st.markdown("#### Constructor Development Trends")
    if development is not None and not development.empty:
        # Create development trend chart
        fig = go.Figure()
        
        # Add rolling average points trace
        fig.add_trace(go.Scatter(
            x=development['round'],
            y=development['rolling_avg_points'],
            mode='lines+markers',
            name='Rolling Avg Points',
            line=dict(color='#E10600', width=3),
            marker=dict(size=8, color='#E10600'),
            customdata=development[['race_name']].values,
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>' +
                'Round: %{x}<br>' +
                'Avg Points: %{y:.2f}<br>' +
                '<extra></extra>'
            )
        ))
        
        # Update layout
        fig.update_layout(
            title=f"{constructor_name} - Development Trend (3-Race Rolling Average)",
            xaxis_title="Race Round",
            yaxis_title="Rolling Average Points",
            hovermode='closest',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title_font=dict(size=16, color='#E10600'),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="sans-serif"
            ),
            xaxis=dict(
                tickmode='linear',
                tick0=1,
                dtick=1,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            yaxis=dict(
                gridcolor='rgba(128,128,128,0.2)'
            ),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show trend classification
        if not development.empty:
            trend = development['trend_classification'].iloc[0]
            if trend == 'improving':
                st.success(f"📈 Trend: **{trend.capitalize()}** - Team performance is improving over the season")
            elif trend == 'declining':
                st.error(f"📉 Trend: **{trend.capitalize()}** - Team performance is declining over the season")
            elif trend == 'stable':
                st.info(f"➡️ Trend: **{trend.capitalize()}** - Team performance is stable throughout the season")
            else:
                st.warning(f"⚠️ Trend: **{trend}**")
    else:
        st.warning("⚠️ Insufficient data for development trends.")
    
    # Display driver pairing effectiveness
    st.markdown("#### Driver Pairing Effectiveness")
    if driver_pairing:
        # Display driver names
        st.markdown(f"**{driver_pairing['driver1_name']}** vs **{driver_pairing['driver2_name']}**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Points Ratio",
                driver_pairing['points_ratio'],
                help="Points distribution between the two drivers"
            )
        with col2:
            st.metric(
                "Avg Qualifying Gap",
                f"{driver_pairing['quali_gap']:.2f} positions",
                help="Average gap in qualifying positions"
            )
        with col3:
            st.metric(
                "Avg Race Gap",
                f"{driver_pairing['race_gap']:.2f} positions",
                help="Average gap in race finishing positions"
            )
        
        # Show balance flag
        if driver_pairing['balance_flag'] == 'imbalanced':
            st.warning(f"⚠️ **Imbalanced pairing** - One driver is significantly outperforming the other (>70:30 points ratio)")
        elif driver_pairing['balance_flag'] == 'balanced':
            st.success(f"✅ **Balanced pairing** - Both drivers are contributing relatively equally")
        
        # Create comparison chart
        st.markdown("**Points Comparison:**")
        comparison_df = pd.DataFrame({
            'Driver': [driver_pairing['driver1_name'], driver_pairing['driver2_name']],
            'Points': [driver_pairing['driver1_points'], driver_pairing['driver2_points']]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=comparison_df['Driver'],
            y=comparison_df['Points'],
            marker_color=['#E10600', '#1E41FF'],
            text=comparison_df['Points'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Points: %{y:.1f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"Driver Points Comparison - {constructor_name}",
            xaxis_title="Driver",
            yaxis_title="Points",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title_font=dict(size=16, color='#E10600'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        if len(drivers) < 2:
            st.warning("⚠️ Unable to analyze driver pairing - insufficient driver data.")
        else:
            st.warning("⚠️ Unable to calculate driver pairing metrics.")


def render_analytics_circuit_subsection(year: str = "current"):
    """
    Circuit analytics subsection with circuit difficulty ratings and driver performance.
    
    Args:
        year: Season year to analyze
    """
    st.subheader("Circuit Analytics")
    
    # Fetch all races to get circuit list and calculate difficulty
    with st.spinner("Loading circuit data..."):
        try:
            all_races = fetch_all_races(year)
        except Exception as e:
            st.error(f"❌ Error fetching race data: {str(e)}. The API may be temporarily unavailable. Please try again later.")
            return
    
    if not all_races:
        st.warning(f"⚠️ No race data available for {year}. Please select a different season.")
        return
    
    # Extract unique circuits from races
    circuits = {}
    for race in all_races:
        circuit = race.get('Circuit', {})
        circuit_name = circuit.get('circuitName', 'Unknown')
        if circuit_name != 'Unknown' and circuit_name not in circuits:
            circuits[circuit_name] = circuit
    
    if not circuits:
        st.warning("⚠️ No circuits found in the race data.")
        return
    
    # Calculate circuit difficulty ratings
    with st.spinner("Calculating circuit difficulty ratings..."):
        try:
            difficulty_df = calculate_analytics_circuit_difficulty(all_races, [year])
        except Exception as e:
            st.error(f"❌ Error calculating circuit difficulty: {str(e)}")
            return
    
    # Display circuit difficulty ratings table
    st.markdown("#### Circuit Difficulty Ratings")
    
    if difficulty_df is not None and not difficulty_df.empty:
        st.info("ℹ️ Difficulty score combines DNF rate and position volatility. Higher scores indicate more challenging circuits.")
        
        # Format the dataframe for display
        display_df = difficulty_df.copy()
        display_df.columns = ['Circuit', 'DNF Rate (%)', 'Avg Position Change', 'Difficulty Score', 'Races Analyzed']
        
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Circuit": st.column_config.TextColumn("Circuit", width="medium"),
                "DNF Rate (%)": st.column_config.NumberColumn("DNF Rate (%)", format="%.1f%%"),
                "Avg Position Change": st.column_config.NumberColumn("Avg Position Change", format="%.2f"),
                "Difficulty Score": st.column_config.ProgressColumn(
                    "Difficulty Score",
                    format="%.1f",
                    min_value=0,
                    max_value=100
                ),
                "Races Analyzed": st.column_config.NumberColumn("Races", format="%d")
            }
        )
    else:
        st.warning("⚠️ Unable to calculate circuit difficulty ratings.")
    
    # Driver-specific circuit performance section
    st.markdown("---")
    st.markdown("#### Driver Performance at Circuit")
    
    # Fetch driver standings to populate selector
    driver_standings = fetch_driver_standings(year)
    
    if not driver_standings:
        st.warning("⚠️ Unable to load driver standings for circuit performance analysis.")
        return
    
    # Create driver options
    driver_options = {}
    for standing in driver_standings:
        driver = standing.get('Driver', {})
        driver_id = driver.get('driverId', '')
        driver_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
        constructor = standing.get('Constructors', [{}])[0]
        team_name = constructor.get('name', 'Unknown')
        
        display_name = f"{driver_name} ({team_name})"
        driver_options[display_name] = {
            'driver_id': driver_id,
            'driver_name': driver_name,
            'team_name': team_name
        }
    
    # Create two columns for selectors
    col1, col2 = st.columns(2)
    
    with col1:
        selected_driver_display = st.selectbox(
            "Select Driver",
            options=list(driver_options.keys()),
            key="circuit_driver_selector",
            help="Select a driver to view their performance at a specific circuit"
        )
    
    with col2:
        selected_circuit = st.selectbox(
            "Select Circuit",
            options=sorted(circuits.keys()),
            key="circuit_selector",
            help="Select a circuit to view driver performance"
        )
    
    if not selected_driver_display or not selected_circuit:
        return
    
    selected_driver = driver_options[selected_driver_display]
    driver_id = selected_driver['driver_id']
    driver_name = selected_driver['driver_name']
    
    # Fetch driver's race results for the selected year
    with st.spinner(f"Loading {driver_name}'s race data..."):
        try:
            driver_races = fetch_driver_race_results(driver_id, year)
        except Exception as e:
            st.error(f"❌ Error fetching driver race data: {str(e)}")
            return
    
    if not driver_races:
        st.warning(f"⚠️ No race data available for {driver_name} in {year}.")
        return
    
    # Filter races for the selected circuit
    circuit_races = [
        race for race in driver_races
        if race.get('Circuit', {}).get('circuitName', '') == selected_circuit
    ]
    
    if not circuit_races:
        st.info(f"ℹ️ {driver_name} did not race at {selected_circuit} in {year}.")
        return
    
    # Calculate circuit-specific performance
    with st.spinner("Calculating circuit performance..."):
        try:
            circuit_perf = calculate_analytics_circuit_performance(
                circuit_races,
                selected_circuit,
                min_appearances=1  # Lower threshold for single season
            )
        except Exception as e:
            st.error(f"❌ Error calculating circuit performance: {str(e)}")
            return
    
    # Display circuit performance metrics
    st.markdown(f"##### {driver_name} at {selected_circuit}")
    
    if circuit_perf['low_sample_warning'] and circuit_perf['appearances'] < 3:
        st.warning(f"⚠️ Limited data: Only {circuit_perf['appearances']} race(s) at this circuit. Statistics may not be representative.")
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if circuit_perf['avg_finish'] is not None:
            st.metric(
                "Avg Finish",
                f"{circuit_perf['avg_finish']:.1f}",
                help="Average finishing position at this circuit"
            )
        else:
            st.metric(
                "Avg Finish",
                "N/A",
                help="No finished races at this circuit"
            )
    
    with col2:
        st.metric(
            "Win Rate",
            f"{circuit_perf['win_rate']:.1f}%",
            help="Percentage of races won at this circuit"
        )
    
    with col3:
        st.metric(
            "Podium Rate",
            f"{circuit_perf['podium_rate']:.1f}%",
            help="Percentage of podium finishes at this circuit"
        )
    
    with col4:
        st.metric(
            "Points Rate",
            f"{circuit_perf['points_rate']:.1f}%",
            help="Percentage of points-scoring finishes at this circuit"
        )
    
    # Display race-by-race results at this circuit
    st.markdown("##### Race Results at This Circuit")
    
    race_results_list = []
    for race in circuit_races:
        results = race.get('Results', [])
        if results:
            result = results[0]
            race_results_list.append({
                'Race': race.get('raceName', 'Unknown'),
                'Date': race.get('date', 'Unknown'),
                'Grid': result.get('grid', 'N/A'),
                'Position': result.get('position', 'N/A'),
                'Points': result.get('points', '0'),
                'Status': result.get('status', 'Unknown')
            })
    
    if race_results_list:
        results_df = pd.DataFrame(race_results_list)
        st.dataframe(
            results_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Race": st.column_config.TextColumn("Race", width="medium"),
                "Date": st.column_config.DateColumn("Date"),
                "Grid": st.column_config.TextColumn("Grid", width="small"),
                "Position": st.column_config.TextColumn("Finish", width="small"),
                "Points": st.column_config.NumberColumn("Points", format="%d"),
                "Status": st.column_config.TextColumn("Status", width="medium")
            }
        )
    else:
        st.info("No race results available.")


def render_analytics_comparative_subsection(year: str = "current"):
    """
    Comparative analytics subsection.
    
    Controls:
    - Multi-select for drivers (3-10)
    - Season selector (single or multi)
    - Comparison type selector (current season vs season-over-season)
    
    Displays:
    - Radar chart for multi-driver comparison
    - Grouped bar charts for direct metric comparison
    - Season-over-season line charts
    - Percentile rankings
    
    Args:
        year: Season year to analyze
    """
    st.subheader("⚔️ Comparative Analytics")
    st.markdown("Compare multiple drivers across various performance metrics")
    
    # Comparison type selector
    comparison_type = st.radio(
        "Comparison Type",
        options=["Multi-Driver Comparison", "Season-Over-Season Analysis", "Percentile Rankings"],
        horizontal=True,
        key="comparative_type"
    )
    
    if comparison_type == "Multi-Driver Comparison":
        render_multi_driver_comparison(year)
    elif comparison_type == "Season-Over-Season Analysis":
        render_season_comparison(year)
    else:
        render_percentile_rankings(year)


def render_multi_driver_comparison(year: str = "current"):
    """
    Render multi-driver comparison section.
    
    Args:
        year: Season year to analyze
    """
    st.markdown("### Multi-Driver Comparison")
    st.markdown("Compare 3-10 drivers across standardized performance metrics")
    
    # Fetch driver standings to get driver list
    with st.spinner("Loading driver list..."):
        standings_data = fetch_driver_standings(year)
    
    if not standings_data:
        st.error("Unable to load driver standings. Please try again later.")
        return
    
    # Parse driver standings
    standings = parse_driver_standings(standings_data)
    
    if not standings:
        st.warning("No driver data available for the selected season.")
        return
    
    # Create driver options (name and ID)
    driver_options = {}
    for driver in standings:
        driver_name = f"{driver['driver_name']}"
        driver_id = driver['driver_id']
        driver_options[driver_name] = driver_id
    
    # Multi-select for drivers
    selected_driver_names = st.multiselect(
        "Select Drivers to Compare (3-10)",
        options=list(driver_options.keys()),
        default=list(driver_options.keys())[:3] if len(driver_options) >= 3 else list(driver_options.keys()),
        key="multi_driver_selector",
        help="Select between 3 and 10 drivers for comparison"
    )
    
    # Validate selection
    if len(selected_driver_names) < 3:
        st.info("Please select at least 3 drivers for comparison.")
        return
    
    if len(selected_driver_names) > 10:
        st.warning("Please select no more than 10 drivers for comparison.")
        return
    
    # Fetch race results for selected drivers
    drivers_data = {}
    
    with st.spinner("Fetching race data for selected drivers..."):
        for driver_name in selected_driver_names:
            driver_id = driver_options[driver_name]
            race_results = fetch_driver_race_results(driver_id, year)
            
            if race_results:
                drivers_data[driver_name] = race_results
    
    if not drivers_data:
        st.error("Unable to load race data for selected drivers.")
        return
    
    # Calculate comparison metrics
    with st.spinner("Calculating comparison metrics..."):
        comparison_df = calculate_analytics_multi_driver_comparison(
            drivers_data,
            metrics=['avg_finish', 'points_per_race', 'consistency_score', 'dnf_rate']
        )
    
    if comparison_df.empty:
        st.warning("No comparison data available.")
        return
    
    # Display metrics summary
    st.markdown("#### Performance Metrics Summary")
    st.dataframe(
        comparison_df.style.format({
            'avg_finish': '{:.2f}',
            'points_per_race': '{:.2f}',
            'consistency_score': '{:.1f}',
            'dnf_rate': '{:.1f}%'
        }).background_gradient(subset=['points_per_race', 'consistency_score'], cmap='RdYlGn'),
        use_container_width=True
    )
    
    # Normalize metrics for radar chart (0-100 scale)
    radar_df = comparison_df.copy()
    
    # Invert avg_finish (lower is better) and scale to 0-100
    if 'avg_finish' in radar_df.columns:
        max_pos = 20
        radar_df['avg_finish_normalized'] = radar_df['avg_finish'].apply(
            lambda x: max(0, 100 - (x / max_pos * 100)) if pd.notna(x) else 0
        )
    
    # Points per race - normalize to 0-100 (25 points = 100)
    if 'points_per_race' in radar_df.columns:
        radar_df['points_normalized'] = radar_df['points_per_race'].apply(
            lambda x: min(100, (x / 25) * 100) if pd.notna(x) else 0
        )
    
    # Consistency score is already 0-100
    if 'consistency_score' in radar_df.columns:
        radar_df['consistency_normalized'] = radar_df['consistency_score'].fillna(0)
    
    # Invert DNF rate (lower is better) and scale to 0-100
    if 'dnf_rate' in radar_df.columns:
        radar_df['reliability_normalized'] = radar_df['dnf_rate'].apply(
            lambda x: max(0, 100 - x) if pd.notna(x) else 0
        )
    
    # Create radar chart
    st.markdown("#### Performance Radar Chart")
    st.markdown("All metrics normalized to 0-100 scale (higher is better)")
    
    radar_metrics = ['avg_finish_normalized', 'points_normalized', 'consistency_normalized', 'reliability_normalized']
    radar_metric_labels = ['Finishing Position', 'Points Scoring', 'Consistency', 'Reliability']
    
    # Prepare data for radar chart
    radar_chart_df = radar_df[['driver_name'] + radar_metrics].copy()
    radar_chart_df.columns = ['driver_name'] + radar_metric_labels
    
    fig_radar = create_analytics_radar_chart(
        radar_chart_df,
        radar_metric_labels,
        selected_driver_names
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # Create grouped bar chart for direct comparison
    st.markdown("#### Direct Metric Comparison")
    
    fig_bars = create_analytics_grouped_bar_chart(
        comparison_df,
        'driver_name',
        ['avg_finish', 'points_per_race', 'consistency_score'],
        "Driver Performance Metrics"
    )
    
    st.plotly_chart(fig_bars, use_container_width=True)
    
    # DNF Rate comparison
    st.markdown("#### Reliability Comparison (DNF Rate)")
    
    fig_dnf = go.Figure()
    
    fig_dnf.add_trace(go.Bar(
        x=comparison_df['driver_name'],
        y=comparison_df['dnf_rate'],
        marker=dict(
            color=comparison_df['dnf_rate'],
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="DNF %")
        ),
        text=comparison_df['dnf_rate'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>DNF Rate: %{y:.1f}%<extra></extra>'
    ))
    
    fig_dnf.update_layout(
        title="DNF Rate by Driver (Lower is Better)",
        xaxis_title="Driver",
        yaxis_title="DNF Rate (%)",
        showlegend=False,
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_dnf, use_container_width=True)


def render_season_comparison(year: str = "current"):
    """
    Render season-over-season comparison section.
    
    Args:
        year: Current season year
    """
    st.markdown("### Season-Over-Season Analysis")
    st.markdown("Track driver or team performance evolution across multiple seasons")
    
    # Entity type selector
    entity_type = st.radio(
        "Compare",
        options=["Driver", "Team"],
        horizontal=True,
        key="season_comparison_entity_type"
    )
    
    # Season range selector
    current_year = int(year) if year != "current" else 2024
    available_years = list(range(2010, current_year + 1))
    
    selected_seasons = st.multiselect(
        "Select Seasons to Compare",
        options=available_years,
        default=[current_year - 2, current_year - 1, current_year] if current_year >= 2012 else [current_year],
        key="season_comparison_years",
        help="Select 2 or more seasons for comparison"
    )
    
    if len(selected_seasons) < 2:
        st.info("Please select at least 2 seasons for comparison.")
        return
    
    if entity_type == "Driver":
        # Fetch driver list from most recent season
        with st.spinner("Loading driver list..."):
            standings_data = fetch_driver_standings(str(selected_seasons[-1]))
        
        if not standings_data:
            st.error("Unable to load driver standings.")
            return
        
        standings = parse_driver_standings(standings_data)
        
        if not standings:
            st.warning("No driver data available.")
            return
        
        # Create driver options
        driver_options = {}
        for driver in standings:
            driver_name = driver['driver_name']
            driver_id = driver['driver_id']
            driver_options[driver_name] = driver_id
        
        # Driver selector
        selected_driver_name = st.selectbox(
            "Select Driver",
            options=list(driver_options.keys()),
            key="season_comparison_driver"
        )
        
        if not selected_driver_name:
            return
        
        driver_id = driver_options[selected_driver_name]
        
        # Fetch race results for each season
        entity_results_by_season = {}
        
        with st.spinner(f"Fetching race data for {selected_driver_name} across {len(selected_seasons)} seasons..."):
            for season in selected_seasons:
                race_results = fetch_driver_race_results(driver_id, str(season))
                if race_results:
                    entity_results_by_season[str(season)] = race_results
        
        if not entity_results_by_season:
            st.warning(f"No race data available for {selected_driver_name} in the selected seasons.")
            return
        
        # Calculate season comparison
        with st.spinner("Calculating season-over-season metrics..."):
            comparison_df = calculate_analytics_season_comparison(
                entity_results_by_season,
                entity_type="driver"
            )
        
        if comparison_df.empty:
            st.warning("No comparison data available.")
            return
        
        # Display metrics table
        st.markdown(f"#### {selected_driver_name} - Season Performance")
        
        display_df = comparison_df[['season', 'avg_finish', 'total_points', 'points_per_race', 'consistency_score', 'yoy_change_pct']].copy()
        
        st.dataframe(
            display_df.style.format({
                'avg_finish': '{:.2f}',
                'total_points': '{:.1f}',
                'points_per_race': '{:.2f}',
                'consistency_score': '{:.1f}',
                'yoy_change_pct': '{:+.1f}%'
            }).background_gradient(subset=['points_per_race'], cmap='RdYlGn'),
            use_container_width=True
        )
        
        # Create line charts for season progression
        st.markdown("#### Performance Trends Across Seasons")
        
        # Points per race trend
        fig_points = go.Figure()
        
        fig_points.add_trace(go.Scatter(
            x=comparison_df['season'],
            y=comparison_df['points_per_race'],
            mode='lines+markers',
            name='Points per Race',
            line=dict(color='#E10600', width=3),
            marker=dict(size=10),
            hovertemplate='<b>Season %{x}</b><br>Points per Race: %{y:.2f}<extra></extra>'
        ))
        
        fig_points.update_layout(
            title=f"{selected_driver_name} - Points per Race by Season",
            xaxis_title="Season",
            yaxis_title="Points per Race",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_points, use_container_width=True)
        
        # Average finish position trend
        fig_finish = go.Figure()
        
        fig_finish.add_trace(go.Scatter(
            x=comparison_df['season'],
            y=comparison_df['avg_finish'],
            mode='lines+markers',
            name='Avg Finish Position',
            line=dict(color='#0090FF', width=3),
            marker=dict(size=10),
            hovertemplate='<b>Season %{x}</b><br>Avg Finish: %{y:.2f}<extra></extra>'
        ))
        
        fig_finish.update_layout(
            title=f"{selected_driver_name} - Average Finish Position by Season",
            xaxis_title="Season",
            yaxis_title="Average Finish Position",
            yaxis=dict(autorange='reversed'),  # Lower position is better
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_finish, use_container_width=True)
        
        # Consistency trend
        if 'consistency_score' in comparison_df.columns:
            fig_consistency = go.Figure()
            
            fig_consistency.add_trace(go.Scatter(
                x=comparison_df['season'],
                y=comparison_df['consistency_score'],
                mode='lines+markers',
                name='Consistency Score',
                line=dict(color='#00D2BE', width=3),
                marker=dict(size=10),
                hovertemplate='<b>Season %{x}</b><br>Consistency: %{y:.1f}<extra></extra>'
            ))
            
            fig_consistency.update_layout(
                title=f"{selected_driver_name} - Consistency Score by Season",
                xaxis_title="Season",
                yaxis_title="Consistency Score (0-100)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_consistency, use_container_width=True)
    
    else:
        st.info("Team season-over-season comparison coming soon!")


def render_percentile_rankings(year: str = "current"):
    """
    Render percentile rankings section.
    
    Args:
        year: Season year to analyze
    """
    st.markdown("### Percentile Rankings")
    st.markdown("See how a driver ranks relative to the entire field")
    
    # Fetch driver standings
    with st.spinner("Loading driver list..."):
        standings_data = fetch_driver_standings(year)
    
    if not standings_data:
        st.error("Unable to load driver standings.")
        return
    
    standings = parse_driver_standings(standings_data)
    
    if not standings:
        st.warning("No driver data available.")
        return
    
    # Create driver options
    driver_options = {}
    for driver in standings:
        driver_name = driver['driver_name']
        driver_id = driver['driver_id']
        driver_options[driver_name] = driver_id
    
    # Driver selector
    selected_driver_name = st.selectbox(
        "Select Driver",
        options=list(driver_options.keys()),
        key="percentile_driver"
    )
    
    if not selected_driver_name:
        return
    
    driver_id = driver_options[selected_driver_name]
    
    # Fetch race results for all drivers
    all_drivers_results = {}
    
    with st.spinner("Fetching race data for all drivers..."):
        for driver_name, driver_id in driver_options.items():
            race_results = fetch_driver_race_results(driver_id, year)
            if race_results:
                all_drivers_results[driver_name] = race_results
    
    if not all_drivers_results:
        st.error("Unable to load race data.")
        return
    
    # Get target driver results
    target_driver_id = driver_options[selected_driver_name]
    driver_results = all_drivers_results.get(selected_driver_name)
    
    if not driver_results:
        st.warning(f"No race data available for {selected_driver_name}.")
        return
    
    # Calculate percentile rankings
    with st.spinner("Calculating percentile rankings..."):
        percentiles = calculate_analytics_percentile_rankings(
            driver_results,
            all_drivers_results,
            year
        )
    
    # Display field size info
    st.info(f"Rankings calculated relative to {percentiles['field_size']} drivers who competed in at least 50% of races")
    
    # Display percentile metrics
    st.markdown(f"#### {selected_driver_name} - Percentile Rankings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Avg Finish Percentile",
            f"{percentiles['avg_finish_percentile']:.1f}",
            help="Higher percentile = better average finishing position"
        )
    
    with col2:
        st.metric(
            "Points Percentile",
            f"{percentiles['points_percentile']:.1f}",
            help="Higher percentile = more points scored"
        )
    
    with col3:
        st.metric(
            "Consistency Percentile",
            f"{percentiles['consistency_percentile']:.1f}",
            help="Higher percentile = more consistent performance"
        )
    
    # Create horizontal percentile chart
    st.markdown("#### Percentile Rankings Visualization")
    
    fig_percentile = create_analytics_horizontal_percentile_chart(
        {
            'Avg Finish': percentiles['avg_finish_percentile'],
            'Points Scored': percentiles['points_percentile'],
            'Consistency': percentiles['consistency_percentile']
        },
        selected_driver_name
    )
    
    st.plotly_chart(fig_percentile, use_container_width=True)
    
    # Interpretation guide
    with st.expander("📊 How to Interpret Percentile Rankings"):
        st.markdown("""
        **Percentile rankings show where a driver stands relative to the entire field:**
        
        - **90th percentile or above**: Elite performance, top 10% of the field
        - **75th-89th percentile**: Strong performance, upper quartile
        - **50th-74th percentile**: Above average performance
        - **25th-49th percentile**: Below average performance
        - **Below 25th percentile**: Lower quartile performance
        
        **Note**: Rankings are calculated only for drivers who competed in at least 50% of the season's races to ensure statistical validity.
        """)


def render_analytics_statistical_subsection(year: str = "current"):
    """
    Statistical insights subsection with placeholder content.
    
    Args:
        year: Season year to analyze
    """
    st.subheader("Statistical Insights")
    st.info("🚧 Qualifying-race correlations, win probabilities, and championship projections coming soon!")
    
    # Season range selector placeholder
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(
            "Start Season",
            options=["Coming soon..."],
            key="stats_start_season",
            help="Select starting season for statistical analysis"
        )
    with col2:
        st.selectbox(
            "End Season",
            options=["Coming soon..."],
            key="stats_end_season",
            help="Select ending season for statistical analysis"
        )


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="F1 Dashboard",
        page_icon="🏎️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state for auto-refresh tracking
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    # Sidebar - Year Selection
    with st.sidebar:
        st.title("⚙️ Settings")
        st.markdown("---")
        
        st.subheader("📅 Season Selection")
        
        # Generate year options (from 1950 to current year + 1)
        import datetime
        current_year = datetime.datetime.now().year
        year_options = ["Current Season"] + [str(year) for year in range(current_year, 1949, -1)]
        
        selected_year_display = st.selectbox(
            "Select Season",
            options=year_options,
            index=0,
            help="Choose a season to view historical data"
        )
        
        # Convert display value to API value
        if selected_year_display == "Current Season":
            selected_year = "current"
            season_display = f"{current_year} Season"
        else:
            selected_year = selected_year_display
            season_display = f"{selected_year} Season"
        
        st.markdown("---")
        st.info(f"📊 Viewing: **{season_display}**")
        
        # Auto-refresh toggle (only for current season)
        if selected_year == "current":
            st.markdown("---")
            auto_refresh = st.checkbox("Auto-refresh (60s)", value=True)
            
            if auto_refresh:
                # Auto-refresh logic: refresh every 60 seconds
                current_time = time.time()
                if current_time - st.session_state.last_refresh > 60:
                    st.session_state.last_refresh = current_time
                    st.rerun()
                
                time_since_refresh = int(current_time - st.session_state.last_refresh)
                next_refresh = max(0, 60 - time_since_refresh)
                st.caption(f"Next refresh in: {next_refresh}s")
    
    # App header
    st.title(f"🏎️ Formula 1 Dashboard - {season_display}")
    st.markdown("Real-time F1 race data, standings, and statistics")
    
    # Tab-based navigation
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", 
        "🏎️ Driver Standings", 
        "🏁 Constructor Standings", 
        "📅 Race Calendar",
        "🏁 All Races",
        "📊 Advanced Analytics"
    ])
    
    with tab1:
        render_overview_page(selected_year)
    
    with tab2:
        render_driver_standings_page(selected_year)
    
    with tab3:
        render_constructor_standings_page(selected_year)
    
    with tab4:
        render_race_calendar_page(selected_year)
    
    with tab5:
        render_all_races_page(selected_year)
    
    with tab6:
        render_analytics_main_page(selected_year)
    
    # Footer with last updated time
    st.divider()
    last_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.session_state.last_refresh))
    st.caption(f"Last updated: {last_update} | Data source: Jolpica F1 API (Ergast data)")


if __name__ == "__main__":
    main()
