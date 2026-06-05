from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Bin(Base):
    __tablename__ = "bins"

    bin_id          = Column(String, primary_key=True, index=True)
    name            = Column(String, nullable=False)
    neighborhood    = Column(String, nullable=False)
    lat             = Column(Float, nullable=False)
    lon             = Column(Float, nullable=False)
    capacity_kg     = Column(Float, nullable=False)
    is_market_area  = Column(Boolean, default=False)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    reports = relationship("CommunityReport", back_populates="bin")


class WasteReading(Base):
    __tablename__ = "waste_readings"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    bin_id          = Column(String, ForeignKey("bins.bin_id"), nullable=False)
    timestamp       = Column(DateTime, default=datetime.utcnow)
    waste_level_kg  = Column(Float, nullable=False)
    fill_percentage = Column(Float, nullable=False)
    predicted_fill  = Column(Float, nullable=True)
    day_of_week     = Column(Integer, nullable=True)
    hour            = Column(Integer, nullable=True)
    is_weekend      = Column(Boolean, default=False)


class CommunityReport(Base):
    __tablename__ = "community_reports"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    report_id   = Column(String, unique=True, nullable=False)
    bin_id      = Column(String, ForeignKey("bins.bin_id"), nullable=False)
    reporter    = Column(String, nullable=False)
    phone       = Column(String, nullable=True)
    message     = Column(Text, nullable=False)
    fill_level  = Column(Float, nullable=True)
    timestamp   = Column(DateTime, default=datetime.utcnow)
    status      = Column(String, default="received")

    bin = relationship("Bin", back_populates="reports")


class Route(Base):
    __tablename__ = "routes"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    route_date      = Column(DateTime, default=datetime.utcnow)
    truck_id        = Column(String, nullable=False)
    total_bins      = Column(Integer, nullable=False)
    total_load_kg   = Column(Float, nullable=False)
    distance_km     = Column(Float, nullable=False)
    stops           = Column(Text, nullable=False)
    status          = Column(String, default="planned")