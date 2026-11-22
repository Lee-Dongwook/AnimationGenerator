from fastapi import FastAPI

app = FastAPI(
    title="Kids Motion Engine",
    description="Local AI-powered kids animation engine",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "kids-motion-engine",
        "version": "0.1.0",
    }
