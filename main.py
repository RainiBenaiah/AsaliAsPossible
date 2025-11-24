# ============================================================
# ENVIRONMENT SETUP - MUST BE FIRST!
# ============================================================
import os

#  Force CPU-only mode (silences CUDA errors on Render)
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

#  Set matplotlib backend to non-interactive (required for server)
os.environ['MPLBACKEND'] = 'Agg'

import asyncio
import threading
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


# ============================================================
# BACKGROUND MODEL LOADING (After Server Starts)
# ============================================================
def load_models_in_background():
    """
    Pre-load ML models in background thread after server starts.
    This makes first API calls faster while not delaying startup.
    """
    import time
    time.sleep(5)  # Wait 5 seconds after server starts
    
    try:
        print("\n" + "=" * 60)
        print(" BACKGROUND MODEL LOADING STARTED")
        print("=" * 60)
        
        # Load Audio Service (CNN-LSTM)
        try:
            print(" Loading Audio Classification Model (CNN-LSTM)...")
            from services.audio_service import get_audio_service
            audio_service = get_audio_service()
            print(" Audio model loaded and cached")
        except Exception as e:
            print(f" Audio model loading failed: {e}")
        
        # Load Forecasting Service (LSTM)
        try:
            print(" Loading Forecasting Model (LSTM)...")
            from services.forecasting_service import get_forecasting_service
            forecasting_service = get_forecasting_service()
            print(" Forecasting model loaded and cached")
        except Exception as e:
            print(f" Forecasting model loading failed: {e}")
        
        # Load RL Service (PPO)
        try:
            print(" Loading Reinforcement Learning Model (PPO)...")
            from services.rl_service import get_rl_service
            rl_service = get_rl_service()
            print(" RL model loaded and cached")
        except Exception as e:
            print(f" RL model loading failed: {e}")
        
        print("=" * 60)
        print("🎉 ALL MODELS LOADED - First API calls will be FAST!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f" Background model loading error: {e}")


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
    print(" Starting background model loading (won't delay requests)...")
    print("=" * 60)
    
    #  Start background model loading (non-blocking!)
    model_loading_thread = threading.Thread(
        target=load_models_in_background,
        daemon=True  # Thread dies when main process exits
    )
    model_loading_thread.start()
    
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