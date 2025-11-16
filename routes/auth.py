from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from models.user import UserCreate, UserLogin, GoogleLogin, AuthResponse, UserResponse
from services.auth_service import AuthService
from utils.security import decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user_email(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """Dependency to get current user email from token"""
    email = decode_access_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return email

@router.post("/register", response_model=AuthResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    return await AuthService.register_user(user_data)

@router.post("/login", response_model=AuthResponse)
async def login(user_data: UserLogin):
    """Login user"""
    return await AuthService.login_user(user_data.email, user_data.password)

@router.post("/google", response_model=AuthResponse)
async def google_login(google_data: GoogleLogin):
    """Google OAuth login (mock implementation)"""
    # verify google token with Google API
    # For just incase and testing, create a mock user
    mock_email = "google.user@gmail.com"
    mock_name = "Google User"
    
    # Try to find existing user or create new
    try:
        return await AuthService.login_user(mock_email, "google_auth_password")
    except:
        user_data = UserCreate(
            email=mock_email,
            name=mock_name,
            password="google_auth_password"
        )
        return await AuthService.register_user(user_data)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user_email: Annotated[str, Depends(get_current_user_email)]):
    """Get current user"""
    return await AuthService.get_current_user(current_user_email)

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    name: str,
    phone_number: str = None,
    current_user_email: Annotated[str, Depends(get_current_user_email)] = None
):
    """Update user profile"""
    return await AuthService.update_profile(current_user_email, name, phone_number)

@router.post("/logout")
async def logout():
    """Logout user (client-side should remove token)"""
    return {"success": True, "message": "Logged out successfully"}