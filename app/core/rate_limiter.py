import os
import time
import redis.asyncio as aioredis
from fastapi import HTTPException, status

redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            os.getenv("REDIS_URL", "redis://redis:6379"),
            decode_responses=True
        )
    return redis_client


async def check_rate_limit(key: str, limit: int, window: int = 60) -> None:
    redis = await get_redis()
    now = time.time()
    window_start = now - window

    pipe = redis.pipeline()
    await pipe.zremrangebyscore(key, "-inf", window_start)
    await pipe.zadd(key, {str(now): now})
    await pipe.zcard(key)
    await pipe.expire(key, window)
    results = await pipe.execute()

    count = results[2]
    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {limit} requests per minute.",
            headers={"Retry-After": str(window)},
        )