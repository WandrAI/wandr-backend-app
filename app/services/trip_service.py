from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from typing import List, Optional
import uuid

from app.models.trip import Trip, TripMember, TripActivity
from app.models.user import User
from app.schemas.trip import (
    TripCreate, 
    TripUpdate, 
    TripMemberCreate, 
    TripMemberUpdate,
    TripMemberRole,
    TripActivityType
)


class TripService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_trip(self, trip_data: TripCreate, user_id: uuid.UUID) -> Trip:
        """Create a new trip with the user as organizer."""
        trip = Trip(
            title=trip_data.title,
            description=trip_data.description,
            start_date=trip_data.start_date,
            end_date=trip_data.end_date,
            created_by=user_id,
            trip_data=trip_data.trip_data or {},
        )
        self.db.add(trip)
        await self.db.flush()  # Get trip.id
        
        # Add creator as organizer
        trip_member = TripMember(
            trip_id=trip.id,
            user_id=user_id,
            role=TripMemberRole.ORGANIZER,
            permissions={"edit": True, "delete": True, "invite": True, "manage_members": True},
        )
        self.db.add(trip_member)
        
        # Create activity log
        activity = TripActivity(
            trip_id=trip.id,
            user_id=user_id,
            activity_type=TripActivityType.CREATED,
            activity_data={"title": trip.title},
        )
        self.db.add(activity)
        
        await self.db.commit()
        await self.db.refresh(trip)
        return trip
    
    async def get_user_trips(
        self, 
        user_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Trip]:
        """Get trips where user is a member."""
        query = (
            select(Trip)
            .join(TripMember)
            .where(TripMember.user_id == user_id)
            .order_by(Trip.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_trip_by_id(
        self, 
        trip_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> Optional[Trip]:
        """Get trip by ID if user has access."""
        query = (
            select(Trip)
            .join(TripMember)
            .options(selectinload(Trip.members))
            .where(
                and_(
                    Trip.id == trip_id,
                    TripMember.user_id == user_id,
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_trip(
        self, 
        trip_id: uuid.UUID, 
        trip_data: TripUpdate, 
        user_id: uuid.UUID
    ) -> Optional[Trip]:
        """Update trip if user has permission."""
        # Check if user has edit permission
        if not await self._has_trip_permission(trip_id, user_id, "edit"):
            return None
        
        query = select(Trip).where(Trip.id == trip_id)
        result = await self.db.execute(query)
        trip = result.scalar_one_or_none()
        
        if not trip:
            return None
        
        # Update fields
        update_data = trip_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(trip, field, value)
        
        # Create activity log
        activity = TripActivity(
            trip_id=trip_id,
            user_id=user_id,
            activity_type=TripActivityType.UPDATED,
            activity_data=update_data,
        )
        self.db.add(activity)
        
        await self.db.commit()
        await self.db.refresh(trip)
        return trip
    
    async def delete_trip(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete trip if user has permission."""
        # Check if user has delete permission (typically only organizer/creator)
        if not await self._has_trip_permission(trip_id, user_id, "delete"):
            return False
        
        query = select(Trip).where(Trip.id == trip_id)
        result = await self.db.execute(query)
        trip = result.scalar_one_or_none()
        
        if not trip:
            return False
        
        await self.db.delete(trip)
        await self.db.commit()
        return True
    
    async def add_trip_member(
        self, 
        trip_id: uuid.UUID, 
        member_data: TripMemberCreate, 
        user_id: uuid.UUID
    ) -> Optional[TripMember]:
        """Add member to trip if user has permission."""
        # Check if user has invite permission
        if not await self._has_trip_permission(trip_id, user_id, "invite"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to add members to this trip"
            )
        
        # Check if target user exists
        user_query = select(User).where(User.id == member_data.user_id)
        user_result = await self.db.execute(user_query)
        target_user = user_result.scalar_one_or_none()
        
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is already a member
        existing_query = select(TripMember).where(
            and_(
                TripMember.trip_id == trip_id,
                TripMember.user_id == member_data.user_id
            )
        )
        existing_result = await self.db.execute(existing_query)
        existing_member = existing_result.scalar_one_or_none()
        
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this trip"
            )
        
        # Add member
        trip_member = TripMember(
            trip_id=trip_id,
            user_id=member_data.user_id,
            role=member_data.role,
            permissions=member_data.permissions or self._get_default_permissions(member_data.role),
        )
        self.db.add(trip_member)
        
        # Create activity log
        activity = TripActivity(
            trip_id=trip_id,
            user_id=user_id,
            activity_type=TripActivityType.MEMBER_ADDED,
            activity_data={
                "added_user_id": str(member_data.user_id),
                "role": member_data.role
            },
        )
        self.db.add(activity)
        
        await self.db.commit()
        await self.db.refresh(trip_member)
        return trip_member
    
    async def remove_trip_member(
        self, 
        trip_id: uuid.UUID, 
        member_user_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> bool:
        """Remove member from trip if user has permission."""
        # Check if user has manage_members permission
        if not await self._has_trip_permission(trip_id, user_id, "manage_members"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to remove members from this trip"
            )
        
        # Cannot remove trip creator
        trip_query = select(Trip).where(Trip.id == trip_id)
        trip_result = await self.db.execute(trip_query)
        trip = trip_result.scalar_one_or_none()
        
        if trip and trip.created_by == member_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove trip creator"
            )
        
        # Find and remove member
        query = select(TripMember).where(
            and_(
                TripMember.trip_id == trip_id,
                TripMember.user_id == member_user_id
            )
        )
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()
        
        if not member:
            return False
        
        await self.db.delete(member)
        
        # Create activity log
        activity = TripActivity(
            trip_id=trip_id,
            user_id=user_id,
            activity_type=TripActivityType.MEMBER_REMOVED,
            activity_data={"removed_user_id": str(member_user_id)},
        )
        self.db.add(activity)
        
        await self.db.commit()
        return True
    
    async def get_trip_members(
        self, 
        trip_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> List[TripMember]:
        """Get trip members if user has access."""
        # Check if user is a member of the trip
        if not await self._is_trip_member(trip_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access to this trip"
            )
        
        query = (
            select(TripMember)
            .where(TripMember.trip_id == trip_id)
            .order_by(TripMember.created_at)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_user_role_in_trip(
        self, 
        trip_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> Optional[TripMemberRole]:
        """Get user's role in a specific trip."""
        query = select(TripMember.role).where(
            and_(
                TripMember.trip_id == trip_id,
                TripMember.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        return role
    
    async def _has_trip_permission(
        self, 
        trip_id: uuid.UUID, 
        user_id: uuid.UUID, 
        permission: str
    ) -> bool:
        """Check if user has specific permission for trip."""
        query = select(TripMember.permissions).where(
            and_(
                TripMember.trip_id == trip_id,
                TripMember.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        permissions = result.scalar_one_or_none()
        
        if not permissions:
            return False
        
        return permissions.get(permission, False)
    
    async def _is_trip_member(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user is a member of the trip."""
        query = select(TripMember).where(
            and_(
                TripMember.trip_id == trip_id,
                TripMember.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()
        return member is not None
    
    def _get_default_permissions(self, role: TripMemberRole) -> dict:
        """Get default permissions for a role."""
        if role == TripMemberRole.ORGANIZER:
            return {
                "edit": True,
                "delete": True,
                "invite": True,
                "manage_members": True,
                "view": True
            }
        elif role == TripMemberRole.PARTICIPANT:
            return {
                "edit": False,
                "delete": False,
                "invite": False,
                "manage_members": False,
                "view": True
            }
        else:  # VIEWER
            return {
                "edit": False,
                "delete": False,
                "invite": False,
                "manage_members": False,
                "view": True
            }