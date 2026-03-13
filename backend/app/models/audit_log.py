from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    target_user = Column(String, nullable=True) # User email or ID
    details = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
