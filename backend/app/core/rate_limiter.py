from __future__ import annotations

import threading
import time
from collections import defaultdict
from math import ceil

from fastapi import HTTPException, Request, status

from app.core.config import settings


class LoginRateLimiter:
    """
    Thread-safe in-memory sliding-window rate limiter for login attempts.
    Tracks failed attempts per key (e.g. client IP or IP:email pair).
    """

    def __init__(
        self,
        max_attempts: int | None = None,
        window_seconds: int | None = None,
    ) -> None:
        self.max_attempts = max_attempts or settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS
        self.window_seconds = window_seconds or settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _cleanup_old_attempts(self, key: str, now: float) -> list[float]:
        cutoff = now - self.window_seconds
        valid_attempts = [t for t in self._attempts[key] if t > cutoff]
        if valid_attempts:
            self._attempts[key] = valid_attempts
        else:
            self._attempts.pop(key, None)
        return valid_attempts

    def check_rate_limit(self, key: str) -> None:
        """
        Check if the key has exceeded the allowed number of failed login attempts.
        Raises HTTPException(429) if exceeded.
        """
        now = time.time()
        with self._lock:
            attempts = self._cleanup_old_attempts(key, now)
            if len(attempts) >= self.max_attempts:
                oldest = attempts[0]
                retry_after = max(1, ceil(oldest + self.window_seconds - now))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed login attempts. Please try again in {retry_after}s.",
                    headers={"Retry-After": str(retry_after)},
                )

    def record_failed_attempt(self, key: str) -> None:
        """Record a failed login attempt for the key."""
        now = time.time()
        with self._lock:
            attempts = self._cleanup_old_attempts(key, now)
            attempts.append(now)
            self._attempts[key] = attempts

    def reset(self, key: str) -> None:
        """Reset attempts for a specific key upon successful login."""
        with self._lock:
            self._attempts.pop(key, None)

    def clear(self) -> None:
        """Clear all tracked attempts (useful for tests)."""
        with self._lock:
            self._attempts.clear()


login_rate_limiter = LoginRateLimiter()


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, taking proxy headers into account."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


def get_login_rate_limit_key(request: Request, email: str | None = None) -> str:
    """Generate rate limit key based on client IP and optionally normalized email."""
    client_ip = get_client_ip(request)
    if email:
        return f"{client_ip}:{email.lower().strip()}"
    return client_ip
