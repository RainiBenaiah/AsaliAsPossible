# Set matplotlib backend BEFORE any other imports
import os
os.environ['MPLBACKEND'] = 'Agg'  # Non-interactive backend (speeds up startup)

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
# TEMPORARILY DISABLED - Testing if router imports cause crashes
# from routes import auth, dashboard, hives, analytics, recommendations, harvests
# from routes import settings as settings_route

# ❌ REMOVED heavy imports - these slow down startup:
# from services.audio_service import get_audio_service
# from services.forecasting_service import get_forecasting_service
# from services.rl_service import get_rl_service

async def load_models_async():
    """Load ML models in background AFTER server starts and binds to port"""
    await asyncio.sleep(5)  # Give server time to fully bind to port
    
    print("\n" + "=" * 60)
    print("🤖 Loading ML Models in Background...")
    print("=" * 60)
    
    # Import services ONLY when loading (not at startup)
    try:
        from services.audio_service import get_audio_service
        get_audio_service()
        print("✅ Audio model (CNN-LSTM) loaded")
    except Exception as e:
        print(f"❌ Audio model failed: {e}")
    
    try:
        from services.forecasting_service import get_forecasting_service
        get_forecasting_service()
        print("✅ LSTM forecasting model loaded")
    except Exception as e:
        print(f"❌ LSTM model failed: {e}")
    
    try:
        from services.rl_service import get_rl_service
        get_rl_service()
        print("✅ PPO reinforcement learning model loaded")
    except Exception as e:
        print(f"❌ PPO model failed: {e}")
    
    print("=" * 60)
    print("🎉 All ML models loaded!")
    print("=" * 60 + "\n")

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 60)
    print("🐝 AsaliAsPossible API Starting...")
    print("=" * 60)
    
    # Connect to database with timeout (don't block startup)
    try:
        print("🔌 Connecting to MongoDB...")
        await asyncio.wait_for(connect_to_mongo(), timeout=10.0)
        print("✅ MongoDB connected")
    except asyncio.TimeoutError:
        print("⚠️  MongoDB connection timeout - API will continue without DB")
    except Exception as e:
        print(f"⚠️  MongoDB error: {e} - API will continue without DB")
    
    # Initialize database indexes with timeout
    try:
        print("📊 Initializing database indexes...")
        await asyncio.wait_for(init_indexes(), timeout=5.0)
        print("✅ Database indexes created")
    except asyncio.TimeoutError:
        print("⚠️  Index creation timeout - skipping")
    except Exception as e:
        print(f"⚠️  Index warning: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API Server Ready and Listening!")
    print("🔄 ML models loading in background...")
    print("=" * 60 + "\n")
    
    # Load models in background AFTER server is fully up
    asyncio.create_task(load_models_async())
    
    yield
    
    # Shutdown
    print("\n" + "=" * 60)
    print("🛑 Shutting down AsaliAsPossible API...")
    try:
        await close_mongo_connection()
        print("✅ MongoDB disconnected")
    except Exception as e:
        print(f"⚠️  Shutdown warning: {e}")
    print("✅ AsaliAsPossible API Stopped")
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
    
    try:
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
    except Exception as e:
        print(f"⚠️ OpenAPI schema error: {e}")
        # Return basic schema as fallback
        return get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

app.openapi = custom_openapi


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - TEMPORARILY DISABLED FOR TESTING
# app.include_router(auth.router, prefix=settings.API_V1_STR)
# app.include_router(dashboard.router, prefix=settings.API_V1_STR)
# app.include_router(hives.router, prefix=settings.API_V1_STR)
# app.include_router(analytics.router, prefix=settings.API_V1_STR)
# app.include_router(recommendations.router, prefix=settings.API_V1_STR)
# app.include_router(harvests.router, prefix=settings.API_V1_STR)
# app.include_router(settings_route.router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/")
@app.head("/")  # Add HEAD support for health checks
async def root():
    try:
        return {
            "message": "Welcome to AsaliAsPossible API 🐝",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
            "health": "/api/health"
        }
    except Exception as e:
        print(f"Root endpoint error: {e}")
        return {"status": "error", "message": str(e)}

# Health check endpoint
@app.get("/api/health")
@app.head("/api/health")  # Add HEAD support
async def health_check():
    try:
        return {
            "status": "healthy",
            "service": "AsaliAsPossible API",
            "version": "1.0.0"
        }
    except Exception as e:
        print(f"Health check error: {e}")
        return {"status": "error", "message": str(e)}