"""
Common Pydantic models shared across multiple endpoints.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class DriverInfo(BaseModel):
    """Driver information model."""
    model_config = ConfigDict(populate_by_name=True)
    
    driverId: str = Field(..., description="Unique driver identifier")
    givenName: str = Field(..., description="Driver's first name")
    familyName: str = Field(..., description="Driver's last name")
    nationality: Optional[str] = Field(None, description="Driver's nationality")
    permanentNumber: Optional[str] = Field(None, description="Driver's permanent race number")
    code: Optional[str] = Field(None, description="Three-letter driver code")
    dateOfBirth: Optional[str] = Field(None, description="Driver's date of birth (YYYY-MM-DD)")
    url: Optional[str] = Field(None, description="Wikipedia URL for driver")


class ConstructorInfo(BaseModel):
    """Constructor (team) information model."""
    model_config = ConfigDict(populate_by_name=True)
    
    constructorId: str = Field(..., description="Unique constructor identifier")
    name: str = Field(..., description="Constructor name")
    nationality: Optional[str] = Field(None, description="Constructor's nationality")
    url: Optional[str] = Field(None, description="Wikipedia URL for constructor")
