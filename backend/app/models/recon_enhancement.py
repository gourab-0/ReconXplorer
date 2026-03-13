from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class ReconEnhancementResult(Base):
    __tablename__ = "recon_enhancement_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    target = Column(String, nullable=False)
    module = Column(String, nullable=False)  # wayback | dns | ssl | harvester

    summary = Column(JSON, nullable=False)
    sources = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
