import redis
from fastapi import Depends
from .config import settings

# Redis connection pool
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    username=settings.REDIS_USERNAME,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DATABASE,
    decode_responses=True  # Decode responses to UTF-8 strings
)

def get_redis_client():
    """
    FastAPI dependency to get a Redis client instance.
    """
    try:
        client = redis.Redis(connection_pool=redis_pool)
        yield client
    finally:
        # Connection is returned to the pool automatically
        pass
