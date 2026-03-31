from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    user_id: str = Field(..., min_length=1, examples=["dev_mdx_user"])
    outfit_id: str = Field(..., min_length=1, examples=["outfit-1"])
    rating: Literal["perfect", "okay", "not_suitable"]
    occasion: Optional[str] = Field(None, examples=["office"])
    comment: Optional[str] = Field(None, examples=["Great for cool office weather"])


class FeedbackOut(BaseModel):
    id: str
    user_id: str
    outfit_id: str
    rating: str
    occasion: Optional[str] = None
    comment: Optional[str] = None
    timestamp: datetime
    weights_before: dict
    weights_after: dict