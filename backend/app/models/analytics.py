"""
Pydantic models for analytics API responses.
Field names match analytics service function return dicts exactly.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any


class ConsistencyScore(BaseModel):
    """Driver consistency metrics."""
    consistency_score: float = Field(ge=0, le=100, description="Consistency score (0-100)")
    std_dev: float = Field(ge=0, description="Standard deviation of finishing positions")
    avg_position: float = Field(ge=0, description="Average finishing position")
    completed_races: int = Field(ge=0, description="Number of races completed")
    total_races: int = Field(ge=0, description="Total races entered")


class DNFRate(BaseModel):
    """DNF (Did Not Finish) statistics."""
    dnf_count: int = Field(ge=0, description="Number of DNFs")
    total_races: int = Field(ge=0, description="Total races entered")
    dnf_percentage: float = Field(ge=0, le=100, description="DNF percentage (0-100)")
    dnf_causes: Dict[str, int] = Field(description="DNF causes breakdown")


class FormIndicator(BaseModel):
    """Recent form analysis."""
    avg_position: float = Field(ge=0, description="Average position in recent races")
    total_points: float = Field(ge=0, description="Total points in recent races")
    trend_direction: str = Field(description="Trend direction: improving, declining, or stable")
    trend_slope: float = Field(description="Trend slope (negative = improving)")
    races_analyzed: int = Field(ge=0, description="Number of races analyzed")


class PerformanceTrend(BaseModel):
    """Performance trend data - returns list of race records."""
    data: List[Dict[str, Any]] = Field(description="List of race performance records")


class PointsPerRace(BaseModel):
    """Points per race average."""
    total_points: float = Field(ge=0, description="Total points scored")
    races_completed: int = Field(ge=0, description="Number of races completed")
    points_per_race: float = Field(ge=0, description="Average points per race")


class QualifyingRaceCorrelation(BaseModel):
    """Correlation between qualifying and race performance."""
    correlation: float = Field(ge=-1, le=1, description="Correlation coefficient (-1 to 1)")
    qualifying_avg: float = Field(ge=0, description="Average qualifying position")
    race_avg: float = Field(ge=0, description="Average race finish position")
    sample_size: int = Field(ge=0, description="Number of races analyzed")


class TeamReliability(BaseModel):
    """Constructor reliability metrics."""
    constructor_id: str = Field(description="Constructor identifier")
    total_entries: int = Field(ge=0, description="Total race entries")
    dnf_count: int = Field(ge=0, description="Total DNFs")
    reliability_rate: float = Field(ge=0, le=1, description="Reliability rate (0-1)")


class ConstructorDevelopment(BaseModel):
    """Constructor development trajectory over season."""
    constructor_id: str = Field(description="Constructor identifier")
    early_avg: float = Field(ge=0, description="Average position in early races")
    late_avg: float = Field(ge=0, description="Average position in late races")
    improvement: float = Field(description="Position improvement (negative = better)")
    trend: str = Field(description="Development trend: improving, declining, or stable")


class DriverPairing(BaseModel):
    """Driver pairing analysis within a team."""
    constructor_id: str = Field(description="Constructor identifier")
    driver1_id: str = Field(description="First driver identifier")
    driver2_id: str = Field(description="Second driver identifier")
    driver1_avg: float = Field(ge=0, description="Driver 1 average position")
    driver2_avg: float = Field(ge=0, description="Driver 2 average position")
    driver1_wins: int = Field(ge=0, description="Driver 1 head-to-head wins")
    driver2_wins: int = Field(ge=0, description="Driver 2 head-to-head wins")


class CircuitPerformance(BaseModel):
    """Circuit-specific performance metrics."""
    circuit_id: str = Field(description="Circuit identifier")
    performances: List[Dict[str, Any]] = Field(description="Performance data by driver/team")


class CircuitDifficulty(BaseModel):
    """Circuit difficulty analysis."""
    circuit_id: str = Field(description="Circuit identifier")
    avg_dnf_rate: float = Field(ge=0, le=1, description="Average DNF rate at circuit")
    difficulty_score: float = Field(ge=0, le=100, description="Difficulty score (0-100)")


class DriverComparison(BaseModel):
    """Multi-driver comparison metrics."""
    drivers: List[str] = Field(description="List of driver IDs being compared")
    metrics: Dict[str, List[Optional[float]]] = Field(description="Metrics for each driver")


class SeasonComparison(BaseModel):
    """Multi-season comparison for a driver."""
    driver_id: str = Field(description="Driver identifier")
    seasons: List[str] = Field(description="Seasons being compared")
    metrics: Dict[str, List[float]] = Field(description="Metrics across seasons")


class PercentileRankings(BaseModel):
    """Percentile rankings for all drivers."""
    year: str = Field(description="Season year")
    rankings: Dict[str, Dict[str, float]] = Field(description="Percentile rankings by metric")


class ChampionshipProjection(BaseModel):
    """Championship projection and predictions."""
    projected_winner: str = Field(description="Projected championship winner driver ID")
    projected_points: Dict[str, float] = Field(description="Projected final points for each driver")
    confidence: float = Field(ge=0, le=1, description="Confidence level (0-1)")
    races_remaining: int = Field(ge=0, description="Number of races remaining")
