from sqlalchemy import Column, String, DateTime, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class ScanCache(Base):
    __tablename__ = "scan_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target = Column(String, index=True, nullable=False)
    api_name = Column(String, index=True, nullable=False)
    data = Column(JSONB, nullable=False)
    cached_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
