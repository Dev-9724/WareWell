from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class WardrobeItemCreate(BaseModel):
    user_id: str = Field(..., min_length=1, examples=["65f4f7f96588c6c3f3e3a123"])
    name: str = Field(..., min_length=1, examples=["Red Hoodie"])
    category: str = Field(..., examples=["Top"])
    occasion: Optional[str] = Field(None, examples=["Casual"])

    colour_primary: str = Field(..., examples=["Red"])
    colour_secondary: Optional[str] = Field(None, examples=["White"])

    formality_level: int = Field(5, ge=0, le=10, examples=[5])
    season: List[str] = Field(default_factory=list, examples=[["Spring", "Autumn"]])

    temperature_min: float = Field(0, examples=[0])
    temperature_max: float = Field(40, examples=[40])

    rain_suitable: bool = Field(False, examples=[True])

    wear_count: int = Field(0, ge=0, examples=[0])
    last_worn_date: Optional[date] = Field(None, examples=["2026-03-01"])

    cost: Optional[float] = Field(0, ge=0, examples=[49.99])
    image_url: Optional[str] = Field(None, examples=["/uploads/jacket.png"])


class WardrobeItemOut(WardrobeItemCreate):
    id: str
    created_at: datetime