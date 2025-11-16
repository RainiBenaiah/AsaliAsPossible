from fastapi import APIRouter, Depends
from typing import Annotated
from utils.auth_utils import get_current_user_email  # ADDED
from services.hive_service import HiveService
from database.mock_data import generate_mock_history
import random

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
async def get_dashboard_summary(
    current_user_email: str = Depends(get_current_user_email)  # ADDED
):
    """Get dashboard summary statistics"""
    # Get user's hives
    hives = await HiveService.get_user_hives(current_user_email)
    
    # Calculate statistics
    healthy_count = len([h for h in hives if h.status == "healthy"])
    warning_count = len([h for h in hives if h.status == "warning"])
    critical_count = len([h for h in hives if h.status == "critical"])
    alert_count = sum(h.alerts for h in hives)
    
    # Mock weather data (in production, call weather API)
    weather = {
        "temperature": round(random.uniform(25, 30), 1),
        "humidity": round(random.uniform(60, 70)),
        "wind_speed": round(random.uniform(10, 15), 1)
    }
    
    return {
        "stats": {
            "healthy_count": healthy_count,
            "warning_count": warning_count,
            "alert_count": alert_count,
            "total_hives": len(hives)
        },
        "weather": weather
    }

@router.get("/chart")
async def get_dashboard_chart(
    days: int = 7,
    current_user_email: str = Depends(get_current_user_email) # added
):
    """Get chart data for dashboard"""
    # Mock data for 7 days
    dates = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][:days]
    
    # Generate realistic data
    healthy = [random.randint(3, 6) for _ in range(days)]
    warning = [random.randint(1, 3) for _ in range(days)]
    
    return {
        "dates": dates,
        "healthy": healthy,
        "warning": warning
    }