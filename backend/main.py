from fastapi import FastAPI
from backend.api.routes.videos import router as videos_router

app = FastAPI(
    title="Kids Motion Engine",
    description="Local AI-powered kids animation engine",
    version="0.1.0",
)

app.include_router(videos_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "kids-motion-engine",
        "version": "0.1.0",
    }
