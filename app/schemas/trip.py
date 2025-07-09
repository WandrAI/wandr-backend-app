from datetime import date, datetime
from enum import Enum
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TripStatus(str, Enum):
    """Trip status options."""

    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TripMemberRole(str, Enum):
    """Trip member role options."""

    ORGANIZER = "organizer"
    PARTICIPANT = "participant"
    VIEWER = "viewer"


class TripBase(BaseModel):
    """Base trip schema."""

    title: str = Field(..., min_length=1, max_length=200, description="Trip title")
    description: str | None = Field(
        None, max_length=1000, description="Trip description"
    )
    destination: str | None = Field(
        None, max_length=200, description="Trip destination"
    )
    start_date: date | None = Field(None, description="Trip start date")
    end_date: date | None = Field(None, description="Trip end date")

    @field_validator("end_date")
    @classmethod
    def end_date_after_start_date(cls, v, info):
        if v and info.data.get("start_date"):
            start_date = info.data["start_date"]
            # Convert string to date if needed
            if isinstance(start_date, str):
                from datetime import datetime

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(v, str):
                from datetime import datetime

                v = datetime.strptime(v, "%Y-%m-%d").date()
            if v < start_date:
                raise ValueError("End date must be after start date")
        return v


class TripCreate(TripBase):
    """Schema for creating a trip."""

    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    trip_data: dict[str, Any] | None = Field(
        default_factory=dict, description="Additional trip data"
    )


class TripUpdate(BaseModel):
    """Schema for updating a trip."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    start_date: date | None = None
    end_date: date | None = None
    status: TripStatus | None = None
    trip_data: dict[str, Any] | None = None

    @field_validator("end_date")
    @classmethod
    def end_date_after_start_date(cls, v, info):
        if v and info.data.get("start_date"):
            start_date = info.data["start_date"]
            # Convert string to date if needed
            if isinstance(start_date, str):
                from datetime import datetime

                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(v, str):
                from datetime import datetime

                v = datetime.strptime(v, "%Y-%m-%d").date()
            if v < start_date:
                raise ValueError("End date must be after start date")
        return v


class TripResponse(TripBase):
    """Schema for trip response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: TripStatus
    created_by: uuid.UUID
    trip_data: dict[str, Any]
    created_at: datetime
    updated_at: datetime | None = None

    # Optional nested data
    member_count: int | None = Field(None, description="Number of trip members")
    user_role: TripMemberRole | None = Field(
        None, description="Current user's role in this trip"
    )


class TripListResponse(BaseModel):
    """Schema for trip list response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: TripStatus
    created_by: uuid.UUID
    created_at: datetime
    member_count: int | None = None
    user_role: TripMemberRole | None = None


class TripMemberBase(BaseModel):
    """Base trip member schema."""

    user_id: uuid.UUID
    role: TripMemberRole = TripMemberRole.PARTICIPANT


class TripMemberCreate(TripMemberBase):
    """Schema for adding a trip member."""

    permissions: dict[str, Any] | None = Field(default_factory=dict)


class TripMemberUpdate(BaseModel):
    """Schema for updating a trip member."""

    role: TripMemberRole | None = None
    permissions: dict[str, Any] | None = None


class TripMemberResponse(TripMemberBase):
    """Schema for trip member response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trip_id: uuid.UUID
    permissions: dict[str, Any]
    created_at: datetime

    # User information (if included)
    user_email: str | None = None
    user_username: str | None = None
    user_display_name: str | None = None


class TripActivityType(str, Enum):
    """Trip activity types."""

    CREATED = "created"
    UPDATED = "updated"
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"
    MEMBER_ROLE_CHANGED = "member_role_changed"
    COMMENT_ADDED = "comment_added"


class TripActivityResponse(BaseModel):
    """Schema for trip activity response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trip_id: uuid.UUID
    user_id: uuid.UUID | None = None
    activity_type: TripActivityType
    activity_data: dict[str, Any]
    created_at: datetime

    # User information (if included)
    user_email: str | None = None
    user_username: str | None = None
