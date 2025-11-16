
from datetime import datetime
from bson import ObjectId
import gridfs
from pathlib import Path

async def save_audio_to_database(
    file_path: str,
    hive_id: str,
    user_id: str,
    classification_result: dict,
    audio_info: dict
):
    """
    Save audio file and metadata to MongoDB Atlas
    
    Args:
        file_path: Path to audio file
        hive_id: Hive ID
        user_id: User email
        classification_result: Classification output from model
        audio_info: Audio file information (duration, sample_rate, etc.)
    
    Returns:
        Document ID of saved audio metadata
    """
    from database.connection import get_gridfs_bucket, get_audio_metadata_collection
    
    # Get collections
    gridfs_bucket = get_gridfs_bucket()
    audio_collection = get_audio_metadata_collection()
    
    # Upload audio file to GridFS
    with open(file_path, 'rb') as audio_file:
        file_id = await gridfs_bucket.upload_from_stream(
            filename=Path(file_path).name,
            source=audio_file,
            metadata={
                "hive_id": hive_id,
                "user_id": user_id,
                "content_type": audio_info.get("content_type", "audio/wav"),
                "duration_seconds": audio_info.get("duration", 10.0),
                "sample_rate": audio_info.get("sample_rate", 22050)
            }
        )
    
    # Create metadata document
    audio_metadata = {
        "hive_id": hive_id,
        "user_id": user_id,
        "file_id": file_id,
        "filename": Path(file_path).name,
        "file_size_bytes": audio_info.get("file_size", 0),
        "duration_seconds": audio_info.get("duration", 10.0),
        "sample_rate": audio_info.get("sample_rate", 22050),
        "uploaded_at": datetime.utcnow(),
        
        # Classification results
        "classification": {
            "status": classification_result.get("status"),
            "confidence": classification_result.get("confidence"),
            "probabilities": classification_result.get("probabilities"),
            "queenless_risk": classification_result.get("queenless_risk"),
            "queen_present": classification_result.get("queen_present"),
            "model_version": "v1.0",
            "classified_at": datetime.utcnow(),
            "mock_mode": classification_result.get("mock_mode", False)
        },
        
        "metadata": {
            "notes": audio_info.get("notes", "")
        }
    }
    
    # Insert metadata
    result = await audio_collection.insert_one(audio_metadata)
    
    print(f"Audio saved to database: {result.inserted_id}")
    
    return str(result.inserted_id)


async def get_audio_history(hive_id: str, limit: int = 10):
    """
    Get audio classification history for a hive
    
    Args:
        hive_id: Hive ID
        limit: Number of records to return
    
    Returns:
        List of audio metadata documents
    """
    from database.connection import get_audio_metadata_collection
    
    audio_collection = get_audio_metadata_collection()
    
    cursor = audio_collection.find(
        {"hive_id": hive_id}
    ).sort("uploaded_at", -1).limit(limit)
    
    records = await cursor.to_list(length=limit)
    
    # Convert ObjectIds to strings
    for record in records:
        record["_id"] = str(record["_id"])
        record["file_id"] = str(record["file_id"])
    
    return records


async def download_audio_file(file_id: str):
    """
    Download audio file from GridFS
    
    Args:
        file_id: GridFS file ID
    
    Returns:
        File content as bytes
    """
    from database.connection import get_gridfs_bucket
    
    gridfs_bucket = get_gridfs_bucket()
    
    # Download file
    grid_out = await gridfs_bucket.open_download_stream(ObjectId(file_id))
    contents = await grid_out.read()
    
    return contents


async def get_audio_statistics(hive_id: str = None, user_id: str = None):
    """
    Get statistics about audio classifications
    
    Args:
        hive_id: Optional hive filter
        user_id: Optional user filter
    
    Returns:
        Dictionary with statistics
    """
    from database.connection import get_audio_metadata_collection
    
    audio_collection = get_audio_metadata_collection()
    
    # Build query
    query = {}
    if hive_id:
        query["hive_id"] = hive_id
    if user_id:
        query["user_id"] = user_id
    
    # Aggregation pipeline
    pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$classification.status",
                "count": {"$sum": 1},
                "avg_confidence": {"$avg": "$classification.confidence"},
                "avg_queenless_risk": {"$avg": "$classification.queenless_risk"}
            }
        }
    ]
    
    cursor = audio_collection.aggregate(pipeline)
    results = await cursor.to_list(length=100)
    
    # Format results
    stats = {
        "total_recordings": sum(r["count"] for r in results),
        "by_status": {
            r["_id"]: {
                "count": r["count"],
                "avg_confidence": round(r["avg_confidence"], 1),
                "avg_queenless_risk": round(r["avg_queenless_risk"], 1)
            }
            for r in results
        }
    }
    
    return stats