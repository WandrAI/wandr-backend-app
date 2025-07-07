from sqlalchemy import Column, String, UniqueConstraint, Float, JSON
from app.models.base import BaseModel


class Location(BaseModel):
    __tablename__ = "locations"
    
    name = Column(String, nullable=False)
    location_type = Column(String, nullable=True)  # city, country, poi, accommodation
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(JSON, default=dict)
    place_data = Column(JSON, default=dict)  # External API data (Google Places, etc.)
    
    __table_args__ = (
        UniqueConstraint("name", "latitude", "longitude", name="unique_location"),
    )