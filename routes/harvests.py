from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from utils.auth_utils import get_current_user_email  #
from services.hive_service import HiveService
from models.harvest import HarvestCreate, HarvestResponse, HarvestSummary
from database.connection import get_harvests_collection
from database.mock_data import generate_mock_harvests
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/harvests", tags=["Harvests"])

@router.get("/summary", response_model=HarvestSummary)
async def get_harvest_summary(
    current_user_email: str = Depends(get_current_user_email)  #
):
    """Get harvest summary statistics"""
    harvests_collection = get_harvests_collection()
    
    # Check if we have harvests
    count = await harvests_collection.count_documents({"user_id": current_user_email})
    
    # Generate mock data if empty
    if count == 0:
        hives = await HiveService.get_user_hives(current_user_email)
        if hives:
            hive_ids = [h.id for h in hives]
            hive_names = [h.name for h in hives]
            mock_harvests = generate_mock_harvests(current_user_email, hive_ids, hive_names)
            if mock_harvests:
                await harvests_collection.insert_many(mock_harvests)
    
    # Calculate summary
    cursor = harvests_collection.find({"user_id": current_user_email})
    harvests = await cursor.to_list(length=1000)
    
    total_kg = sum(h["amount_kg"] for h in harvests)
    count = len(harvests)
    
    return HarvestSummary(
        total_harvest_kg=round(total_kg, 1),
        harvest_count=count,
        period="this_year"
    )

@router.get("/chart")
async def get_harvest_chart(
    period: str = "6_months",
    current_user_email: str = Depends(get_current_user_email)  #
):
    """Get harvest chart data"""
    harvests_collection = get_harvests_collection()
    
    # Get harvests
    cursor = harvests_collection.find({"user_id": current_user_email}).sort("date", 1)
    harvests = await cursor.to_list(length=1000)
    
    # Group by month
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    amounts = []
    
    for month_idx in range(6):
        month_total = sum(
            h["amount_kg"] for h in harvests
            if h["date"].month == month_idx + 1
        )
        amounts.append(round(month_total, 1) if month_total > 0 else 0)
    
    # Fill with mock data if empty
    if sum(amounts) == 0:
        amounts = [15, 18, 22, 25, 20, 27.5]
    
    return {
        "months": months,
        "amounts": amounts
    }

@router.get("", response_model=List[HarvestResponse])
async def get_harvests(
    filter: str = "all",
    current_user_email: str = Depends(get_current_user_email)  # 
):
    """Get harvest history"""
    harvests_collection = get_harvests_collection()
    
    query = {"user_id": current_user_email}
    
    # Apply filter
    if filter == "month":
        query["date"] = {
            "$gte": datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        }
    elif filter == "year":
        query["date"] = {
            "$gte": datetime.utcnow().replace(month=1, day=1, hour=0, minute=0, second=0)
        }
    
    cursor = harvests_collection.find(query).sort("date", -1).limit(50)
    harvests = await cursor.to_list(length=50)
    
    return [
        HarvestResponse(
            id=str(h["_id"]),
            user_id=h["user_id"],
            hive_id=h["hive_id"],
            hive_name=h["hive_name"],
            amount_kg=h["amount_kg"],
            quality=h["quality"],
            date=h["date"],
            harvester_name=h["harvester_name"],
            notes=h.get("notes"),
            created_at=h["created_at"]
        )
        for h in harvests
    ]

@router.post("", response_model=HarvestResponse, status_code=status.HTTP_201_CREATED)
async def create_harvest(
    harvest_data: HarvestCreate,
    current_user_email: str = Depends(get_current_user_email)  
):
    """Record a new harvest"""
    harvests_collection = get_harvests_collection()
    
    # Get hive info
    hive = await HiveService.get_hive_by_id(current_user_email, harvest_data.hive_id)
    
    harvest_dict = {
        "user_id": current_user_email,
        "hive_id": harvest_data.hive_id,
        "hive_name": hive.name,
        "amount_kg": harvest_data.amount_kg,
        "quality": harvest_data.quality,
        "date": harvest_data.date,
        "harvester_name": "Current User",  # In production, get from user profile
        "notes": harvest_data.notes,
        "created_at": datetime.utcnow()
    }
    
    result = await harvests_collection.insert_one(harvest_dict)
    harvest_dict["_id"] = str(result.inserted_id)
    
    return HarvestResponse(
        id=str(result.inserted_id),
        user_id=current_user_email,
        hive_id=harvest_data.hive_id,
        hive_name=hive.name,
        amount_kg=harvest_data.amount_kg,
        quality=harvest_data.quality,
        date=harvest_data.date,
        harvester_name="Current User",
        notes=harvest_data.notes,
        created_at=harvest_dict["created_at"]
    )