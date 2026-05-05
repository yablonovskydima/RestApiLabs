import time
from collections import defaultdict
from fastapi import Request, HTTPException, status


_requests: dict[str, list[float]] = defaultdict(list)

WINDOW = 60


def _clean(timestamps: list[float], now: float) -> list[float]:
    return [t for t in timestamps if now - t < WINDOW]


def check_rate_limit(request: Request, limit: int, key: str) -> None:
    now = time.time()
    _requests[key] = _clean(_requests[key], now)

    if len(_requests[key]) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {limit} requests per minute.",
        )

    _requests[key].append(now)