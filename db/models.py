from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    owner = Column(String, nullable=False)
    bucket_capacity = Column(Integer, nullable=False)
    refill_rate = Column(Float, nullable=False)  # Tokens generated per second
    created_at = Column(DateTime, default=datetime.utcnow)

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)
    endpoint = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    allowed = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
