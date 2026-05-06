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


FAKE_TOKEN_KEY = "rl:auth:" + "a" * 32


@pytest.mark.asyncio
async def test_auth_within_limit_allowed():
    for count in range(1, 11):  # 1..10 — всі дозволені
        with patch("app.core.rate_limiter.get_redis", AsyncMock(return_value=make_redis_mock(count=count))):
            await check_rate_limit(FAKE_TOKEN_KEY, limit=10)


@pytest.mark.asyncio
async def test_auth_exactly_at_limit_allowed():
    with patch("app.core.rate_limiter.get_redis", AsyncMock(return_value=make_redis_mock(count=10))):
        await check_rate_limit(FAKE_TOKEN_KEY, limit=10)


@pytest.mark.asyncio
async def test_auth_over_limit_blocked():
    with patch("app.core.rate_limiter.get_redis", AsyncMock(return_value=make_redis_mock(count=11))):
        with pytest.raises(HTTPException) as exc_info:
            await check_rate_limit(FAKE_TOKEN_KEY, limit=10)

    assert exc_info.value.status_code == 429
    assert "10" in exc_info.value.detail