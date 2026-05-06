import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.core.rate_limiter import check_rate_limit


def make_redis_mock(count: int):
    pipe = MagicMock()
    pipe.zremrangebyscore = AsyncMock()
    pipe.zadd = AsyncMock()
    pipe.zcard = AsyncMock()
    pipe.expire = AsyncMock()
    pipe.execute = AsyncMock(return_value=[None, None, count, None])

    redis_mock = MagicMock()
    redis_mock.pipeline.return_value = pipe
    return redis_mock


@pytest.mark.asyncio
async def test_anon_first_request_allowed():
    with patch("app.core.rate_limiter.get_redis", AsyncMock(return_value=make_redis_mock(count=1))):
        await check_rate_limit("rl:anon:127.0.0.1", limit=2)


@pytest.mark.asyncio
async def test_anon_second_request_allowed():
    with patch("app.core.rate_limiter.get_redis", AsyncMock(return_value=make_redis_mock(count=2))):
        await check_rate_limit("rl:anon:127.0.0.1", limit=2)


@pytest.mark.asyncio
async def test_anon_third_request_blocked():
    with patch("app.core.rate_limiter.get_redis", AsyncMock(return_value=make_redis_mock(count=3))):
        with pytest.raises(HTTPException) as exc_info:
            await check_rate_limit("rl:anon:127.0.0.1", limit=2)

    assert exc_info.value.status_code == 429
    assert "2" in exc_info.value.detail