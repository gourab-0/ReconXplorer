from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    api_limit_daily = Column(Integer, default=12)
    api_limit_used = Column(Integer, default=0)
    api_key = Column(String, unique=True, nullable=True)
    last_limit_reset = Column(DateTime(timezone=True), server_default=func.now())
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Email verification
    verification_token = Column(String, nullable=True, index=True)
    verification_expiry = Column(DateTime(timezone=True), nullable=True)
    is_verified = Column(Boolean, default=False)

    # Security: Account Lockout
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String, nullable=True)
