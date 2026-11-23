from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_admin, require_student
from app.core.config import settings
from app.core.rate_limiter import get_login_rate_limit_key, login_rate_limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.domain.auth_schemas import (
    LoginRequest,
    MessageResponse,
    RefreshTokenResponse,
    RegisterRequest,
    TokenResponse,
)
from app.domain.profile_preparation.models import StudentProfile, User
from app.domain.profile_preparation.schemas import UserRead
from app.domain.shared_enums import UserRole

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    email_clean = data.email.lower().strip()

    existing = await db.scalar(select(User).where(User.email == email_clean))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user_id = f"usr-{uuid4()}"
    role_str = data.role.value if hasattr(data.role, "value") else str(data.role)
    new_user = User(
        id=user_id,
        email=email_clean,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        role=role_str,
        is_active=True,
        is_verified=False,
    )
    db.add(new_user)

    if role_str == UserRole.STUDENT.value:
        profile = StudentProfile(
            id=f"prof-{uuid4()}",
            user_id=user_id,
        )
        db.add(profile)

    await db.commit()
    await db.refresh(new_user)
    return UserRead.model_validate(new_user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive short-lived access token and httpOnly refresh cookie",
)
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    rate_key = get_login_rate_limit_key(request, data.email)
    login_rate_limiter.check_rate_limit(rate_key)

    email_clean = data.email.lower().strip()
    user = await db.scalar(select(User).where(User.email == email_clean))

    if not user or not verify_password(data.password, user.hashed_password):
        login_rate_limiter.record_failed_attempt(rate_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    login_rate_limiter.reset(rate_key)

    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id)

    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path=settings.REFRESH_COOKIE_PATH,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserRead.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Exchange httpOnly refresh token for a new short-lived access token",
)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> RefreshTokenResponse:
    token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token cookie",
        )

    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: refresh token required",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        )

    user = await db.scalar(select(User).where(User.id == user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    new_access_token = create_access_token(subject=user.id, role=user.role)
    new_refresh_token = create_refresh_token(subject=user.id)

    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=new_refresh_token,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path=settings.REFRESH_COOKIE_PATH,
    )

    return RefreshTokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Clear refresh token cookie and invalidate session",
)
async def logout(response: Response) -> MessageResponse:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        path=settings.REFRESH_COOKIE_PATH,
    )
    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=UserRead,
    summary="Retrieve current authenticated user",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.get(
    "/test-student",
    summary="Endpoint protected by require_student",
)
async def test_student_role(
    current_student: User = Depends(require_student),
) -> dict[str, str]:
    return {
        "message": "Authorized as student",
        "user_id": current_student.id,
        "role": current_student.role,
    }


@router.get(
    "/test-admin",
    summary="Endpoint protected by require_admin",
)
async def test_admin_role(
    current_admin: User = Depends(require_admin),
) -> dict[str, str]:
    return {
        "message": "Authorized as administrator",
        "user_id": current_admin.id,
        "role": current_admin.role,
    }
