import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from config.settings import settings
from database.connection import connect_to_mongo, close_mongo_connection, init_indexes 
#from routes import auth, dashboard, hives, analytics, recommendations, harvests
#from routes import settings as settings_route


async def load_models_async():
    """Load ML models in background after server starts"""
    await asyncio.sleep(2)  # Let server start first
    
    print("\n Loading ML Models...")

    # Import services ONLY when needed
    from services.audio_service import get_audio_service
    from services.forecasting_service import get_forecasting_service
    from services.rl_service import get_rl_service
    
    try:
        get_audio_service()
        print(" Audio model loaded")
    except Exception as e:
        print(f" Audio: {e}")
    
    try:
        get_forecasting_service()
        print(" LSTM model loaded")
    except Exception as e:
        print(f" LSTM: {e}")
    
    try:
        get_rl_service()
        print(" PPO model loaded")
    except Exception as e:
        print(f" PPO: {e}")

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 60)
    print(" AsaliAsPossible API Starting...")
    print("=" * 60)
    
    # Connect to database
    await connect_to_mongo()
    
    # Initialize database indexes
    try:
        print("\n Initializing database indexes...")
        await init_indexes()
        print(" Database indexes created")
    except Exception as e:
        print(f"⚠ Index warning: {e}")
    
    print("\n API Ready - ML models loading in background...")
    
    # Load models in background AFTER server starts
    asyncio.create_task(load_models_async())
    
    yield
    
    # Shutdown
    print("\n" + "=" * 60)
    print("  Shutting down AsaliAsPossible API...")
    await close_mongo_connection()
    print("  AsaliAsPossible API Stopped")
    print("=" * 60 + "\n")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Smart Beehive Monitoring API with ML-powered insights",
    lifespan=lifespan
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Custom OpenAPI schema to show "Authorize" with Bearer Token input
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
#app.include_router(auth.router, prefix=settings.API_V1_STR)
#app.include_router(dashboard.router, prefix=settings.API_V1_STR)
#app.include_router(hives.router, prefix=settings.API_V1_STR)
#app.include_router(analytics.router, prefix=settings.API_V1_STR)
#app.include_router(recommendations.router, prefix=settings.API_V1_STR)
#app.include_router(harvests.router, prefix=settings.API_V1_STR)
#app.include_router(settings_route.router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to AsaliAsPossible API ",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "ml_models": {
            "audio": "CNN-LSTM Audio Classifier",
            "forecasting": "LSTM Time-Series (24h→6h)",
            "rl": "PPO Reinforcement Learning"
        },
        "database": {
            "name": settings.DATABASE_NAME,
            "type": "MongoDB Atlas",
            "collections": [
                "users", "hives", "hive_history",
                "audio_metadata", "forecasts", 
                "rl_training_data", "rl_episodes",
                "recommendations", "harvests", "settings"
            ]
        }
    }

# Health check endpoint
@app.get(f"{settings.API_V1_STR}/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AsaliAsPossible API",
        "version": "1.0.0",
        "ml_models_loaded": True,
        "database": "MongoDB Atlas",
        "features": {
            "audio_classification": True,
            "time_series_forecasting": True,
            "rl_recommendations": True,
            "cloud_storage": True
        }
    }

# Run with: uvicorn main:app --host 0.0.0.0 --port $PORT
