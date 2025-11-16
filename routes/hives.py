from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from typing import List, Optional
from utils.auth_utils import get_current_user_email
from services.hive_service import HiveService
from services.audio_service import get_audio_service
from services.forecasting_service import get_forecasting_service
from services.rl_service import get_rl_service
# NEW: Import storage services
from services.audio_storage_service import save_audio_to_database, get_audio_history
from services.forecast_storage_service import save_forecast_to_database, get_latest_forecast
from services.rl_storage_service import create_rl_episode, save_rl_step, update_rl_episode, complete_rl_episode
from models.hive import HiveCreate, HiveUpdate, HiveResponse, HiveLocation
from database.connection import (
    get_hives_collection, 
    get_hive_history_collection, 
    get_recommendations_collection,
    get_gridfs_bucket  # NEW: For audio file storage
)
from bson import ObjectId
from datetime import datetime, timedelta
import aiofiles
import os
from pathlib import Path
import numpy as np
import traceback
import soundfile as sf

router = APIRouter(prefix="/hives", tags=["Hives"])

# Create uploads directory for temporary files
UPLOAD_DIR = Path("uploads/audio")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("", response_model=HiveResponse)
async def create_hive(
    hive_data: HiveCreate,
    current_user_email: str = Depends(get_current_user_email)
):
    """Create a new hive"""
    return await HiveService.create_hive(current_user_email, hive_data)

@router.get("", response_model=List[HiveResponse])
async def get_hives(
    current_user_email: str = Depends(get_current_user_email)
):
    """Get all user's hives"""
    return await HiveService.get_user_hives(current_user_email)

@router.get("/locations", response_model=List[HiveLocation])
async def get_hive_locations(
    current_user_email: str = Depends(get_current_user_email)
):
    """Get hive locations for map view"""
    hives = await HiveService.get_user_hives(current_user_email)
    
    return [
        HiveLocation(
            id=hive.id,
            name=hive.name,
            location=hive.location,
            latitude=hive.latitude,
            longitude=hive.longitude,
            status=hive.status
        )
        for hive in hives
    ]

@router.get("/{hive_id}/detail", response_model=HiveResponse)
async def get_hive_detail(
    hive_id: str,
    current_user_email: str = Depends(get_current_user_email)
):
    """Get detailed hive information"""
    return await HiveService.get_hive_by_id(current_user_email, hive_id)

@router.get("/{hive_id}/history")
async def get_hive_history(
    hive_id: str,
    metric: str = "temperature",
    range: str = "7D",
    current_user_email: str = Depends(get_current_user_email)
):
    """Get historical data for charts"""
    return await HiveService.get_hive_history(hive_id, metric, range)

@router.put("/{hive_id}", response_model=HiveResponse)
async def update_hive(
    hive_id: str,
    hive_data: HiveUpdate,
    current_user_email: str = Depends(get_current_user_email)
):
    """Update hive information"""
    return await HiveService.update_hive(current_user_email, hive_id, hive_data)

@router.delete("/{hive_id}")
async def delete_hive(
    hive_id: str,
    current_user_email: str = Depends(get_current_user_email)
):
    """Delete a hive"""
    await HiveService.delete_hive(current_user_email, hive_id)
    return {"success": True, "message": "Hive deleted successfully"}

@router.post("/{hive_id}/historical-reading")
async def add_historical_reading(
    hive_id: str,
    temperature: float = Form(...),
    humidity: float = Form(...),
    weight: float = Form(...),
    timestamp: Optional[str] = Form(None),
    current_user_email: str = Depends(get_current_user_email)
):
    """Add a single historical reading"""
    history_collection = get_hive_history_collection()
    hives_collection = get_hives_collection()
    
    hive = await hives_collection.find_one({
        "_id": ObjectId(hive_id),
        "user_id": current_user_email
    })
    
    if not hive:
        raise HTTPException(status_code=404, detail="Hive not found")
    
    if timestamp:
        reading_time = datetime.fromisoformat(timestamp)
    else:
        reading_time = datetime.utcnow()
    
    reading = {
        "hive_id": hive_id,
        "user_id": current_user_email,
        "temperature": temperature,
        "humidity": humidity,
        "weight": weight,
        "timestamp": reading_time,
        "created_at": datetime.utcnow()
    }
    
    await history_collection.insert_one(reading)
    count = await history_collection.count_documents({"hive_id": hive_id})
    
    return {
        "success": True,
        "message": "Reading added",
        "total_readings": count,
        "needs_more": count < 24,
        "reading": {
            "temperature": temperature,
            "humidity": humidity,
            "weight": weight,
            "timestamp": reading_time.isoformat()
        }
    }

@router.get("/{hive_id}/historical-readings")
async def get_historical_readings(
    hive_id: str,
    limit: int = 24,
    current_user_email: str = Depends(get_current_user_email)
):
    """Get historical readings for a hive"""
    history_collection = get_hive_history_collection()
    
    cursor = history_collection.find({
        "hive_id": hive_id,
        "user_id": current_user_email
    }).sort("timestamp", -1).limit(limit)
    
    readings = await cursor.to_list(length=limit)
    readings.reverse()
    
    return {
        "count": len(readings),
        "readings": [
            {
                "temperature": r["temperature"],
                "humidity": r["humidity"],
                "weight": r["weight"],
                "timestamp": r["timestamp"].isoformat()
            }
            for r in readings
        ]
    }

@router.post("/{hive_id}/upload-audio")
async def upload_audio(
    hive_id: str,
    audio_file: UploadFile = File(...),
    notes: str = Form(""),
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Upload audio file for classification and save to MongoDB Atlas
    
    This endpoint:
    1. Validates the audio file
    2. Classifies it using CNN-LSTM model
    3. Saves file to GridFS
    4. Saves metadata and classification to MongoDB
    """
    hives_collection = get_hives_collection()
    file_path = None
    
    try:
        # Verify hive exists
        hive = await hives_collection.find_one({
            "_id": ObjectId(hive_id),
            "user_id": current_user_email
        })
        
        if not hive:
            raise HTTPException(status_code=404, detail="Hive not found")
        
        # Validate file extension
        allowed_extensions = ['.wav', '.mp3', '.flac']
        file_ext = Path(audio_file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file temporarily
        timestamp = datetime.utcnow().timestamp()
        safe_filename = f"{hive_id}_{timestamp}{file_ext}"
        file_path = UPLOAD_DIR / safe_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await audio_file.read()
            await f.write(content)
        
        file_size = file_path.stat().st_size
        
        # Get audio info
        try:
            audio_info_sf = sf.info(str(file_path))
            audio_info = {
                "duration": audio_info_sf.duration,
                "sample_rate": audio_info_sf.samplerate,
                "file_size": file_size,
                "content_type": audio_file.content_type or "audio/wav",
                "notes": notes
            }
        except:
            # Fallback if soundfile can't read the file
            audio_info = {
                "duration": 10.0,
                "sample_rate": 22050,
                "file_size": file_size,
                "content_type": audio_file.content_type or "audio/wav",
                "notes": notes
            }
        
        # Validate audio with audio service
        audio_service = get_audio_service()
        is_valid, message = audio_service.validate_audio_file(str(file_path))
        
        if not is_valid:
            if file_path.exists():
                os.remove(file_path)
            raise HTTPException(status_code=400, detail=message)
        
        # Classify audio with CNN-LSTM model
        print(f"🎵 Classifying audio for hive {hive_id}...")
        classification_result = audio_service.classify_audio(str(file_path))
        print(f"   Classification: {classification_result['status']} ({classification_result['confidence']}%)")
        
        # NEW: Save to MongoDB Atlas (GridFS + metadata)
        print(f" Saving audio to MongoDB Atlas...")
        audio_doc_id = await save_audio_to_database(
            file_path=str(file_path),
            hive_id=hive_id,
            user_id=current_user_email,
            classification_result=classification_result,
            audio_info=audio_info
        )
        print(f"   ✓ Saved to MongoDB: {audio_doc_id}")
        
        # Update hive with latest classification
        await hives_collection.update_one(
            {"_id": ObjectId(hive_id)},
            {
                "$set": {
                    "audio_classification": classification_result,
                    "audio_updated_at": datetime.utcnow(),
                    "audio_doc_id": audio_doc_id  # Reference to audio metadata
                }
            }
        )
        
        # Clean up temporary file (audio is now in GridFS)
        if file_path.exists():
            os.remove(file_path)
            print(f"   ✓ Temporary file cleaned up")
        
        return {
            "success": True,
            "message": "Audio classified and saved to cloud database",
            "classification": classification_result,
            "audio_doc_id": audio_doc_id,
            "file_info": {
                "filename": audio_file.filename,
                "size_bytes": file_size,
                "duration": audio_info["duration"]
            },
            "storage": {
                "location": "MongoDB Atlas GridFS",
                "metadata_collection": "audio_metadata"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        if file_path and file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{hive_id}/audio-history")
async def get_audio_classification_history(
    hive_id: str,
    limit: int = 10,
    current_user_email: str = Depends(get_current_user_email)
):
    """Get audio classification history for a hive"""
    try:
        history = await get_audio_history(hive_id, limit)
        
        return {
            "success": True,
            "hive_id": hive_id,
            "count": len(history),
            "recordings": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{hive_id}/analyze")
async def analyze_hive_complete(
    hive_id: str,
    current_user_email: str = Depends(get_current_user_email)
):
    """
    Complete ML pipeline analysis with MongoDB Atlas storage
    
    This endpoint:
    1. Gets 24h historical sensor data
    2. Runs LSTM forecasting
    3. Runs PPO RL for recommendations
    4. Saves all results to MongoDB Atlas
    """
    hives_collection = get_hives_collection()
    history_collection = get_hive_history_collection()
    recommendations_collection = get_recommendations_collection()
    
    try:
        # Get hive
        hive = await hives_collection.find_one({
            "_id": ObjectId(hive_id),
            "user_id": current_user_email
        })
        
        if not hive:
            raise HTTPException(status_code=404, detail="Hive not found")
        
        print(f"\n Analyzing hive: {hive['name']}")
        
        # Get historical data (last 24 hours)
        cursor = history_collection.find({
            "hive_id": hive_id,
            "user_id": current_user_email
        }).sort("timestamp", 1).limit(24)
        
        historical_readings = await cursor.to_list(length=24)
        
        if len(historical_readings) < 24:
            raise HTTPException(
                status_code=400,
                detail=f"Need 24 historical readings, found {len(historical_readings)}"
            )
        
        # Prepare data for forecasting
        historical_data = [
            {
                "timestamp": r["timestamp"],
                "temperature": r["temperature"],
                "humidity": r["humidity"],
                "weight": r.get("weight", 45.0)
            }
            for r in historical_readings
        ]
        
        current_sensors = {
            "temperature": hive["temperature"],
            "humidity": hive["humidity"],
            "weight": hive["weight"]
        }
        
        # Get audio classification
        audio_classification = hive.get("audio_classification", {
            "status": "active",
            "confidence": 75.0,
            "probabilities": {"active": 75.0, "inactive": 24.0, "queenless": 1.0},
            "queenless_risk": 1.0,
            "queen_present": True
        })
        
        # Run LSTM forecasting
        print(f" Running LSTM forecasting...")
        forecasting_service = get_forecasting_service()
        forecast_data = forecasting_service.predict_future(historical_data)
        print(f"   Temperature trend: {forecast_data['trends']['temperature']}")
        print(f"   Humidity trend: {forecast_data['trends']['humidity']}")
        
        # NEW: Save forecast to MongoDB Atlas
        print(f" Saving forecast to MongoDB Atlas...")
        
        # Build predictions with timestamps
        now = datetime.utcnow()
        predictions = [
            {
                "timestamp": now + timedelta(hours=i+1),
                "temperature": {
                    "value": forecast_data['forecasts']['temperature'][i],
                    "confidence_lower": forecast_data['forecasts']['temperature'][i] - 1.0,
                    "confidence_upper": forecast_data['forecasts']['temperature'][i] + 1.0
                },
                "humidity": {
                    "value": forecast_data['forecasts']['humidity'][i],
                    "confidence_lower": forecast_data['forecasts']['humidity'][i] - 3.0,
                    "confidence_upper": forecast_data['forecasts']['humidity'][i] + 3.0
                },
                "weight": {
                    "value": current_sensors['weight'],
                    "confidence_lower": current_sensors['weight'] - 0.5,
                    "confidence_upper": current_sensors['weight'] + 0.5
                }
            }
            for i in range(len(forecast_data['forecasts']['temperature']))
        ]
        
        forecast_doc_id = await save_forecast_to_database(
            hive_id=hive_id,
            user_id=current_user_email,
            historical_data=historical_data,
            predictions=predictions,
            trends=forecast_data['trends'],
            alerts=forecast_data.get('alerts', [])
        )
        print(f"   ✓ Saved to MongoDB: {forecast_doc_id}")
        
        # Weight analysis
        weight_24h_ago = historical_readings[0]["weight"]
        weight_change = current_sensors["weight"] - weight_24h_ago
        
        if weight_change > 1.0:
            weight_trend = "increasing"
        elif weight_change < -1.0:
            weight_trend = "decreasing"
        else:
            weight_trend = "stable"
        
        weight_analysis = {
            "current": current_sensors["weight"],
            "weight_24h_ago": weight_24h_ago,
            "change_24h": round(weight_change, 2),
            "trend": weight_trend
        }
        
        # Build context for RL
        health_score = hive.get("health_score", 80)
        
        context = {
            "day_of_year": now.timetuple().tm_yday,
            "hour_of_day": now.hour,
            "hours_since_action": 24,
            "health_status": 2 if health_score >= 80 else (1 if health_score >= 60 else 0)
        }
        
        # Run PPO RL for recommendation
        print(f" Running PPO RL model...")
        rl_service = get_rl_service()
        recommendation = rl_service.get_recommendation(
            current_sensors,
            audio_classification,
            forecast_data,
            context
        )
        print(f"   Action: {recommendation['action']} (Priority: {recommendation['priority']})")
        
        #  Create RL episode and save step to MongoDB Atlas
        print(f" Saving RL data to MongoDB Atlas...")
        episode_id = await create_rl_episode(hive_id, current_user_email)
        
        # Build state for RL
        state = {
            **current_sensors,
            "audio_status": audio_classification.get("status"),
            "queenless_risk": audio_classification.get("queenless_risk"),
            "temp_forecast_6h": forecast_data['forecasts']['temperature'][5] if len(forecast_data['forecasts']['temperature']) > 5 else current_sensors["temperature"],
            "humidity_forecast_6h": forecast_data['forecasts']['humidity'][5] if len(forecast_data['forecasts']['humidity']) > 5 else current_sensors["humidity"],
            "weight_forecast_6h": current_sensors["weight"],
            **context
        }
        
        # Calculate reward (simplified - in production, this would be based on actual outcome)
        reward = 0.5 if health_score >= 80 else (0.2 if health_score >= 60 else 0.0)
        
        await save_rl_step(
            episode_id=episode_id,
            hive_id=hive_id,
            user_id=current_user_email,
            state=state,
            action=recommendation['action'],
            action_encoded=recommendation.get('action_index', 0),
            reward=reward,
            reward_components={
                "health_reward": 0.3 if health_score >= 80 else 0.1,
                "production_reward": 0.2 if weight_trend == "increasing" else 0.0,
                "efficiency_penalty": 0.0
            },
            next_state=state,  # Will be updated with actual next state later
            done=False,
            step=1,
            value_estimate=None,
            action_log_prob=None,
            advantage=None
        )
        print(f"    Saved RL episode: {episode_id}")
        
        recommendations = [recommendation]
        
        # Save recommendations
        for rec in recommendations:
            await recommendations_collection.insert_one({
                "hive_id": hive_id,
                "user_id": current_user_email,
                "action": rec["action"],
                "reason": rec["reason"],
                "priority": rec["priority"],
                "status": "active",
                "created_at": now
            })
        
        # Update hive with latest analysis
        await hives_collection.update_one(
            {"_id": ObjectId(hive_id)},
            {
                "$set": {
                    "last_updated": now,
                    "last_analysis": now,
                    "audio_classification": audio_classification,
                    "forecast_data": forecast_data,
                    "forecast_doc_id": forecast_doc_id,  # Reference to forecast
                    "weight_analysis": weight_analysis,
                    "health_score": health_score,
                    "rl_episode_id": episode_id  # Reference to RL episode
                }
            }
        )
        
        print(f" Analysis complete!\n")
        
        return {
            "success": True,
            "hive_id": hive_id,
            "hive_name": hive["name"],
            "analysis_timestamp": now.isoformat(),
            "current_sensors": current_sensors,
            "audio_classification": audio_classification,
            "forecasts": forecast_data,
            "forecast_doc_id": forecast_doc_id,  
            "weight_analysis": weight_analysis,
            "health_score": health_score,
            "recommendations": recommendations,
            "rl_episode_id": episode_id,  
            "storage": {  
                "forecast_saved": True,
                "rl_data_saved": True,
                "location": "MongoDB Atlas"
            },
            "summary": {
                "status": hive["status"],
                "queen_present": audio_classification.get("queen_present", True),
                "temperature_trend": forecast_data["trends"]["temperature"],
                "humidity_trend": forecast_data["trends"]["humidity"],
                "weight_trend": weight_trend,
                "action_needed": len(recommendations) > 0,
                "priority_actions": len([r for r in recommendations if r["priority"] in ["high", "critical"]])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{hive_id}/generate-demo-data")
async def generate_demo_data(
    hive_id: str,
    current_user_email: str = Depends(get_current_user_email)
):
    """Generate demo data for testing"""
    import random
    hives_collection = get_hives_collection()
    history_collection = get_hive_history_collection()
    
    hive = await hives_collection.find_one({
        "_id": ObjectId(hive_id),
        "user_id": current_user_email
    })
    
    if not hive:
        raise HTTPException(status_code=404, detail="Hive not found")
    
    now = datetime.utcnow()
    historical_readings = []
    
    # Generate 24 hours of data
    for hour in range(24, 0, -1):
        timestamp = now - timedelta(hours=hour)
        reading = {
            "hive_id": hive_id,
            "user_id": current_user_email,
            "temperature": round(random.uniform(32, 36), 1),
            "humidity": round(random.uniform(55, 70), 1),
            "weight": round(random.uniform(42, 48), 1),
            "timestamp": timestamp,
            "created_at": now,
            "demo": True
        }
        historical_readings.append(reading)
    
    # Delete old demo data
    await history_collection.delete_many({"hive_id": hive_id, "demo": True})
    
    # Insert new demo data
    await history_collection.insert_many(historical_readings)
    
    # Update hive with latest values
    latest = historical_readings[-1]
    await hives_collection.update_one(
        {"_id": ObjectId(hive_id)},
        {
            "$set": {
                "temperature": latest["temperature"],
                "humidity": latest["humidity"],
                "weight": latest["weight"],
                "last_updated": now
            }
        }
    )
    
    # Run analysis
    print(f" Generated demo data, running analysis...")
    analysis_result = await analyze_hive_complete(hive_id, current_user_email)
    
    return {
        "success": True,
        "message": "Demo data generated and analysis complete",
        "readings_created": 24,
        "analysis": analysis_result
    }