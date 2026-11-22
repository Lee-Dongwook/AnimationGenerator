from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api.routes.videos import router as videos_router

app = FastAPI(
    title="Kids Motion Engine",
    description="Local AI-powered kids animation engine",
    version="0.1.0",
)

app.include_router(videos_router)

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
ASSETS_DIR.mkdir(exist_ok=True)
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "kids-motion-engine",
        "version": "0.1.0",
    }
