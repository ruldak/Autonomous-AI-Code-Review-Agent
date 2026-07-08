import redis.asyncio as redis
from app.config import settings
from app.utils.logger import logger

redis_client = None

async def init_redis():
    global redis_client
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error("Failed to connect to Redis", error=str(e))
        raise e

def get_redis():
    return redis_client