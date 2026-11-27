"""
Tests for ScholarPal Authentication and Role-based Access Control.

Covers:
- Password hashing with argon2 (verification, mismatch, invalid hash handling)
- User registration (strictly student role, profile creation, duplicate email rejection)
- Login flow (credentials validation, short-lived JWT access token, httpOnly refresh cookie)
- Login rate limiting (blocking after 5 failed attempts, Retry-After header, reservation, proxy IP)
- Refresh token flow (session tracking, atomic consumption on rotation, revoked token rejection)
- Logout flow (cookie clearing, server-side session revocation)
- Role-based access control (require_student, require_admin, get_current_user)
- Error conditions:
  - Expired access and refresh tokens
  - Tampered tokens (invalid signature / corrupted payload)
  - Wrong roles (student trying to access admin endpoint, admin trying student endpoint)
  - Wrong token types (refresh token sent as bearer, access token sent as refresh cookie)
  - Production settings validation for SECRET_KEY
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi import Request
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings, settings
from app.core.rate_limiter import (
    get_client_ip,
    login_rate_limiter,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.domain import StudentProfile, User, UserRole


# ---------------------------------------------------------------------------
# 1. Argon2 Password Hashing Tests
# ---------------------------------------------------------------------------
def test_argon2_password_hashing() -> None:
    raw_password = "SecretPassword123!"
    hashed = get_password_hash(raw_password)

    # Argon2id produces a standard encoded string beginning with $argon2
    assert hashed.startswith("$argon2")
    assert hashed != raw_password

    # Correct password verifies
    assert verify_password(raw_password, hashed) is True

    # Incorrect password fails
    assert verify_password("WrongPassword123!", hashed) is False

    # Empty inputs fail safely
    assert verify_password("", hashed) is False
    assert verify_password(raw_password, "") is False

    # Corrupted hash fails safely without raising unhandled exceptions
    assert verify_password(raw_password, "not-a-valid-argon2-hash") is False


# ---------------------------------------------------------------------------
# 2. Registration Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_register_student_success(
    async_client: AsyncClient,
    async_db: async_sessionmaker[AsyncSession],
) -> None:
    payload = {
        "email": "nurul.student@scholarpal.my",
        "password": "SecurePassword123!",
        "full_name": "Nurul Huda binti Ismail",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["email"] == "nurul.student@scholarpal.my"
    assert data["full_name"] == "Nurul Huda binti Ismail"
    assert data["role"] == "student"
    assert "password" not in data
    assert "hashed_password" not in data

    # Verify DB state: password is argon2 hashed and StudentProfile was created
    async with async_db() as session:
        user = await session.scalar(select(User).where(User.email == "nurul.student@scholarpal.my"))
        assert user is not None
        assert user.hashed_password.startswith("$argon2")
        assert verify_password("SecurePassword123!", user.hashed_password) is True

        profile = await session.scalar(
            select(StudentProfile).where(StudentProfile.user_id == user.id)
        )
        assert profile is not None


@pytest.mark.asyncio
async def test_register_always_creates_student_role(
    async_client: AsyncClient,
    async_db: async_sessionmaker[AsyncSession],
) -> None:
    # Attempting to submit role=administrator in public registration must be ignored/prevented
    payload = {
        "email": "sneaky.admin@scholarpal.my",
        "password": "AdminPassword123!",
        "full_name": "Sneaky Admin",
        "role": "administrator",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "student"

    async with async_db() as session:
        user = await session.scalar(select(User).where(User.email == "sneaky.admin@scholarpal.my"))
        assert user is not None
        assert user.role == "student"
        profile = await session.scalar(
            select(StudentProfile).where(StudentProfile.user_id == user.id)
        )
        assert profile is not None


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(async_client: AsyncClient) -> None:
    payload = {
        "email": "duplicate@scholarpal.my",
        "password": "Password123!",
        "full_name": "Test User",
    }
    first_res = await async_client.post("/api/v1/auth/register", json=payload)
    assert first_res.status_code == 201

    second_res = await async_client.post("/api/v1/auth/register", json=payload)
    assert second_res.status_code == 400
    assert "already registered" in second_res.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 3. Login & Rate Limiting Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_login_success_and_httponly_cookie(async_client: AsyncClient) -> None:
    # Register user
    reg_payload = {
        "email": "haziq.login@scholarpal.my",
        "password": "CorrectPassword123!",
        "full_name": "Haziq bin Zulkifli",
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)

    # Login
    login_payload = {
        "email": "haziq.login@scholarpal.my",
        "password": "CorrectPassword123!",
    }
    res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 200
    body = res.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    assert body["user"]["email"] == "haziq.login@scholarpal.my"

    # Verify httpOnly cookie presence and parameters
    set_cookie_header = res.headers.get("set-cookie", "")
    assert settings.REFRESH_COOKIE_NAME in set_cookie_header
    assert "httponly" in set_cookie_header.lower()
    assert f"path={settings.REFRESH_COOKIE_PATH}" in set_cookie_header.lower()


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient) -> None:
    reg_payload = {
        "email": "valid.user@scholarpal.my",
        "password": "CorrectPassword123!",
        "full_name": "Valid User",
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)

    # Wrong password
    res1 = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "valid.user@scholarpal.my", "password": "WrongPassword!"},
    )
    assert res1.status_code == 401
    assert "invalid email or password" in res1.json()["detail"].lower()

    # Non-existent email
    res2 = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@scholarpal.my", "password": "AnyPassword123!"},
    )
    assert res2.status_code == 401


@pytest.mark.asyncio
async def test_login_rate_limiting(async_client: AsyncClient) -> None:
    reg_payload = {
        "email": "ratelimit.target@scholarpal.my",
        "password": "RealPassword123!",
        "full_name": "Target User",
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)

    # Trigger max_attempts (5) failed logins
    for i in range(5):
        bad_res = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "ratelimit.target@scholarpal.my",
                "password": f"BadPassword{i}!",
            },
        )
        assert bad_res.status_code == 401

    # 6th attempt should be blocked by rate limiter with HTTP 429
    blocked_res = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "ratelimit.target@scholarpal.my",
            "password": "BadPassword6!",
        },
    )
    assert blocked_res.status_code == 429
    assert "too many failed login attempts" in blocked_res.json()["detail"].lower()
    assert "retry-after" in blocked_res.headers


def test_rate_limiter_in_flight_reservation() -> None:
    test_key = "192.168.1.100:test@example.com"
    login_rate_limiter.clear()

    # Reserve 5 attempts concurrently
    with login_rate_limiter.reserve_attempt(test_key):
        with login_rate_limiter.reserve_attempt(test_key):
            with login_rate_limiter.reserve_attempt(test_key):
                with login_rate_limiter.reserve_attempt(test_key):
                    with login_rate_limiter.reserve_attempt(test_key):
                        # 6th reservation while 5 in-flight must be rejected
                        with pytest.raises(Exception) as exc:
                            login_rate_limiter.check_and_reserve(test_key)
                        assert exc.value.status_code == 429

    # Once context managers exit, all 5 reservations are released
    assert login_rate_limiter._reservations.get(test_key, 0) == 0


def test_client_ip_trusted_proxy_handling() -> None:
    # 1. Untrusted direct client -> client host is used, X-Forwarded-For ignored
    scope_untrusted = {
        "type": "http",
        "client": ("198.51.100.25", 54321),
        "headers": [(b"x-forwarded-for", b"203.0.113.195")],
    }
    req_untrusted = Request(scope_untrusted)
    assert get_client_ip(req_untrusted) == "198.51.100.25"

    # 2. Trusted proxy peer -> X-Forwarded-For address is used
    scope_trusted = {
        "type": "http",
        "client": ("127.0.0.1", 54321),
        "headers": [(b"x-forwarded-for", b"10.0.0.1, 203.0.113.195")],
    }
    req_trusted = Request(scope_trusted)
    assert get_client_ip(req_trusted) == "203.0.113.195"


# ---------------------------------------------------------------------------
# 4. Refresh & Logout Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_refresh_token_flow(async_client: AsyncClient) -> None:
    reg_payload = {
        "email": "refresh.user@scholarpal.my",
        "password": "Password123!",
        "full_name": "Refresh User",
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "refresh.user@scholarpal.my", "password": "Password123!"},
    )
    old_access_token = login_res.json()["access_token"]

    # Call refresh (cookies are stored in async_client)
    refresh_res = await async_client.post("/api/v1/auth/refresh")
    assert refresh_res.status_code == 200
    refresh_body = refresh_res.json()
    new_access_token = refresh_body["access_token"]
    assert new_access_token != old_access_token
    assert refresh_body["token_type"] == "bearer"

    # New refresh cookie should also be set (rotation)
    assert settings.REFRESH_COOKIE_NAME in refresh_res.headers.get("set-cookie", "")


@pytest.mark.asyncio
async def test_consumed_refresh_token_rejected_on_reuse(async_client: AsyncClient) -> None:
    # 1. Register & login
    reg_payload = {
        "email": "consumed.token@scholarpal.my",
        "password": "Password123!",
        "full_name": "Consumed Token User",
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)
    await async_client.post(
        "/api/v1/auth/login",
        json={"email": "consumed.token@scholarpal.my", "password": "Password123!"},
    )
    # Save the original refresh token
    first_cookie = async_client.cookies.get(settings.REFRESH_COOKIE_NAME)

    # 2. First refresh succeeds and rotates token
    res1 = await async_client.post("/api/v1/auth/refresh")
    assert res1.status_code == 200

    # 3. Re-injecting the old consumed refresh token must be rejected with 401
    async_client.cookies.set(settings.REFRESH_COOKIE_NAME, first_cookie)
    res2 = await async_client.post("/api/v1/auth/refresh")
    assert res2.status_code == 401
    assert "revoked or already consumed" in res2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_revokes_server_side_session(async_client: AsyncClient) -> None:
    # Login to set cookie
    reg_payload = {
        "email": "logout.revoked@scholarpal.my",
        "password": "Password123!",
        "full_name": "Logout Revoked User",
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)
    await async_client.post(
        "/api/v1/auth/login",
        json={"email": "logout.revoked@scholarpal.my", "password": "Password123!"},
    )
    saved_cookie = async_client.cookies.get(settings.REFRESH_COOKIE_NAME)

    # Logout
    logout_res = await async_client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Successfully logged out"

    # Attempting to use the logged-out refresh token must fail with 401
    async_client.cookies.set(settings.REFRESH_COOKIE_NAME, saved_cookie)
    refresh_res = await async_client.post("/api/v1/auth/refresh")
    assert refresh_res.status_code == 401
    assert "revoked or already consumed" in refresh_res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_safe_when_cookie_absent(async_client: AsyncClient) -> None:
    # Fresh client with no cookies
    async_client.cookies.clear()
    logout_res = await async_client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Successfully logged out"


# ---------------------------------------------------------------------------
# 5. Role-based Dependencies (require_student & require_admin)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_role_based_student_access(async_client: AsyncClient) -> None:
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "student.role@scholarpal.my",
            "password": "Password123!",
            "full_name": "Student Role User",
        },
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "student.role@scholarpal.my", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Student accessing student endpoint -> 200 OK
    res_student = await async_client.get("/api/v1/auth/test-student", headers=headers)
    assert res_student.status_code == 200
    assert res_student.json()["role"] == "student"

    # Student accessing admin endpoint -> 403 Forbidden
    res_admin = await async_client.get("/api/v1/auth/test-admin", headers=headers)
    assert res_admin.status_code == 403
    assert "administrator role required" in res_admin.json()["detail"].lower()


@pytest.mark.asyncio
async def test_role_based_admin_access(
    async_client: AsyncClient,
    async_db: async_sessionmaker[AsyncSession],
) -> None:
    # Administrators are provisioned via database fixtures or administrative workflows
    async with async_db() as session:
        admin_user = User(
            id="admin-prov-001",
            email="admin.role@scholarpal.my",
            full_name="Admin Role User",
            hashed_password=get_password_hash("AdminPassword123!"),
            role=UserRole.ADMINISTRATOR.value,
            is_active=True,
            is_verified=True,
        )
        session.add(admin_user)
        await session.commit()

    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin.role@scholarpal.my", "password": "AdminPassword123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Admin accessing admin endpoint -> 200 OK
    res_admin = await async_client.get("/api/v1/auth/test-admin", headers=headers)
    assert res_admin.status_code == 200
    assert res_admin.json()["role"] == "administrator"

    # Admin accessing student endpoint -> 403 Forbidden
    res_student = await async_client.get("/api/v1/auth/test-student", headers=headers)
    assert res_student.status_code == 403
    assert "student role required" in res_student.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 6. Expired, Tampered, and Malformed Token Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_expired_access_token_rejected(async_client: AsyncClient) -> None:
    expired_token = create_access_token(
        subject="test-user-id",
        role="student",
        expires_delta=timedelta(seconds=-10),
    )
    res = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res.status_code == 401
    assert "token has expired" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_tampered_access_token_rejected(async_client: AsyncClient) -> None:
    valid_token = create_access_token(subject="test-user-id", role="student")
    parts = valid_token.split(".")
    tampered_signature = parts[2][:-4] + "ABCD"
    tampered_token = f"{parts[0]}.{parts[1]}.{tampered_signature}"

    res1 = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tampered_token}"},
    )
    assert res1.status_code == 401
    assert "invalid token" in res1.json()["detail"].lower()

    res2 = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-even-a-jwt"},
    )
    assert res2.status_code == 401


@pytest.mark.asyncio
async def test_expired_refresh_token_rejected(async_client: AsyncClient) -> None:
    expired_refresh = create_refresh_token(
        subject="test-user-id",
        expires_delta=timedelta(seconds=-10),
    )
    async_client.cookies.set(settings.REFRESH_COOKIE_NAME, expired_refresh)
    res = await async_client.post("/api/v1/auth/refresh")
    assert res.status_code == 401
    assert "token has expired" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_tampered_refresh_token_rejected(async_client: AsyncClient) -> None:
    valid_refresh = create_refresh_token(subject="test-user-id")
    parts = valid_refresh.split(".")
    tampered_refresh = f"{parts[0]}.{parts[1]}.badsignature"

    async_client.cookies.set(settings.REFRESH_COOKIE_NAME, tampered_refresh)
    res = await async_client.post("/api/v1/auth/refresh")
    assert res.status_code == 401
    assert "invalid token" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_wrong_token_type_rejected(async_client: AsyncClient) -> None:
    # Case A: Refresh token passed as Bearer access token on protected endpoint
    refresh_token = create_refresh_token(subject="test-user-id")
    res1 = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert res1.status_code == 401
    assert "access token required" in res1.json()["detail"].lower()

    # Case B: Access token passed as cookie to /refresh endpoint
    access_token = create_access_token(subject="test-user-id", role="student")
    async_client.cookies.set(settings.REFRESH_COOKIE_NAME, access_token)
    res2 = await async_client.post("/api/v1/auth/refresh")
    assert res2.status_code == 401
    assert "refresh token required" in res2.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 7. Production Settings Validation Tests
# ---------------------------------------------------------------------------
def test_production_secret_key_validation() -> None:
    # In development/test, placeholder is accepted
    dev_settings = Settings(
        ENVIRONMENT="development",
        SECRET_KEY="change-this-in-production-super-secret-key-at-least-32-bytes-long",
    )
    assert dev_settings.ENVIRONMENT == "development"

    # In production, default placeholder must raise ValueError
    with pytest.raises(ValueError) as exc:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="change-this-in-production-super-secret-key-at-least-32-bytes-long",
        )
    assert "SECRET_KEY must be a deployment-specific secret" in str(exc.value)

    # In production, custom secure key of >= 32 chars succeeds
    prod_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="secure-production-random-key-at-least-32-characters-long",
    )
    assert prod_settings.SECRET_KEY.startswith("secure-production")
