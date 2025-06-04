from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api.routes import router
import os
from pathlib import Path

# FastAPI App erstellen
app = FastAPI(
    title="RadioX Backend API",
    description="Backend für RadioX AI Radio mit MP3-Streaming und Cover-Art",
    version="1.0.0"
)

# CORS-Middleware für Frontend-Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API-Routen einbinden
app.include_router(router)

# Statische Dateien für Output-Ordner
OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"
if OUTPUT_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(OUTPUT_DIR)), name="static")

@app.get("/")
async def root():
    """Root-Endpoint mit API-Info"""
    return {
        "message": "RadioX Backend API",
        "version": "1.0.0",
        "endpoints": {
            "latest_broadcast": "/api/latest-broadcast",
            "audio_files": "/api/audio/{filename}",
            "cover_images": "/api/cover/{filename}",
            "all_broadcasts": "/api/broadcasts"
        }
    }

@app.get("/health")
async def health_check():
    """Health-Check Endpoint"""
    return {"status": "healthy", "service": "RadioX Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 