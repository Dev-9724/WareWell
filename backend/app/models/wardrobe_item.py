from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class WardrobeItemCreate(BaseModel):
    # Core identity
    user_id: str = Field(..., min_length=1, examples=["dev_mdx_user"])

    # Clothing attributes
    category: str = Field(..., examples=["top"])  # top, bottom, shoes, outerwear, accessory
    colour_primary: str = Field(..., examples=["black"])
    colour_secondary: Optional[str] = Field(None, examples=["white"])

    # Context fit
    formality_level: int = Field(..., ge=0, le=10, examples=[5])
    season: List[str] = Field(default_factory=list, examples=[["spring", "summer"]])

    temperature_min: float = Field(..., examples=[10])
    temperature_max: float = Field(..., examples=[25])

    rain_suitable: bool = Field(..., examples=[True])

    # Usage tracking
    wear_count: int = Field(0, ge=0, examples=[0])
    last_worn_date: Optional[date] = Field(None, examples=["2026-03-01"])

    # Optional sustainability / extra info
    cost: Optional[float] = Field(None, ge=0, examples=[49.99])
    image_url: Optional[str] = Field(None, examples=["https://example.com/jacket.png"])


class WardrobeItemOut(WardrobeItemCreate):
    id: str
    created_at: datetime