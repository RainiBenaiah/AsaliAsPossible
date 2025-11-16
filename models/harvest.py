from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class HarvestQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"

class HarvestBase(BaseModel):
    hive_id: str
    amount_kg: float = Field(gt=0)
    quality: HarvestQuality
    date: datetime
    notes: Optional[str] = None

class HarvestCreate(HarvestBase):
    pass

class HarvestResponse(HarvestBase):
    id: str
    user_id: str
    hive_name: str
    harvester_name: str
    created_at: datetime
    
    class Config:
        populate_by_name = True

class HarvestSummary(BaseModel):
    total_harvest_kg: float
    harvest_count: int
    period: str