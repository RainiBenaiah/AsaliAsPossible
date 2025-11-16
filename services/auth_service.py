# services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional
from config.settings import settings
from database.connection import get_users_collection
from models.user import UserCreate, AuthResponse, UserResponse
from utils.security import get_password_hash, verify_password, create_access_token

class AuthService:
    @staticmethod
    async def register_user(user_data: UserCreate) -> AuthResponse:
        """Register a new user"""
        users_collection = get_users_collection()

        # Check if user already exists
        existing_user = await users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise Exception("User already exists")

        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Prepare user document with proper timestamps
        now = datetime.utcnow()
        new_user = {
            "email": user_data.email,
            "name": user_data.name,
            "hashed_password": hashed_password,  #  Use hashed_password to match DB
            "phone_number": None,
            "created_at": now,  
            "updated_at": now
        }

        # Insert into DB
        result = await users_collection.insert_one(new_user)
        
        # Prepare response (remove hashed_password, add id)
        response_user = {
            "id": str(result.inserted_id),
            "email": new_user["email"],
            "name": new_user["name"],
            "phone_number": new_user["phone_number"],
            "created_at": new_user["created_at"]
        }

        # Create JWT token
        access_token = create_access_token(
            data={"sub": response_user["email"]},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**response_user)
        )

    @staticmethod
    async def login_user(email: str, password: str) -> AuthResponse:
        """Login a user and return JWT"""
        users_collection = get_users_collection()

        user = await users_collection.find_one({"email": email})
        
        if not user:
            raise Exception("Invalid credentials")

        #  Check for both 'password' and 'hashed_password' fields
        password_field = None
        if "hashed_password" in user:
            password_field = user["hashed_password"]
        elif "password" in user:
            password_field = user["password"]
        else:
            raise Exception("User account is corrupted - missing password field")
        
        # Verify password
        if not verify_password(password, password_field):
            raise Exception("Invalid credentials")

        # Create JWT token
        access_token = create_access_token(
            data={"sub": user["email"]},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # Prepare response
        response_user = {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name", ""),
            "phone_number": user.get("phone_number"),
            "created_at": user.get("created_at", datetime.utcnow())
        }

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**response_user)
        )

    @staticmethod
    async def get_current_user(email: str) -> UserResponse:
        """Fetch current user by email"""
        users_collection = get_users_collection()
        
        user = await users_collection.find_one({"email": email})
        if not user:
            raise Exception("User not found")
        
        return UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            name=user.get("name", ""),
            phone_number=user.get("phone_number"),
            created_at=user.get("created_at", datetime.utcnow())
        )

    @staticmethod
    async def update_profile(email: str, name: str, phone_number: Optional[str] = None) -> UserResponse:
        """Update user profile"""
        users_collection = get_users_collection()
        
        update_data = {
            "name": name,
            "updated_at": datetime.utcnow()
        }
        if phone_number:
            update_data["phone_number"] = phone_number

        await users_collection.update_one(
            {"email": email},
            {"$set": update_data}
        )

        user = await users_collection.find_one({"email": email})
        
        return UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            name=user.get("name", ""),
            phone_number=user.get("phone_number"),
            created_at=user.get("created_at", datetime.utcnow())
        )