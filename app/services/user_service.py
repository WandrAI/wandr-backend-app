import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserProfile
from app.schemas.user import UserProfileUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_with_profile(self, user_id: uuid.UUID) -> User | None:
        """Get user with profile information."""
        query = (
            select(User).options(selectinload(User.profile)).where(User.id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_profile(self, user_id: uuid.UUID) -> UserProfile | None:
        """Get user profile by user ID."""
        query = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_user_profile(
        self, user_id: uuid.UUID, profile_data: UserProfileUpdate
    ) -> UserProfile | None:
        """Update user profile."""
        query = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.db.execute(query)
        profile = result.scalar_one_or_none()

        if not profile:
            # Create profile if it doesn't exist
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)

        # Update fields
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def get_public_user_info(self, user_id: uuid.UUID) -> dict | None:
        """Get public user information (for trip member display)."""
        query = (
            select(User, UserProfile)
            .outerjoin(UserProfile, User.id == UserProfile.user_id)
            .where(User.id == user_id)
        )
        result = await self.db.execute(query)
        row = result.first()

        if not row:
            return None

        user, profile = row
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "display_name": profile.display_name if profile else None,
            "avatar_url": profile.avatar_url if profile else None,
        }
