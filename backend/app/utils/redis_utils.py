import redis
import logging
from app.core.config import settings
from app.core.redis_client import redis_pool

logger = logging.getLogger(__name__)

def get_redis_client_from_pool():
    """Gets a Redis client from the existing connection pool."""
    try:
        return redis.Redis(connection_pool=redis_pool)
    except Exception:
        logger.error("Failed to create Redis client from pool.", exc_info=True)
        return None

def get_scan_detection_threshold() -> int:
    """
    Gets the scan detection threshold from Redis.
    Falls back to the default value from settings if Redis is unavailable or the key is not set.
    """
    redis_client = get_redis_client_from_pool()
    if redis_client:
        try:
            threshold_str = redis_client.get("config:scan_detection_threshold")
            if threshold_str is not None:
                threshold = int(threshold_str)
                logger.debug(f"Using scan detection threshold from Redis: {threshold}")
                return threshold
        except Exception:
            logger.error("Failed to get or parse threshold from Redis. Falling back to default.", exc_info=True)
            
    default_threshold = settings.SCAN_DETECTION_THRESHOLD_DEFAULT
    logger.debug(f"Using default scan detection threshold: {default_threshold}")
    return default_threshold

def set_scan_detection_threshold(value: int) -> bool:
    """
    Sets the scan detection threshold in Redis.
    (This is a helper function for potential future use via an admin interface)
    """
    redis_client = get_redis_client_from_pool()
    if redis_client:
        try:
            redis_client.set("config:scan_detection_threshold", value)
            logger.info(f"Successfully set scan detection threshold in Redis to: {value}")
            return True
        except Exception:
            logger.error(f"Failed to set scan detection threshold in Redis.", exc_info=True)
            return False
    return False