"""
Authentication utility for API endpoints
Handles JWT token validation for all protected routes
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.security import decode_access_token

# Security scheme for JWT tokens
security = HTTPBearer()

async def get_current_user_email(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and validate user email from JWT token
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        str: User's email address from token
        
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    token = credentials.credentials
    email = decode_access_token(token)
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return email