from __future__ import annotations

import threading
import time
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import HTTPException, status

from app.core.config import settings

_hasher = PasswordHasher()


class RefreshSessionStore:
    """
    Thread-safe in-memory store for refresh token sessions.
    Tracks active sessions, single-use token consumption, and revocation.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._cleanup_counter: int = 0
        self._lock = threading.Lock()

    def _maybe_evict_expired_sessions(self, now: float) -> None:
        """Periodically evict expired session records while holding _lock."""
        self._cleanup_counter += 1
        if self._cleanup_counter < 50:
            return
        self._cleanup_counter = 0
        expired_sids = [
            sid for sid, session in self._sessions.items() if now > session["expires_at"]
        ]
        for sid in expired_sids:
            self._sessions.pop(sid, None)

    def create_session(self, user_id: str, sid: str, jti: str, expires_at: float) -> None:
        now = time.time()
        with self._lock:
            self._maybe_evict_expired_sessions(now)
            self._sessions[sid] = {
                "user_id": user_id,
                "current_jti": jti,
                "expires_at": expires_at,
            }

    def rotate_session(
        self,
        sid: str,
        submitted_jti: str,
        new_jti: str,
        expires_at: float,
    ) -> bool:
        """Atomically consume submitted_jti and update session to new_jti."""
        now = time.time()
        with self._lock:
            self._maybe_evict_expired_sessions(now)
            session = self._sessions.get(sid)
            if not session:
                return False
            if now > session["expires_at"]:
                self._sessions.pop(sid, None)
                return False
            if session["current_jti"] != submitted_jti:
                # Token reuse detected -> revoke and remove the entire session
                self._sessions.pop(sid, None)
                return False
            session["current_jti"] = new_jti
            session["expires_at"] = expires_at
            return True

    def revoke_session(self, sid: str) -> bool:
        with self._lock:
            return self._sessions.pop(sid, None) is not None

    def is_session_active(self, sid: str, jti: str) -> bool:
        now = time.time()
        with self._lock:
            self._maybe_evict_expired_sessions(now)
            session = self._sessions.get(sid)
            if not session:
                return False
            if session["current_jti"] != jti:
                return False
            if now > session["expires_at"]:
                self._sessions.pop(sid, None)
                return False
            return True

    def clear(self) -> None:
        with self._lock:
            self._sessions.clear()
            self._cleanup_counter = 0


refresh_session_store = RefreshSessionStore()


def get_password_hash(password: str) -> str:
    """Hash a password synchronously using argon2."""
    return _hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against an argon2 hash synchronously."""
    if not plain_password or not hashed_password:
        return False
    try:
        return _hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def create_access_token(
    subject: str,
    role: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Generate a short-lived JWT access token."""
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": str(role),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: str,
    session_id: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Generate a long-lived JWT refresh token bound to a server-side session.
    Registers the session with refresh_session_store.
    """
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    sid = session_id or str(uuid4())
    jti = str(uuid4())

    payload: dict[str, Any] = {
        "sub": str(subject),
        "sid": sid,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": jti,
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    refresh_session_store.create_session(
        user_id=str(subject),
        sid=sid,
        jti=jti,
        expires_at=expire.timestamp(),
    )
    return token


def rotate_refresh_token(
    subject: str,
    session_id: str,
    submitted_jti: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Atomically consume the submitted refresh token and issue a replacement.
    Raises 401 if the token has already been consumed or revoked.
    """
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    new_jti = str(uuid4())
    success = refresh_session_store.rotate_session(
        sid=session_id,
        submitted_jti=submitted_jti,
        new_jti=new_jti,
        expires_at=expire.timestamp(),
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or already consumed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload: dict[str, Any] = {
        "sub": str(subject),
        "sid": session_id,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": new_jti,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


def verify_student_ownership(resource_owner_id: Any, current_student_id: Any) -> None:
    """
    Enforces Rule 8: Backend enforces record ownership on every student endpoint.
    Raises HTTPException(403) if the resource does not belong to the current authenticated student.
    """
    if str(resource_owner_id) != str(current_student_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to access or modify this record.",
        )
