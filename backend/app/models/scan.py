from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class Scan(Base):
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    target_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)

    tool = Column(String, nullable=False)
    profile = Column(String, default="full") # passive | active | full
    status = Column(String, default="pending")
    current_phase = Column(String, nullable=True) # Identifying | Passive Recon | Threat Intel | Active Scan | Finalizing
    progress = Column(Integer, default=0)

    # Resolution
    resolved_ip = Column(String, nullable=True)

    # Active scan output
    output = Column(String, nullable=True)
    error = Column(String, nullable=True)
    result_path = Column(String, nullable=True)  # Path to XML/JSON output file

    # Passive recon snapshot (optional but powerful)
    passive_summary = Column(JSON, nullable=True)
    threat_summary = Column(JSON, nullable=True)
    aggregated_result = Column(JSON, nullable=True)

    # Risk Analysis (Phase 2.5)
    risk_summary = Column(JSON, nullable=True)
    risk_score = Column(Integer, nullable=True)
    risk_level = Column(String, nullable=True)

    # AI Insights
    ai_summary = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def summary(self):
        return None

    @property
    def result(self):
        return None