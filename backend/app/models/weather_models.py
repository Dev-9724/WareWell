from datetime import datetime
from pydantic import BaseModel, Field


class WeatherSnapshotBase(BaseModel):
    temperature: float = Field(..., examples=[12.3])
    humidity: int = Field(..., ge=0, le=100, examples=[72])
    wind: float = Field(..., examples=[10.5])  # kph (from WeatherAPI)
    rain: float = Field(0.0, examples=[0.0])   # mm (precip_mm)
    condition: str = Field(..., examples=["Cloudy"])  # normalized category
    city: str = Field(..., examples=["London"])
    timestamp: datetime
    source: str = Field(..., examples=["weatherapi"])  # "weatherapi" or "manual"


class WeatherManualIn(BaseModel):
    temperature: float
    humidity: int = Field(..., ge=0, le=100)
    wind: float
    rain: float = 0.0
    condition: str
    city: str


class WeatherSnapshotOut(WeatherSnapshotBase):
    id: str