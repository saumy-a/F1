"""
Pydantic models for driver and constructor standings.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List
from app.models.common import DriverInfo, ConstructorInfo


class DriverStanding(BaseModel):
    """Driver championship standing model."""
    model_config = ConfigDict(populate_by_name=True)
    
    position: str = Field(..., description="Championship position")
    points: str = Field(..., description="Total points scored")
    wins: str = Field(..., description="Number of race wins")
    Driver: DriverInfo = Field(..., description="Driver information")
    Constructors: List[ConstructorInfo] = Field(..., description="List of constructors driver has raced for")
    
    @field_validator('position', 'points', 'wins')
    @classmethod
    def validate_numeric_string(cls, v: str) -> str:
        """Validate that string fields contain valid numeric values (int or float)."""
        try:
            float(v)  # Accept both integers and floats (e.g., 395.5 for half points)
            return v
        except ValueError:
            raise ValueError(f"Must be a numeric string, got: {v}")


class ConstructorStanding(BaseModel):
    """Constructor championship standing model."""
    model_config = ConfigDict(populate_by_name=True)
    
    position: str = Field(..., description="Championship position")
    points: str = Field(..., description="Total points scored")
    wins: str = Field(..., description="Number of race wins")
    Constructor: ConstructorInfo = Field(..., description="Constructor information")
    
    @field_validator('position', 'points', 'wins')
    @classmethod
    def validate_numeric_string(cls, v: str) -> str:
        """Validate that string fields contain valid numeric values (int or float)."""
        try:
            float(v)  # Accept both integers and floats
            return v
        except ValueError:
            raise ValueError(f"Must be a numeric string, got: {v}")
