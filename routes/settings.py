from fastapi import APIRouter, Depends
from typing import Annotated
from utils.auth_utils import get_current_user_email  
from models.settings import UserSettings, SettingsUpdate
from database.connection import get_settings_collection

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=UserSettings)
async def get_settings(
    current_user_email: str = Depends(get_current_user_email)  
):
    """Get user settings"""
    settings_collection = get_settings_collection()
    
    settings = await settings_collection.find_one({"user_id": current_user_email})
    
    if not settings:
        # Create default settings
        default_settings = UserSettings(
            user_id=current_user_email,
            temperature_alerts=True,
            weight_monitoring=True,
            sound_analysis=True,
            push_notifications=True,
            email_alerts=False,
            data_backup=True,
            monitoring_frequency="Every 15 minutes",
            alert_threshold="Medium and High priority"
        )
        await settings_collection.insert_one(default_settings.dict())
        return default_settings
    
    return UserSettings(**settings)

@router.put("", response_model=UserSettings)
async def update_settings(
    settings_data: SettingsUpdate,
    current_user_email: str = Depends(get_current_user_email)  
):
    """Update user settings"""
    settings_collection = get_settings_collection()
    
    await settings_collection.update_one(
        {"user_id": current_user_email},
        {"$set": settings_data.dict()},
        upsert=True
    )
    
    return await get_settings(current_user_email)

@router.post("/reset", response_model=UserSettings)
async def reset_settings(
    current_user_email: str = Depends(get_current_user_email)  
):
    """Reset settings to default"""
    settings_collection = get_settings_collection()
    
    default_settings = UserSettings(
        user_id=current_user_email,
        temperature_alerts=True,
        weight_monitoring=True,
        sound_analysis=True,
        push_notifications=True,
        email_alerts=False,
        data_backup=True,
        monitoring_frequency="Every 15 minutes",
        alert_threshold="Medium and High priority"
    )
    
    await settings_collection.replace_one(
        {"user_id": current_user_email},
        default_settings.dict(),
        upsert=True
    )
    
    return default_settings

@router.get("/export")
async def export_data(
    current_user_email: str = Depends(get_current_user_email)  
):
    """Export user data (placeholder)"""
    return {
        "message": "Export feature coming soon",
        "user": current_user_email
    }