from fastapi import FastAPI

app = FastAPI(
    title="Waste Route Optimizer API",
    description="AI-Enhanced Waste Collection Route Optimization - University of Buea",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Waste Route Optimizer is running",
        "project": "AI-Enhanced Waste Collection - Cameroon",
        "author": "MBARGA MBOM NOEMIE"
    }

@app.get("/health")
def health():
    return {"status": "ok"}
