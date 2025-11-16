"""
Add 5 Specific Hives to MongoDB Atlas
These are your real hive locations in Rwanda

Usage:
    cd backend
    python add_hives_to_atlas.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import random

# Atlas connection (update with your actual URL)
ATLAS_MONGODB_URL = "mongodb+srv://benaiahraini:BJT1Hrq8JTVqDGC0@asaliaspossible.075itbp.mongodb.net/?retryWrites=true&w=majority"
ATLAS_DATABASE = "asali_production"

# Your user email 
USER_EMAIL = "b.raini@alustudent.com"  # Updated

# Your 5 hives with Rwandan locations
HIVES = [
    {
        "name": "Hive Mosi",
        "location": "Nyamata",
        "latitude": -1.9403,
        "longitude": 29.8739,
        "status": "healthy",
        "temperature": 34.5,
        "humidity": 65.0,
        "weight": 45.2,
        "alerts": 0,
        "health_score": 85.0,
    },
    {
        "name": "Hive Pili",
        "location": "Nyamirambo",
        "latitude": -1.9453,
        "longitude": 29.8789,
        "status": "warning",
        "temperature": 36.8,
        "humidity": 58.0,
        "weight": 42.8,
        "alerts": 1,
        "health_score": 70.0,
    },
    {
        "name": "Hive Utat",
        "location": "Kimironko",
        "latitude": -1.9353,
        "longitude": 29.8839,
        "status": "healthy",
        "temperature": 33.2,
        "humidity": 68.0,
        "weight": 48.5,
        "alerts": 0,
        "health_score": 90.0,
    },
    {
        "name": "Hive Nne",
        "location": "Nyarutarama",
        "latitude": -1.9503,
        "longitude": 29.8689,
        "status": "critical",
        "temperature": 38.5,
        "humidity": 52.0,
        "weight": 38.2,
        "alerts": 3,
        "health_score": 45.0,
    },
    {
        "name": "Hive Tano",
        "location": "Kacyiru",
        "latitude": -1.9403,
        "longitude": 29.8789,
        "status": "healthy",
        "temperature": 34.8,
        "humidity": 64.0,
        "weight": 46.7,
        "alerts": 0,
        "health_score": 88.0,
    }
]

async def add_hives():
    """Add 5 hives to MongoDB Atlas"""
    
    print("=" * 70)
    print("ADDING 5 HIVES TO MONGODB ATLAS")
    print("=" * 70)
    
    # Connect to Atlas
    print("\n  Connecting to MongoDB Atlas...")
    try:
        client = AsyncIOMotorClient(ATLAS_MONGODB_URL)
        await client.admin.command('ping')
        db = client[ATLAS_DATABASE]
        print(f"    Connected to Atlas: {ATLAS_DATABASE}")
    except Exception as e:
        print(f"    Failed to connect: {e}")
        print("\n   Update ATLAS_MONGODB_URL in this script!")
        return
    
    hives_collection = db["hives"]
    
    # Check if user exists
    users_collection = db["users"]
    user = await users_collection.find_one({"email": USER_EMAIL})
    
    if not user:
        print(f"\n  User not found: {USER_EMAIL}")
        print("\n   Options:")
        print("   1. Update USER_EMAIL in this script")
        print("   2. Or register user at /api/auth/register first")
        return
    
    print(f"\n Found user: {USER_EMAIL}")
    
    # Check existing hives
    existing_count = await hives_collection.count_documents({"user_id": USER_EMAIL})
    print(f"\n Current hives: {existing_count}")
    
    if existing_count > 0:
        response = input(f"\n  You already have {existing_count} hive(s). Delete them? (yes/no): ")
        if response.lower() == 'yes':
            result = await hives_collection.delete_many({"user_id": USER_EMAIL})
            print(f"     Deleted {result.deleted_count} hives")
    
    # Add 5 hives
    print(f"\n Adding 5 hives...")
    print("-" * 70)
    
    now = datetime.utcnow()
    
    for i, hive_data in enumerate(HIVES, 1):
        print(f"\n{i}. {hive_data['name']} - {hive_data['location']}")
        
        # Build complete hive document
        hive_doc = {
            "name": hive_data["name"],
            "location": hive_data["location"],
            "latitude": hive_data["latitude"],
            "longitude": hive_data["longitude"],
            "user_id": USER_EMAIL,
            "status": hive_data["status"],
            "temperature": hive_data["temperature"],
            "humidity": hive_data["humidity"],
            "weight": hive_data["weight"],
            "alerts": hive_data["alerts"],
            "health_score": hive_data["health_score"],
            "last_updated": now,
            "created_at": now,
            # Default fields
            "queen_present": True,
            "swarming_probability": 0.0,
            "sound_health_status": "Normal"
        }
        
        result = await hives_collection.insert_one(hive_doc)
        hive_id = str(result.inserted_id)
        
        print(f"    Created: {hive_id}")
        print(f"    Location: {hive_data['latitude']}, {hive_data['longitude']}")
        print(f"     Temp: {hive_data['temperature']}°C |  Humidity: {hive_data['humidity']}%")
        print(f"     Weight: {hive_data['weight']}kg |   Health: {hive_data['health_score']}%")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    final_count = await hives_collection.count_documents({"user_id": USER_EMAIL})
    
    print(f"\n Successfully added 5 hives!")
    print(f"   Total hives for {USER_EMAIL}: {final_count}")
    
    # List all hives
    print(f"\n Your hives:")
    cursor = hives_collection.find({"user_id": USER_EMAIL})
    hives = await cursor.to_list(length=100)
    
    for hive in hives:
        print(f"   • {hive['name']} ({hive['location']}) - {hive['status']}")
    
    client.close()
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Restart your backend")
    print("2. Login to Flutter app")
    print("3. View your 5 hives on the map!")
    print("4. Generate demo data for any hive:")
    print("   POST /api/hives/{hive_id}/generate-demo-data")
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    asyncio.run(add_hives())