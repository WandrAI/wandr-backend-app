from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username",
    )

    @field_validator("username", "email", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace from string fields."""
        if isinstance(v, str):
            return v.strip()
        return v


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(
        ..., min_length=8, max_length=100, description="User password"
    )


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime | None = None


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfileBase(BaseModel):
    """Base user profile schema."""

    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)
    display_name: str | None = Field(None, max_length=100)
    avatar_url: str | None = Field(None, description="URL to user avatar image")
    bio: str | None = Field(None, max_length=500, description="User bio")
    timezone: str | None = Field(None, max_length=50)
    travel_preferences: dict[str, Any] = Field(default_factory=dict)
    privacy_settings: dict[str, Any] = Field(default_factory=dict)

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v):
        """Validate timezone string."""
        if v is not None:
            import zoneinfo

            try:
                zoneinfo.ZoneInfo(v)
            except zoneinfo.ZoneInfoNotFoundError as e:
                raise ValueError("Invalid timezone") from e
        return v


class UserProfileCreate(UserProfileBase):
    """Schema for creating user profile."""


class UserProfileUpdate(UserProfileBase):
    """Schema for updating user profile."""


class UserProfileResponse(UserProfileBase):
    """Schema for user profile response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime | None = None
