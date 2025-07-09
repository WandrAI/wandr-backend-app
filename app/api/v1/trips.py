import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.common import Message
from app.schemas.trip import (
    TripCreate,
    TripListResponse,
    TripMemberCreate,
    TripMemberResponse,
    TripResponse,
    TripUpdate,
)
from app.services.trip_service import TripService
from app.services.user_service import UserService

router = APIRouter()


@router.post("", response_model=TripResponse)
async def create_trip(
    trip_data: TripCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    """Create a new trip."""
    trip_service = TripService(db)
    trip = await trip_service.create_trip(trip_data, current_user.id)

    # Get user's role in the trip
    user_role = await trip_service.get_user_role_in_trip(trip.id, current_user.id)

    response = TripResponse.model_validate(trip)
    response.member_count = 1  # Creator is the first member
    response.user_role = user_role
    return response


@router.get("", response_model=list[TripListResponse])
async def get_user_trips(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TripListResponse]:
    """Get trips for the current user."""
    trip_service = TripService(db)
    trips = await trip_service.get_user_trips(current_user.id, skip, limit)

    # Build response with user roles and member counts
    response = []
    for trip in trips:
        user_role = await trip_service.get_user_role_in_trip(trip.id, current_user.id)

        # Count members without calling get_trip_members (which has permission checks)
        from sqlalchemy import func, select

        from app.models.trip import TripMember

        count_query = select(func.count(TripMember.id)).where(
            TripMember.trip_id == trip.id
        )
        count_result = await db.execute(count_query)
        member_count = count_result.scalar() or 0

        trip_response = TripListResponse.model_validate(trip)
        trip_response.user_role = user_role
        trip_response.member_count = member_count
        response.append(trip_response)

    return response


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    """Get a specific trip."""
    trip_service = TripService(db)
    trip = await trip_service.get_trip_by_id(trip_id, current_user.id)

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found or no access"
        )

    # Get user's role and member count
    user_role = await trip_service.get_user_role_in_trip(trip.id, current_user.id)

    # Count members directly
    from sqlalchemy import func, select

    from app.models.trip import TripMember

    count_query = select(func.count(TripMember.id)).where(TripMember.trip_id == trip.id)
    count_result = await db.execute(count_query)
    member_count = count_result.scalar() or 0

    response = TripResponse.model_validate(trip)
    response.user_role = user_role
    response.member_count = member_count
    return response


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: uuid.UUID,
    trip_update: TripUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    """Update a trip."""
    trip_service = TripService(db)
    trip = await trip_service.update_trip(trip_id, trip_update, current_user.id)

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found or no permission to edit",
        )

    # Get user's role and member count
    user_role = await trip_service.get_user_role_in_trip(trip.id, current_user.id)

    # Count members directly
    from sqlalchemy import func, select

    from app.models.trip import TripMember

    count_query = select(func.count(TripMember.id)).where(TripMember.trip_id == trip.id)
    count_result = await db.execute(count_query)
    member_count = count_result.scalar() or 0

    response = TripResponse.model_validate(trip)
    response.user_role = user_role
    response.member_count = member_count
    return response


@router.delete("/{trip_id}", response_model=Message)
async def delete_trip(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Message:
    """Delete a trip."""
    trip_service = TripService(db)
    success = await trip_service.delete_trip(trip_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found or no permission to delete",
        )

    return Message(message="Trip deleted successfully")


@router.get("/{trip_id}/members", response_model=list[TripMemberResponse])
async def get_trip_members(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TripMemberResponse]:
    """Get trip members."""
    trip_service = TripService(db)
    user_service = UserService(db)

    members = await trip_service.get_trip_members(trip_id, current_user.id)

    # Enrich with user information
    response = []
    for member in members:
        user_info = await user_service.get_public_user_info(member.user_id)
        member_response = TripMemberResponse.model_validate(member)

        if user_info:
            member_response.user_email = user_info["email"]
            member_response.user_username = user_info["username"]
            member_response.user_display_name = user_info["display_name"]

        response.append(member_response)

    return response


@router.post("/{trip_id}/members", response_model=TripMemberResponse)
async def add_trip_member(
    trip_id: uuid.UUID,
    member_data: TripMemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripMemberResponse:
    """Add a member to the trip."""
    trip_service = TripService(db)
    user_service = UserService(db)

    member = await trip_service.add_trip_member(trip_id, member_data, current_user.id)

    # Enrich with user information
    user_info = await user_service.get_public_user_info(member.user_id)
    response = TripMemberResponse.model_validate(member)

    if user_info:
        response.user_email = user_info["email"]
        response.user_username = user_info["username"]
        response.user_display_name = user_info["display_name"]

    return response


@router.delete("/{trip_id}/members/{user_id}", response_model=Message)
async def remove_trip_member(
    trip_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Message:
    """Remove a member from the trip."""
    trip_service = TripService(db)

    success = await trip_service.remove_trip_member(trip_id, user_id, current_user.id)

    if not success:
        return Message(message="Member not found in trip")

    return Message(message="Member removed successfully")
