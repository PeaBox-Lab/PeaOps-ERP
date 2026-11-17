import time
from collections import defaultdict, deque
from fastapi import Request, HTTPException

_WINDOW = 60
_LIMITS = {"/api/v1/auth/login": 10, "/api/v1/auth/refresh": 20}
_buckets: dict[str, deque] = defaultdict(deque)

async def rate_limit(request: Request, call_next):
    path = request.url.path
    if path in _LIMITS:
        key = f"{path}:{request.client.host if request.client else 'unknown'}"
        now = time.time()
        bucket = _buckets[key]
        while bucket and now - bucket[0] > _WINDOW:
            bucket.popleft()
        if len(bucket) >= _LIMITS[path]:
            raise HTTPException(status_code=429, detail="Too many requests, try again later")
        bucket.append(now)
    return await call_next(request)