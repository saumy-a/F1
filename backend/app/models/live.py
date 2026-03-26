"""
Pydantic models for live F1 data from OpenF1 API.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime


class SessionInfo(BaseModel):
    """Session information from OpenF1."""
    session_key: str = Field(description="Unique session identifier")
    session_name: str = Field(description="Session name (e.g., 'Race', 'Qualifying')")
    session_type: str = Field(description="Session type")
    date_start: str = Field(description="Session start time (ISO format)")
    date_end: Optional[str] = Field(None, description="Session end time (ISO format)")
    gmt_offset: Optional[str] = Field(None, description="GMT offset")
    location: str = Field(description="Circuit location")
    country_name: str = Field(description="Country name")
    circuit_short_name: str = Field(description="Short circuit name")
    mode: str = Field(description="Session mode: live, upcoming, or replay")
    
    @classmethod
    def model_validate(cls, obj):
        # Convert session_key to string if it's an int
        if isinstance(obj, dict) and 'session_key' in obj:
            obj['session_key'] = str(obj['session_key'])
        return super().model_validate(obj)


class Driver(BaseModel):
    """Driver information."""
    driver_number: int = Field(description="Driver's race number")
    broadcast_name: Optional[str] = Field(None, description="Broadcast name")
    full_name: Optional[str] = Field(None, description="Full name")
    name_acronym: Optional[str] = Field(None, description="Three-letter acronym")
    team_name: Optional[str] = Field(None, description="Team name")
    team_colour: Optional[str] = Field(None, description="Team color hex code")
    headshot_url: Optional[str] = Field(None, description="Driver headshot URL")


class Position(BaseModel):
    """Current race position."""
    driver_number: int = Field(description="Driver's race number")
    position: int = Field(description="Current position")
    date: str = Field(description="Timestamp of position data")


class Interval(BaseModel):
    """Time interval data."""
    driver_number: int = Field(description="Driver's race number")
    gap_to_leader: Optional[Any] = Field(None, description="Gap to race leader (null for leader, float/string for others)")
    interval: Optional[Any] = Field(None, description="Interval to car ahead (null for leader, float/string for others)")
    date: str = Field(description="Timestamp of interval data")
    session_key: Optional[int] = Field(None, description="Session key")
    meeting_key: Optional[int] = Field(None, description="Meeting key")


class Stint(BaseModel):
    """Tire stint information."""
    driver_number: int = Field(description="Driver's race number")
    stint_number: int = Field(description="Stint number")
    compound: str = Field(description="Tire compound (SOFT, MEDIUM, HARD, etc.)")
    tyre_age_at_start: int = Field(description="Tire age at stint start (laps)")
    lap_start: Optional[int] = Field(None, description="Lap number stint started")
    lap_end: Optional[int] = Field(None, description="Lap number stint ended")


class PitStop(BaseModel):
    """Pit stop data."""
    driver_number: int = Field(description="Driver's race number")
    lap_number: int = Field(description="Lap number of pit stop")
    pit_duration: float = Field(description="Pit stop duration in seconds")
    date: str = Field(description="Timestamp of pit stop")


class Weather(BaseModel):
    """Weather conditions at circuit."""
    air_temperature: float = Field(description="Air temperature in Celsius")
    track_temperature: float = Field(description="Track temperature in Celsius")
    humidity: float = Field(description="Humidity percentage")
    rainfall: int = Field(description="Rainfall indicator (0=no rain, 1=rain)")
    wind_speed: float = Field(description="Wind speed in m/s")
    wind_direction: int = Field(description="Wind direction in degrees")
    pressure: Optional[float] = Field(None, description="Air pressure in mbar")
    date: str = Field(description="Timestamp of weather data")
    session_key: Optional[int] = Field(None, description="Session key")
    meeting_key: Optional[int] = Field(None, description="Meeting key")


class RaceControlMessage(BaseModel):
    """Race control message."""
    category: str = Field(description="Message category (Flag, SafetyCar, etc.)")
    message: str = Field(description="Message text")
    date: str = Field(description="Timestamp of message")
    lap_number: Optional[int] = Field(None, description="Lap number if applicable")
    driver_number: Optional[int] = Field(None, description="Driver number if applicable")
    flag: Optional[str] = Field(None, description="Flag type if applicable")
    scope: Optional[str] = Field(None, description="Message scope")
    sector: Optional[int] = Field(None, description="Sector number if applicable")


class TeamRadio(BaseModel):
    """Team radio communication."""
    driver_number: int = Field(description="Driver's race number")
    date: str = Field(description="Timestamp of radio message")
    recording_url: str = Field(description="URL to audio recording")
    duration: Optional[float] = Field(None, description="Duration of audio clip in seconds")


class LiveDataAggregate(BaseModel):
    """Aggregated live data from all sources."""
    session_key: str = Field(description="Session identifier")
    timestamp: str = Field(description="Aggregation timestamp")
    drivers: List[Driver] = Field(default_factory=list, description="Drivers in session")
    positions: List[Position] = Field(default_factory=list, description="Current positions")
    intervals: List[Interval] = Field(default_factory=list, description="Time intervals")
    stints: List[Stint] = Field(default_factory=list, description="Tire stints")
    pits: List[PitStop] = Field(default_factory=list, description="Pit stops")
    weather: Optional[Weather] = Field(None, description="Weather conditions")
    race_control: List[RaceControlMessage] = Field(default_factory=list, description="Race control messages")
    error: Optional[str] = Field(None, description="Error message if any")
