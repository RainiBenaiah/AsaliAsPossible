# Set matplotlib backend BEFORE any other imports
import os
os.environ['MPLBACKEND'] = 'Agg'

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import settings carefully
try:
    from config.settings import settings
    SETTINGS_LOADED = True
except Exception as e:
    print(f" Settings import failed: {e}")
    SETTINGS_LOADED = False
    # Create minimal settings fallback
    class FallbackSettings:
        PROJECT_NAME = "AsaliAsPossible API"
        API_V1_STR = "/api"
        BACKEND_CORS_ORIGINS = []
    settings = FallbackSettings()

# Lifespan with isolated error handling
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 60)
    print("🐝 AsaliAsPossible API Starting...")
    print("=" * 60)
    
    # Try database connection (non-blocking, isolated)
    db_connected = False
    try:
        from database.connection import connect_to_mongo, init_indexes
        print("🔌 Connecting to MongoDB...")
        await asyncio.wait_for(connect_to_mongo(), timeout=10.0)
        db_connected = True
        print(" MongoDB connected")
        
        # Try indexes with separate timeout
        try:
            await asyncio.wait_for(init_indexes(), timeout=5.0)
            print(" Indexes created")
        except Exception as e:
            print(f" Indexes skipped: {e}")
    except Exception as e:
        print(f" MongoDB skipped: {e}")
    
    print(" API Ready!")
    
    # Load ML models in background (fire and forget)
    async def load_models():
        await asyncio.sleep(10)  # Wait longer before loading
        print("\n Loading ML models...")
        
        try:
            from services.audio_service import get_audio_service
            get_audio_service()
            print(" Audio model loaded")
        except Exception as e:
            print(f" Audio: {e}")
        
        try:
            from services.forecasting_service import get_forecasting_service
            get_forecasting_service()
            print(" LSTM loaded")
        except Exception as e:
            print(f" LSTM: {e}")
        
        try:
            from services.rl_service import get_rl_service
            get_rl_service()
            print(" PPO loaded")
        except Exception as e:
            print(f" PPO: {e}")
    
    # Start model loading task (don't await it)
    asyncio.create_task(load_models())
    
    yield
    
    # Shutdown
    print("\n Shutting down...")
    if db_connected:
        try:
            from database.connection import close_mongo_connection
            await close_mongo_connection()
        except:
            pass

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME if SETTINGS_LOADED else "AsaliAsPossible API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic endpoints (always work)
@app.get("/")
@app.head("/")
async def root():
    return {
        "message": "AsaliAsPossible API 🐝",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "docs": "/docs"
        }
    }

@app.get("/api/health")
@app.head("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "AsaliAsPossible API",
        "version": "1.0.0"
    }

# Include routers - Now safe with lazy imports in hives.py
try:
    from routes import auth, dashboard, hives, analytics, recommendations, harvests
    from routes import settings as settings_route
    
    api_prefix = settings.API_V1_STR if SETTINGS_LOADED else "/api"
    
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(dashboard.router, prefix=api_prefix)
    app.include_router(hives.router, prefix=api_prefix)
    app.include_router(analytics.router, prefix=api_prefix)
    app.include_router(recommendations.router, prefix=api_prefix)
    app.include_router(harvests.router, prefix=api_prefix)
    app.include_router(settings_route.router, prefix=api_prefix)
    
    print(" All routes loaded")
except Exception as e:
    print(f" Routes not loaded: {e}")
    print("   API will run with basic endpoints only")