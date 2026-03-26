"""
Pydantic models for race data including schedule, results, qualifying, and lap times.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from app.models.common import DriverInfo, ConstructorInfo


class Circuit(BaseModel):
    """Circuit information model."""
    model_config = ConfigDict(populate_by_name=True)
    
    circuitId: str
    circuitName: str
    url: Optional[str] = None
    Location: Optional[Dict[str, Any]] = None


class Race(BaseModel):
    """Race schedule entry model."""
    model_config = ConfigDict(populate_by_name=True)
    
    season: str
    round: str
    raceName: str
    Circuit: Circuit
    date: str
    time: Optional[str] = None
    url: Optional[str] = None
    
    # Optional session times - using aliases to avoid conflicts
    FirstPractice: Optional[Dict[str, str]] = None
    SecondPractice: Optional[Dict[str, str]] = None
    ThirdPractice: Optional[Dict[str, str]] = None
    Qualifying: Optional[Dict[str, str]] = None
    Sprint: Optional[Dict[str, str]] = None


class RaceResultEntry(BaseModel):
    """Single driver's race result."""
    model_config = ConfigDict(populate_by_name=True)
    
    number: Optional[str] = None
    position: str
    positionText: Optional[str] = None
    points: str
    Driver: DriverInfo
    Constructor: ConstructorInfo
    grid: str
    laps: str
    status: str
    Time: Optional[Dict[str, Any]] = None
    FastestLap: Optional[Dict[str, Any]] = None


class RaceResult(BaseModel):
    """Complete race result with all drivers."""
    model_config = ConfigDict(populate_by_name=True)
    
    season: str
    round: str
    raceName: str
    Circuit: Circuit
    date: str
    time: Optional[str] = None
    url: Optional[str] = None
    Results: List[RaceResultEntry]


class QualifyingResultEntry(BaseModel):
    """Single driver's qualifying result."""
    model_config = ConfigDict(populate_by_name=True)
    
    number: Optional[str] = None
    position: str
    Driver: DriverInfo
    Constructor: ConstructorInfo
    Q1: Optional[str] = None
    Q2: Optional[str] = None
    Q3: Optional[str] = None


class QualifyingResult(BaseModel):
    """Complete qualifying result with all drivers."""
    model_config = ConfigDict(populate_by_name=True)
    
    season: str
    round: str
    raceName: str
    Circuit: Circuit
    date: str
    time: Optional[str] = None
    url: Optional[str] = None
    QualifyingResults: List[QualifyingResultEntry]


class LapTime(BaseModel):
    """Lap time entry for a driver."""
    model_config = ConfigDict(populate_by_name=True)
    
    driverId: str
    lap: str
    position: Optional[str] = None  # Position can be None for some laps
    time: str
