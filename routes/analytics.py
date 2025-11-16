from fastapi import APIRouter, Depends
from typing import Annotated
from utils.auth_utils import get_current_user_email  #  added
from services.hive_service import HiveService
import random

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
async def get_analytics_summary(
    current_user_email: str = Depends(get_current_user_email)  #  added
):
    """Get analytics summary"""
    hives = await HiveService.get_user_hives(current_user_email)
    
    if not hives:
        return {
            "avg_temperature": 0,
            "avg_humidity": 0,
            "avg_weight": 0,
            "healthy_count": 0,
            "warning_count": 0,
            "critical_count": 0
        }
    
    avg_temp = sum(h.temperature for h in hives) / len(hives)
    avg_humidity = sum(h.humidity for h in hives) / len(hives)
    avg_weight = sum(h.weight for h in hives) / len(hives)
    
    healthy = len([h for h in hives if h.status == "healthy"])
    warning = len([h for h in hives if h.status == "warning"])
    critical = len([h for h in hives if h.status == "critical"])
    
    return {
        "avg_temperature": round(avg_temp, 1),
        "avg_humidity": round(avg_humidity, 1),
        "avg_weight": round(avg_weight, 1),
        "healthy_count": healthy,
        "warning_count": warning,
        "critical_count": critical
    }

@router.get("/chart")
async def get_analytics_chart(
    metric: str = "temperature",
    range: str = "7D",
    current_user_email: str = Depends(get_current_user_email)  # 
):
    """Get chart data for analytics"""
    days_map = {"7D": 7, "30D": 30, "3M": 90, "1Y": 365}
    days = days_map.get(range, 7)
    
    # Generate dates
    if days <= 7:
        dates = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][:days]
    elif days <= 30:
        dates = [f"Day {i+1}" for i in range(days)]
    else:
        dates = [f"Week {i+1}" for i in range(min(days//7, 52))]
    
    # Generate values based on metric
    if metric == "temperature":
        values = [round(random.uniform(32, 36), 1) for _ in range(len(dates))]
    elif metric == "humidity":
        values = [round(random.uniform(55, 70), 1) for _ in range(len(dates))]
    elif metric == "weight":
        values = [round(random.uniform(42, 48), 1) for _ in range(len(dates))]
    else:
        values = [0] * len(dates)
    
    return {
        "dates": dates,
        "values": values
    }

@router.get("/productivity")
async def get_productivity_chart(
    current_user_email: str = Depends(get_current_user_email)  
):
    """Get productivity comparison data"""
    hives = await HiveService.get_user_hives(current_user_email)
    
    return {
        "hives": [
            {
                "hive_id": hive.id,
                "name": hive.name,
                "productivity_score": hive.health_score
            }
            for hive in hives
        ]
    }

@router.get("/alerts/distribution")
async def get_alert_distribution(
    current_user_email: str = Depends(get_current_user_email)  # 
):
    """Get alert distribution by priority"""
    # Mock data (in production, query recommendations collection)
    return {
        "high": random.randint(2, 5),
        "medium": random.randint(3, 7),
        "low": random.randint(1, 4)
    }