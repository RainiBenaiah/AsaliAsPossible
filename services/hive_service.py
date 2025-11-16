from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from bson import ObjectId
from models.hive import HiveCreate, HiveUpdate, HiveResponse, HiveStatus
from database.connection import get_hives_collection, get_hive_history_collection
from database.mock_data import generate_mock_history
import random

class HiveService:
    
    @staticmethod
    async def create_hive(user_id: str, hive_data: HiveCreate) -> HiveResponse:
        """Create a new hive"""
        hives_collection = get_hives_collection()
        
        hive_dict = {
            "name": hive_data.name,
            "location": hive_data.location,
            "latitude": hive_data.latitude,
            "longitude": hive_data.longitude,
            "user_id": user_id,
            "status": HiveStatus.HEALTHY,
            "temperature": random.uniform(32, 35),
            "humidity": random.uniform(55, 65),
            "weight": random.uniform(42, 48),
            "alerts": 0,
            "health_score": 85.0,
            "last_updated": datetime.utcnow(),
            "queen_present": True,
            "swarming_probability": 0.0,
            "sound_health_status": "Normal",
            "created_at": datetime.utcnow(),
        }
        
        result = await hives_collection.insert_one(hive_dict)
        hive_dict["_id"] = str(result.inserted_id)
        
        return HiveResponse(
            id=str(result.inserted_id),
            user_id=user_id,
            **{k: v for k, v in hive_dict.items() if k not in ['_id', 'user_id', 'created_at']}
        )
    
    @staticmethod
    async def get_user_hives(user_id: str) -> List[HiveResponse]:
        """Get all hives for a user"""
        hives_collection = get_hives_collection()
        
        cursor = hives_collection.find({"user_id": user_id})
        hives = await cursor.to_list(length=100)
        
        return [
            HiveResponse(
                id=str(hive["_id"]),
                user_id=hive["user_id"],
                name=hive["name"],
                location=hive["location"],
                latitude=hive["latitude"],
                longitude=hive["longitude"],
                status=hive["status"],
                temperature=hive["temperature"],
                humidity=hive["humidity"],
                weight=hive["weight"],
                alerts=hive["alerts"],
                health_score=hive["health_score"],
                last_updated=hive["last_updated"],
                queen_present=hive.get("queen_present", True),
                swarming_probability=hive.get("swarming_probability", 0.0),
                sound_health_status=hive.get("sound_health_status", "Normal"),
            )
            for hive in hives
        ]
    
    @staticmethod
    async def get_hive_by_id(user_id: str, hive_id: str) -> HiveResponse:
        """Get a specific hive"""
        hives_collection = get_hives_collection()
        
        try:
            hive = await hives_collection.find_one({
                "_id": ObjectId(hive_id),
                "user_id": user_id
            })
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hive not found"
            )
        
        if not hive:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hive not found"
            )
        
        return HiveResponse(
            id=str(hive["_id"]),
            user_id=hive["user_id"],
            name=hive["name"],
            location=hive["location"],
            latitude=hive["latitude"],
            longitude=hive["longitude"],
            status=hive["status"],
            temperature=hive["temperature"],
            humidity=hive["humidity"],
            weight=hive["weight"],
            alerts=hive["alerts"],
            health_score=hive["health_score"],
            last_updated=hive["last_updated"],
            queen_present=hive.get("queen_present", True),
            swarming_probability=hive.get("swarming_probability", 0.0),
            sound_health_status=hive.get("sound_health_status", "Normal"),
        )
    
    @staticmethod
    async def update_hive(user_id: str, hive_id: str, hive_data: HiveUpdate) -> HiveResponse:
        """Update a hive"""
        hives_collection = get_hives_collection()
        
        update_dict = {k: v for k, v in hive_data.dict(exclude_unset=True).items()}
        update_dict["last_updated"] = datetime.utcnow()
        
        try:
            result = await hives_collection.update_one(
                {"_id": ObjectId(hive_id), "user_id": user_id},
                {"$set": update_dict}
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hive not found"
            )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hive not found"
            )
        
        return await HiveService.get_hive_by_id(user_id, hive_id)
    
    @staticmethod
    async def delete_hive(user_id: str, hive_id: str) -> bool:
        """Delete a hive"""
        hives_collection = get_hives_collection()
        
        try:
            result = await hives_collection.delete_one({
                "_id": ObjectId(hive_id),
                "user_id": user_id
            })
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hive not found"
            )
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hive not found"
            )
        
        return True
    
    @staticmethod
    async def get_hive_history(hive_id: str, metric: str, range_param: str):
        """Get historical data for a hive"""
        history_collection = get_hive_history_collection()
        
        # Parse range
        days_map = {
            "7D": 7,
            "30D": 30,
            "3M": 90,
            "1Y": 365
        }
        days = days_map.get(range_param, 7)
        
        # Check if we have historical data
        count = await history_collection.count_documents({"hive_id": hive_id})
        
        if count == 0:
            # Generate mock data
            mock_history = generate_mock_history(hive_id, days)
            if mock_history:
                await history_collection.insert_many(mock_history)
        
        # Fetch data
        start_date = datetime.utcnow() - timedelta(days=days)
        cursor = history_collection.find({
            "hive_id": hive_id,
            "date": {"$gte": start_date}
        }).sort("date", 1)
        
        history = await cursor.to_list(length=days)
        
        # Format response
        data = []
        for entry in history:
            day_label = entry["date"].strftime("%a")  # Mon, Tue, etc.
            value = entry.get(metric, 0)
            data.append({
                "day": day_label,
                "value": round(value, 2)
            })
        
        return {
            "metric": metric,
            "range": range_param,
            "data": data
        }
