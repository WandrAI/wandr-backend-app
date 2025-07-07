from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from enum import Enum
import uuid


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
    description: Optional[str] = Field(None, max_length=1000, description="Trip description")
    start_date: Optional[date] = Field(None, description="Trip start date")
    end_date: Optional[date] = Field(None, description="Trip end date")
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if v and values.get('start_date') and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class TripCreate(TripBase):
    """Schema for creating a trip."""
    trip_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional trip data")


class TripUpdate(BaseModel):
    """Schema for updating a trip."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[TripStatus] = None
    trip_data: Optional[Dict[str, Any]] = None
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if v and values.get('start_date') and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class TripResponse(TripBase):
    """Schema for trip response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    status: TripStatus
    created_by: uuid.UUID
    trip_data: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional nested data
    member_count: Optional[int] = Field(None, description="Number of trip members")
    user_role: Optional[TripMemberRole] = Field(None, description="Current user's role in this trip")


class TripListResponse(BaseModel):
    """Schema for trip list response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: TripStatus
    created_by: uuid.UUID
    created_at: datetime
    member_count: Optional[int] = None
    user_role: Optional[TripMemberRole] = None


class TripMemberBase(BaseModel):
    """Base trip member schema."""
    user_id: uuid.UUID
    role: TripMemberRole = TripMemberRole.PARTICIPANT


class TripMemberCreate(TripMemberBase):
    """Schema for adding a trip member."""
    permissions: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TripMemberUpdate(BaseModel):
    """Schema for updating a trip member."""
    role: Optional[TripMemberRole] = None
    permissions: Optional[Dict[str, Any]] = None


class TripMemberResponse(TripMemberBase):
    """Schema for trip member response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    trip_id: uuid.UUID
    permissions: Dict[str, Any]
    created_at: datetime
    
    # User information (if included)
    user_email: Optional[str] = None
    user_username: Optional[str] = None
    user_display_name: Optional[str] = None


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
    user_id: Optional[uuid.UUID] = None
    activity_type: TripActivityType
    activity_data: Dict[str, Any]
    created_at: datetime
    
    # User information (if included)
    user_email: Optional[str] = None
    user_username: Optional[str] = None