from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="Waste Route Optimizer API",
    description="AI-Enhanced Waste Collection - University of Buea",
    version="1.0.0"
)

# Allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Waste Route Optimizer API is running",
        "docs"   : "/docs",
        "author" : "MBARGA MBOM NOEMIE - University of Buea"
    }

@app.get("/health")
def health():
    return {"status": "ok"}