from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from database import Base
from datetime import datetime, timezone

class TripHistory(Base):
    __tablename__ = "trip_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)

    #  JSON arrays storing coordinates ([lat, lng])
    origin_coords = Column(JSON)
    destination_coords = Column(JSON)

    # Location names
    origin_name = Column(String)
    destination_name = Column(String, index=True)

    # Routing details
    via_road_name = Column(String)
    route_options = Column(String) # Ex. recommended, fastest, etc.

    # JSON arrays storing preferences
    avoid_roads = Column(JSON, default=list)
    avoid_features = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SavedPlace(Base):
    __tablename__ = "saved_places"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    label = Column(String)
    lat = Column(Float)
    lng = Column(Float)