# MINIMAL DIAGNOSTIC VERSION - Test if server starts without ML models
import os
os.environ['MPLBACKEND'] = 'Agg'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AsaliAsPossible API - Diagnostic Mode")

# Minimal CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "Diagnostic mode - server started successfully!",
        "note": "ML models and routes disabled for testing"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "mode": "diagnostic"}

# To run: uvicorn main:app --host 0.0.0.0 --port $PORT