from sqlalchemy import JSON, Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=True, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    created_trips = relationship("Trip", back_populates="creator")
    trip_memberships = relationship("TripMember", back_populates="user")
    trip_activities = relationship("TripActivity", back_populates="user")


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    travel_preferences = Column(JSON, default=dict)
    privacy_settings = Column(JSON, default=dict)

    # Relationships
    user = relationship("User", back_populates="profile")
