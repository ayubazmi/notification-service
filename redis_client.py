import redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Redis connection pool — har request pe naya connection nahi banta
pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)


def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=pool)
