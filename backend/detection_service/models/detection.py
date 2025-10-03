from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

class DetectionModel(BaseModel):
    timestamp: datetime
    track_id: int
    label: str
    confidence: float
    bounding_box: BoundingBox

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }