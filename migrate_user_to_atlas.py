"""
Migrate single user from local MongoDB to Atlas
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Local MongoDB
LOCAL_URL = "mongodb://localhost:27017"
LOCAL_DB = "asali_beehive_db"

# Atlas MongoDB (UPDATE THIS!)
ATLAS_URL = "mongodb+srv://benaiahraini:BJT1Hrq8JTVqDGC0@asaliaspossible.075itbp.mongodb.net/?retryWrites=true&w=majority"

ATLAS_DB = "asali_production"

# User to migrate
USER_EMAIL = "b.raini@alustudent.com"

async def migrate_user():
    """Migrate user from local to Atlas"""
    
    print("=" * 70)
    print("MIGRATING USER FROM LOCAL TO ATLAS")
    print("=" * 70)
    
    # Connect to local
    print("\n Connecting to local MongoDB...")
    local_client = AsyncIOMotorClient(LOCAL_URL)
    local_db = local_client[LOCAL_DB]
    print("   ✓ Connected to local")
    
    # Connect to Atlas
    print("\n  Connecting to MongoDB Atlas...")
    atlas_client = AsyncIOMotorClient(ATLAS_URL)
    await atlas_client.admin.command('ping')
    atlas_db = atlas_client[ATLAS_DB]
    print("   ✓ Connected to Atlas")
    
    # Get user from local
    print(f"\n👤 Finding user: {USER_EMAIL}")
    user = await local_db.users.find_one({"email": USER_EMAIL})
    
    if not user:
        print(f"    User not found in local MongoDB")
        return
    
    print(f"    Found user in local MongoDB")
    print(f"   Name: {user.get('full_name', 'N/A')}")
    print(f"   Created: {user.get('created_at', 'N/A')}")
    
    # Check if user already exists in Atlas
    existing = await atlas_db.users.find_one({"email": USER_EMAIL})
    
    if existing:
        print(f"\n  User already exists in Atlas!")
        response = input("   Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("   Migration cancelled")
            return
        
        await atlas_db.users.delete_one({"email": USER_EMAIL})
        print("     Deleted existing user from Atlas")
    
    # Copy user to Atlas
    print(f"\n  Copying user to Atlas...")
    
    # Remove _id to let Atlas generate new one
    user.pop('_id', None)
    
    result = await atlas_db.users.insert_one(user)
    
    print(f"    User migrated successfully!")
    print(f"   New ID in Atlas: {result.inserted_id}")
    
    local_client.close()
    atlas_client.close()
    
    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print(f"\n User migrated to Atlas")
    print(f"   Email: {USER_EMAIL}")
    print(f"   Password: demo1234! (unchanged)")
    print(f"\nNow you can:")
    print(f"1. Run: python add_hives_to_atlas.py")
    print(f"2. Update .env to use Atlas")
    print(f"3. Login to app with same credentials")
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    asyncio.run(migrate_user())