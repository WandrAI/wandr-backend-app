from sqlalchemy import Column, String, Date, ForeignKey, Text, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Trip(BaseModel):
    __tablename__ = "trips"
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String, default="planning")  # planning, active, completed, cancelled
    trip_data = Column(JSON, default=dict)  # Flexible trip details, itinerary, budget
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="created_trips")
    members = relationship("TripMember", back_populates="trip")
    activities = relationship("TripActivity", back_populates="trip")


class TripMember(BaseModel):
    __tablename__ = "trip_members"
    
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # organizer, participant, viewer
    permissions = Column(JSON, default=dict)  # Custom permissions per member
    
    # Relationships
    trip = relationship("Trip", back_populates="members")
    user = relationship("User", back_populates="trip_memberships")
    
    __table_args__ = (
        UniqueConstraint("trip_id", "user_id", name="unique_trip_member"),
    )


class TripActivity(BaseModel):
    __tablename__ = "trip_activities"
    
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    activity_type = Column(String, nullable=False)  # created, updated, joined, comment, etc.
    activity_data = Column(JSON, default=dict)
    
    # Relationships
    trip = relationship("Trip", back_populates="activities")
    user = relationship("User", back_populates="trip_activities")