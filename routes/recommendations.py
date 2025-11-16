from fastapi import APIRouter, Depends
from typing import Annotated, List, Optional
from utils.auth_utils import get_current_user_email  # ✅ CHANGED
from services.hive_service import HiveService
from services.ml_service import MLService
from models.recommendation import RecommendationResponse, RecommendationStatus
from database.connection import get_recommendations_collection
from database.mock_data import generate_mock_recommendations
from bson import ObjectId
from datetime import datetime, timedelta

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

def time_ago(dt: datetime) -> str:
    """Convert datetime to 'time ago' string"""
    delta = datetime.utcnow() - dt
    
    if delta.days > 0:
        return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

@router.get("", response_model=List[RecommendationResponse])
async def get_recommendations(
    priority: Optional[str] = None,
    hive_id: Optional[str] = None,
    limit: Optional[int] = None,
    current_user_email: str = Depends(get_current_user_email)  
):
    """Get recommendations with filters"""
    recommendations_collection = get_recommendations_collection()
    
    # Build query
    query = {
        "user_id": current_user_email,
        "status": "active"
    }
    
    if priority:
        query["priority"] = priority
    
    if hive_id:
        query["hive_id"] = hive_id
    
    # Check if we have recommendations
    count = await recommendations_collection.count_documents(query)
    
    # Generate mock data if empty
    if count == 0:
        hives = await HiveService.get_user_hives(current_user_email)
        if hives:
            hive_ids = [h.id for h in hives]
            mock_recs = generate_mock_recommendations(current_user_email, hive_ids)
            if mock_recs:
                await recommendations_collection.insert_many(mock_recs)
    
    # Fetch recommendations
    cursor = recommendations_collection.find(query).sort("created_at", -1)
    
    if limit:
        cursor = cursor.limit(limit)
    
    recs = await cursor.to_list(length=100)
    
    return [
        RecommendationResponse(
            id=str(rec["_id"]),
            user_id=rec["user_id"],
            hive_id=rec["hive_id"],
            action=rec["action"],
            reason=rec["reason"],
            priority=rec["priority"],
            status=rec["status"],
            time=time_ago(rec["created_at"]),
            created_at=rec["created_at"]
        )
        for rec in recs
    ]

@router.get("/active")
async def get_active_recommendations(
    limit: int = 3,
    current_user_email: str = Depends(get_current_user_email)  
):
    """Get active recommendations for dashboard"""
    return await get_recommendations(
        limit=limit,
        current_user_email=current_user_email
    )

@router.put("/{recommendation_id}/complete")
async def complete_recommendation(
    recommendation_id: str,
    current_user_email: str = Depends(get_current_user_email)  
):
    """Mark recommendation as completed"""
    recommendations_collection = get_recommendations_collection()
    
    result = await recommendations_collection.update_one(
        {
            "_id": ObjectId(recommendation_id),
            "user_id": current_user_email
        },
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        return {"success": False, "message": "Recommendation not found"}
    
    return {"success": True, "message": "Recommendation completed"}