from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .redis_client import get_redis

app = FastAPI(
    title="ShopFlow — Notification Service",
    description="User notifications stored in Redis with 24hr expiry",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    try:
        r = get_redis()
        r.ping()                     # Redis se actually connect ho ke check karo
        return {"status": "healthy", "service": "notification-service", "redis": "connected"}
    except Exception:
        return {"status": "unhealthy", "service": "notification-service", "redis": "disconnected"}

