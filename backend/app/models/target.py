from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class Target(Base):
    __tablename__ = "targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    value = Column(String, nullable=False)  # GENERIC TARGET
    created_at = Column(DateTime(timezone=True), server_default=func.now())
