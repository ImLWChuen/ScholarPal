from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.domain.profile_preparation.schemas import UserRead
from app.domain.shared_enums import UserRole


class RegisterRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str = Field(..., max_length=255, description="Unique email address")
    password: str = Field(..., min_length=6, description="User password")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    role: UserRole = Field(
        default=UserRole.STUDENT,
        description="Role assigned to the user",
    )


class LoginRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(..., description="Short-lived JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")
    user: UserRead = Field(..., description="Authenticated user profile")


class RefreshTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(..., description="Newly issued short-lived JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message: str = Field(..., description="Response message")
