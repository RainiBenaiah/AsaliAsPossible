from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class HiveStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"

class HiveBase(BaseModel):
    name: str
    location: str
    latitude: float
    longitude: float

class HiveCreate(HiveBase):
    pass

class HiveUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class HiveMetrics(BaseModel):
    temperature: float
    humidity: float
    weight: float
    sound_frequency: Optional[float] = None

class HiveResponse(HiveBase):
    id: str
    user_id: str
    status: HiveStatus
    temperature: float
    humidity: float
    weight: float
    alerts: int
    health_score: float
    last_updated: datetime
    
    # ML Model outputs
    queen_present: bool = True
    swarming_probability: float = 0.0
    sound_health_status: str = "Normal"
    
    class Config:
        populate_by_name = True

class HiveHistory(BaseModel):
    metric: str
    range: str
    data: list

class HiveLocation(BaseModel):
    id: str
    name: str
    location: str
    latitude: float
    longitude: float
    status: HiveStatus