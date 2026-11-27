from __future__ import annotations

import contextlib
import ipaddress
import socket
import threading
import time
from collections import defaultdict
from collections.abc import Iterator
from math import ceil

from fastapi import HTTPException, Request, status

from app.core.config import settings


class LoginRateLimiter:
    """
    Thread-safe in-memory sliding-window rate limiter for login attempts.
    Tracks failed attempts and in-flight reservations per key.
    Periodically evicts expired entries globally to bound memory growth.
    """

    def __init__(
        self,
        max_attempts: int | None = None,
        window_seconds: int | None = None,
    ) -> None:
        self.max_attempts = max_attempts or settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS
        self.window_seconds = window_seconds or settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._reservations: dict[str, int] = defaultdict(int)
        self._cleanup_counter: int = 0
        self._lock = threading.Lock()

    def _cleanup_old_attempts(self, key: str, now: float) -> list[float]:
        cutoff = now - self.window_seconds
        valid_attempts = [t for t in self._attempts[key] if t > cutoff]
        if valid_attempts:
            self._attempts[key] = valid_attempts
        else:
            self._attempts.pop(key, None)
        return valid_attempts

    def _maybe_evict_expired_entries(self, now: float) -> None:
        """Periodically sweep and evict expired entries across all keys."""
        self._cleanup_counter += 1
        if self._cleanup_counter < 50:
            return
        self._cleanup_counter = 0
        cutoff = now - self.window_seconds
        expired_keys = [k for k, v in self._attempts.items() if not v or max(v) <= cutoff]
        for k in expired_keys:
            if not self._reservations.get(k):
                self._attempts.pop(k, None)

    def check_rate_limit(self, key: str) -> None:
        """
        Check if the key has exceeded the allowed number of failed login attempts.
        Raises HTTPException(429) if exceeded.
        """
        now = time.time()
        with self._lock:
            self._maybe_evict_expired_entries(now)
            attempts = self._cleanup_old_attempts(key, now)
            total_active = len(attempts) + self._reservations.get(key, 0)
            if total_active >= self.max_attempts:
                oldest = attempts[0] if attempts else now
                retry_after = max(1, ceil(oldest + self.window_seconds - now))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed login attempts. Please try again in {retry_after}s.",
                    headers={"Retry-After": str(retry_after)},
                )

    def check_and_reserve(self, key: str) -> None:
        """
        Atomically check rate limit and reserve an attempt slot under lock.
        Raises HTTPException(429) if capacity is exceeded.
        """
        now = time.time()
        with self._lock:
            self._maybe_evict_expired_entries(now)
            attempts = self._cleanup_old_attempts(key, now)
            total_active = len(attempts) + self._reservations.get(key, 0)
            if total_active >= self.max_attempts:
                oldest = attempts[0] if attempts else now
                retry_after = max(1, ceil(oldest + self.window_seconds - now))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed login attempts. Please try again in {retry_after}s.",
                    headers={"Retry-After": str(retry_after)},
                )
            self._reservations[key] += 1

    def release_reservation(self, key: str) -> None:
        """Release an in-flight capacity reservation without recording a failure."""
        with self._lock:
            if self._reservations[key] > 1:
                self._reservations[key] -= 1
            else:
                self._reservations.pop(key, None)

    @contextlib.contextmanager
    def reserve_attempt(self, key: str) -> Iterator[None]:
        """Context manager to reserve capacity and automatically release on completion."""
        self.check_and_reserve(key)
        try:
            yield
        finally:
            self.release_reservation(key)

    def record_failed_attempt(self, key: str) -> None:
        """Record a failed login attempt for the key."""
        now = time.time()
        with self._lock:
            attempts = self._cleanup_old_attempts(key, now)
            attempts.append(now)
            self._attempts[key] = attempts

    def reset(self, key: str) -> None:
        """Reset failed-attempt history for a key upon successful login."""
        with self._lock:
            self._attempts.pop(key, None)

    def clear(self) -> None:
        """Clear all tracked attempts and reservations (useful for tests)."""
        with self._lock:
            self._attempts.clear()
            self._reservations.clear()
            self._cleanup_counter = 0


login_rate_limiter = LoginRateLimiter()


def _is_trusted_proxy(peer_host: str) -> bool:
    """
    Check if peer_host matches an entry in settings.TRUSTED_PROXIES
    by exact string, CIDR network, or resolved hostname IP (e.g., Docker nginx hop).
    """
    if peer_host in settings.TRUSTED_PROXIES:
        return True

    try:
        peer_ip = ipaddress.ip_address(peer_host)
    except ValueError:
        return False

    for entry in settings.TRUSTED_PROXIES:
        try:
            if "/" in entry:
                if peer_ip in ipaddress.ip_network(entry, strict=False):
                    return True
                continue
            if ipaddress.ip_address(entry) == peer_ip:
                return True
        except ValueError:
            # Entry is a hostname (e.g., 'nginx', 'frontend', 'localhost')
            try:
                _, _, resolved_ips = socket.gethostbyname_ex(entry)
                if peer_host in resolved_ips:
                    return True
            except OSError:
                continue
    return False


def get_client_ip(request: Request) -> str:
    """
    Extract client IP from request.
    Uses request.client.host by default. Consults proxy headers only when the
    immediate peer is a trusted proxy in settings.TRUSTED_PROXIES.
    """
    peer_host = request.client.host if request.client else "unknown"
    if _is_trusted_proxy(peer_host):
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # When trusted proxy rewrites or appends, use the appended value
            parts = [ip.strip() for ip in forwarded_for.split(",") if ip.strip()]
            if parts:
                return parts[-1]
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
    return peer_host


def get_login_rate_limit_key(request: Request, email: str | None = None) -> str:
    """Generate rate limit key based on client IP and optionally normalized email."""
    client_ip = get_client_ip(request)
    if email:
        return f"{client_ip}:{email.lower().strip()}"
    return client_ip
