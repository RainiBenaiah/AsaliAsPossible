from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from config.settings import settings

class Database:
    client: AsyncIOMotorClient = None
    gridfs_bucket: AsyncIOMotorGridFSBucket = None
    
db = Database()

async def connect_to_mongo():
    """Connect to MongoDB Atlas"""
    print("Connecting to MongoDB Atlas...")
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Test connection
    await db.client.admin.command('ping')
    
    # Initialize GridFS bucket for audio files
    database = db.client[settings.DATABASE_NAME]
    db.gridfs_bucket = AsyncIOMotorGridFSBucket(database, bucket_name="audio_files")
    
    print(f" Connected to MongoDB Atlas: {settings.DATABASE_NAME}")
    print(f" GridFS bucket initialized: audio_files")

async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        print("✓ Closed MongoDB connection")

def get_database():
    """Get database instance"""
    return db.client[settings.DATABASE_NAME]

def get_gridfs_bucket():
    """Get GridFS bucket for large file storage (audio files)"""
    return db.gridfs_bucket

# ============================================================================
# EXISTING COLLECTIONS
# ============================================================================

def get_users_collection():
    """User accounts collection"""
    return get_database()["users"]

def get_hives_collection():
    """Hive information collection"""
    return get_database()["hives"]

def get_hive_history_collection():
    """Historical sensor readings collection"""
    return get_database()["hive_history"]

def get_recommendations_collection():
    """Action recommendations collection"""
    return get_database()["recommendations"]

def get_harvests_collection():
    """Honey harvest records collection"""
    return get_database()["harvests"]

def get_settings_collection():
    """User settings collection"""
    return get_database()["settings"]

# ============================================================================
#  ML DATA COLLECTIONS
# ============================================================================

def get_audio_metadata_collection():
    """
    Audio file metadata and classification results
    
    Stores:
    - Audio file reference (GridFS file_id)
    - Classification results (status, confidence, probabilities)
    - Upload timestamp
    - Hive and user associations
    """
    return get_database()["audio_metadata"]

def get_forecasts_collection():
    """
    Time series forecasts from LSTM model
    
    Stores:
    - Historical data used for forecast
    - 24-hour predictions (temperature, humidity, weight)
    - Trend analysis
    - Generated alerts
    - Model version info
    """
    return get_database()["forecasts"]

def get_rl_training_collection():
    """
    PPO RL training data (state-action-reward tuples)
    
    Stores:
    - State observations
    - Actions taken
    - Rewards received
    - Next states
    - PPO-specific data (value estimates, log probs, advantages)
    """
    return get_database()["rl_training_data"]

def get_rl_episodes_collection():
    """
    PPO RL episode summaries
    
    Stores:
    - Episode metadata
    - Total rewards
    - Action counts
    - Health progression
    - Training metrics
    """
    return get_database()["rl_episodes"]

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

async def init_indexes():
    """
    Create indexes for better query performance
    Call this once during application startup
    """
    
    # Audio metadata indexes
    audio_collection = get_audio_metadata_collection()
    await audio_collection.create_index([("hive_id", 1), ("uploaded_at", -1)])
    await audio_collection.create_index([("user_id", 1), ("uploaded_at", -1)])
    await audio_collection.create_index([("classification.status", 1)])
    await audio_collection.create_index([("classification.queenless_risk", 1)])
    
    # Forecasts indexes
    forecasts_collection = get_forecasts_collection()
    await forecasts_collection.create_index([("hive_id", 1), ("created_at", -1)])
    await forecasts_collection.create_index([("user_id", 1), ("created_at", -1)])
    await forecasts_collection.create_index([("created_at", -1)])
    
    # RL training data indexes
    rl_training_collection = get_rl_training_collection()
    await rl_training_collection.create_index([("episode_id", 1), ("episode_step", 1)])
    await rl_training_collection.create_index([("hive_id", 1), ("timestamp", -1)])
    await rl_training_collection.create_index([("timestamp", -1)])
    
    # RL episodes indexes
    rl_episodes_collection = get_rl_episodes_collection()
    await rl_episodes_collection.create_index([("hive_id", 1), ("started_at", -1)])
    await rl_episodes_collection.create_index([("started_at", -1)])
    await rl_episodes_collection.create_index([("total_reward", -1)])
    
    # Existing hive history index (if not already created)
    hive_history_collection = get_hive_history_collection()
    await hive_history_collection.create_index([("hive_id", 1), ("timestamp", -1)])
    
    print(" Database indexes created")