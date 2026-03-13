from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class APIQuota(Base):
    __tablename__ = "api_quotas"

    api_name = Column(String, primary_key=True)
    daily_limit = Column(Integer, nullable=True)
    monthly_limit = Column(Integer, nullable=True)
    per_minute_limit = Column(Integer, nullable=True)
    
    daily_used = Column(Integer, default=0)
    monthly_used = Column(Integer, default=0)
    minute_used = Column(Integer, default=0)
    
    last_daily_reset = Column(DateTime(timezone=True), server_default=func.now())
    last_monthly_reset = Column(DateTime(timezone=True), server_default=func.now())
    last_minute_reset = Column(DateTime(timezone=True), server_default=func.now())
