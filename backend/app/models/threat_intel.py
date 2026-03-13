from sqlalchemy import Column, DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class ThreatIntelResult(Base):
    __tablename__ = "threat_intel_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ownership
    user_id = Column(UUID(as_uuid=True), nullable=False)

    # Target info
    target = Column(String, nullable=False)
    resolved_ip = Column(String)

    # Normalized verdict
    risk_score = Column(String, nullable=False)
    verdict = Column(String, nullable=False)
    confidence = Column(String, nullable=False)

    # Details
    signals = Column(JSON, nullable=False)
    tags = Column(JSON, nullable=False)
    sources = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())