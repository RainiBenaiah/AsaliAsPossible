from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str
    DATABASE_NAME: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10050080 # more than 7 days
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "AsaliAsPossible API"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    # Weather
    OPENWEATHER_API_KEY: str = ""
    
    # ML Models
    ML_MODELS_PATH: str = "./ml_models"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()