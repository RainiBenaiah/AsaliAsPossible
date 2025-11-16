"""
Forecast Storage Service
Saves LSTM time series predictions to MongoDB Atlas
"""

from datetime import datetime, timedelta
from typing import List, Dict
from bson import ObjectId


async def save_forecast_to_database(
    hive_id: str,
    user_id: str,
    historical_data: List[Dict],
    predictions: Dict,
    trends: Dict,
    alerts: List[Dict]
):
    """
    Save LSTM forecast to MongoDB Atlas
    
    Args:
        hive_id: Hive ID
        user_id: User email
        historical_data: Last 24 hours of sensor data
        predictions: Forecast predictions
        trends: Trend analysis
        alerts: Generated alerts
    
    Returns:
        Document ID of saved forecast
    """
    from database.connection import get_forecasts_collection
    
    forecasts_collection = get_forecasts_collection()
    
    # Create forecast document
    forecast_doc = {
        "hive_id": hive_id,
        "user_id": user_id,
        "forecast_type": "lstm_24h",
        "created_at": datetime.utcnow(),
        
        # Historical data used for forecast
        "historical_data": [
            {
                "timestamp": reading["timestamp"] if isinstance(reading["timestamp"], datetime) 
                           else datetime.fromisoformat(reading["timestamp"]),
                "temperature": reading["temperature"],
                "humidity": reading["humidity"],
                "weight": reading["weight"]
            }
            for reading in historical_data
        ],
        
        # Predictions
        "predictions": predictions,
        
        # Analysis
        "trends": trends,
        "alerts": alerts,
        
        # Model info
        "model_info": {
            "model_version": "lstm_v1.0",
            "model_type": "CNN-LSTM",
            "training_date": datetime(2025, 11, 1),  # Update with actual training date
            "accuracy_metrics": {
                "mae": 0.5,
                "rmse": 0.8
            }
        }
    }
    
    # Insert forecast
    result = await forecasts_collection.insert_one(forecast_doc)
    
    print(f"Forecast saved to database: {result.inserted_id}")
    
    return str(result.inserted_id)


async def get_latest_forecast(hive_id: str):
    """
    Get the most recent forecast for a hive
    
    Args:
        hive_id: Hive ID
    
    Returns:
        Latest forecast document or None
    """
    from database.connection import get_forecasts_collection
    
    forecasts_collection = get_forecasts_collection()
    
    forecast = await forecasts_collection.find_one(
        {"hive_id": hive_id},
        sort=[("created_at", -1)]
    )
    
    if forecast:
        forecast["_id"] = str(forecast["_id"])
    
    return forecast


async def get_forecast_history(
    hive_id: str,
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = 30
):
    """
    Get forecast history for a hive
    
    Args:
        hive_id: Hive ID
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of forecasts to return
    
    Returns:
        List of forecast documents
    """
    from database.connection import get_forecasts_collection
    
    forecasts_collection = get_forecasts_collection()
    
    # Build query
    query = {"hive_id": hive_id}
    
    if start_date or end_date:
        query["created_at"] = {}
        if start_date:
            query["created_at"]["$gte"] = start_date
        if end_date:
            query["created_at"]["$lte"] = end_date
    
    cursor = forecasts_collection.find(query).sort("created_at", -1).limit(limit)
    
    forecasts = await cursor.to_list(length=limit)
    
    # Convert ObjectIds to strings
    for forecast in forecasts:
        forecast["_id"] = str(forecast["_id"])
    
    return forecasts


async def get_forecast_accuracy_stats(hive_id: str, days: int = 7):
    """
    Calculate forecast accuracy by comparing predictions with actual values
    
    Args:
        hive_id: Hive ID
        days: Number of days to analyze
    
    Returns:
        Dictionary with accuracy statistics
    """
    from database.connection import get_forecasts_collection, get_hive_history_collection
    
    forecasts_collection = get_forecasts_collection()
    history_collection = get_hive_history_collection()
    
    # Get forecasts from last N days
    start_date = datetime.utcnow() - timedelta(days=days)
    
    cursor = forecasts_collection.find({
        "hive_id": hive_id,
        "created_at": {"$gte": start_date}
    }).sort("created_at", 1)
    
    forecasts = await cursor.to_list(length=1000)
    
    if not forecasts:
        return {"error": "No forecasts found"}
    
    # For each forecast, compare first prediction with actual value
    errors = {
        "temperature": [],
        "humidity": [],
        "weight": []
    }
    
    for forecast in forecasts:
        if not forecast.get("predictions"):
            continue
        
        # Get first prediction (1 hour ahead)
        first_pred = forecast["predictions"][0]
        pred_time = first_pred["timestamp"]
        
        # Find actual reading closest to prediction time
        actual = await history_collection.find_one({
            "hive_id": hive_id,
            "timestamp": {
                "$gte": pred_time - timedelta(minutes=30),
                "$lte": pred_time + timedelta(minutes=30)
            }
        })
        
        if actual:
            # Calculate errors
            errors["temperature"].append(abs(first_pred["temperature"]["value"] - actual["temperature"]))
            errors["humidity"].append(abs(first_pred["humidity"]["value"] - actual["humidity"]))
            errors["weight"].append(abs(first_pred["weight"]["value"] - actual["weight"]))
    
    # Calculate statistics
    def calc_stats(error_list):
        if not error_list:
            return {"mae": 0, "rmse": 0, "count": 0}
        
        mae = sum(error_list) / len(error_list)
        rmse = (sum(e**2 for e in error_list) / len(error_list)) ** 0.5
        
        return {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "count": len(error_list)
        }
    
    stats = {
        "period_days": days,
        "total_forecasts": len(forecasts),
        "accuracy": {
            "temperature": calc_stats(errors["temperature"]),
            "humidity": calc_stats(errors["humidity"]),
            "weight": calc_stats(errors["weight"])
        }
    }
    
    return stats


async def cleanup_old_forecasts(days_to_keep: int = 30):
    """
    Remove forecasts older than specified days
    
    Args:
        days_to_keep: Number of days of forecasts to keep
    
    Returns:
        Number of forecasts deleted
    """
    from database.connection import get_forecasts_collection
    
    forecasts_collection = get_forecasts_collection()
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    result = await forecasts_collection.delete_many({
        "created_at": {"$lt": cutoff_date}
    })
    
    print(f"Cleaned up {result.deleted_count} old forecasts")
    
    return result.deleted_count