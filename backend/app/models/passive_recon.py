from sqlalchemy import Column, DateTime, JSON, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class PassiveReconResult(Base):
    __tablename__ = "passive_recon_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), nullable=False)
    target = Column(String, nullable=False)
    resolved_ip = Column(String)

    summary = Column(JSON, nullable=False)
    sources = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
