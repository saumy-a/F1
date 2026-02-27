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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🏎️ Driver Standings", 
        "🏁 Constructor Standings", 
        "📅 Race Calendar",
        "🏁 All Races"
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
    
    # Footer with last updated time
    st.divider()
    last_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.session_state.last_refresh))
    st.caption(f"Last updated: {last_update} | Data source: Jolpica F1 API (Ergast data)")


if __name__ == "__main__":
    main()
