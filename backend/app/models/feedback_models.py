from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    user_id: str = Field(..., min_length=1, examples=["dev_mdx_user"])
    outfit_id: int = Field(..., examples=[3])
    rating: Literal["perfect", "okay", "not_suitable"]
    occasion: Optional[str] = Field(None, examples=["office"])


class FeedbackOut(BaseModel):
    id: str
    user_id: str
    outfit_id: int
    rating: str
    occasion: Optional[str] = None
    timestamp: datetime
    weights_before: dict
    weights_after: dict