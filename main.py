"""
ABSOLUTE MINIMAL VERSION - Zero dependencies test
If this doesn't work, there's a fundamental infrastructure issue
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "alive"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.head("/")
def root_head():
    return {}

@app.head("/health")
def health_head():
    return {}