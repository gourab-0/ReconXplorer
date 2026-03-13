from sqlalchemy import Column, DateTime, JSON, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class ActiveScanResult(Base):
    __tablename__ = "active_scan_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)

    tool = Column(String, nullable=False)  # nmap / whatweb
    raw_output = Column(String)            # full stdout (debug/audit)
    parsed_result = Column(JSON, nullable=False)

    severity = Column(String)              # low / medium / high
    findings_count = Column(String)        # optional quick stats

    created_at = Column(DateTime(timezone=True), server_default=func.now())
