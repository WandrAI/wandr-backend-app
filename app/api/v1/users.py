import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserProfileResponse,
    UserProfileUpdate,
    UserResponse,
)
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_current_user_profile_details(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Get current user's detailed profile."""
    user_service = UserService(db)
    profile = await user_service.get_user_profile(current_user.id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
        )

    return UserProfileResponse.model_validate(profile)


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_current_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Update current user's profile."""
    user_service = UserService(db)
    profile = await user_service.update_user_profile(current_user.id, profile_data)

    return UserProfileResponse.model_validate(profile)


@router.get("/{user_id}", response_model=dict)
async def get_user_public_info(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get public user information."""
    user_service = UserService(db)
    user_info = await user_service.get_public_user_info(user_id)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Return only public information
    return {
        "id": user_info["id"],
        "username": user_info["username"],
        "display_name": user_info["display_name"],
        "avatar_url": user_info["avatar_url"],
    }
