from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class RecommendationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecommendationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DISMISSED = "dismissed"

class RecommendationBase(BaseModel):
    hive_id: str
    action: str
    reason: str
    priority: RecommendationPriority

class RecommendationCreate(RecommendationBase):
    pass

class RecommendationResponse(RecommendationBase):
    id: str
    user_id: str
    status: RecommendationStatus
    time: str  # e.g., "2 hours ago"
    created_at: datetime
    
    class Config:
        populate_by_name = True

class RecommendationUpdate(BaseModel):
    status: Optional[RecommendationStatus] = None