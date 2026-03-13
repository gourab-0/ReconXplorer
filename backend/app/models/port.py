from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class Port(Base):
    __tablename__ = "ports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), nullable=False)
    port = Column(Integer)
    protocol = Column(String)
    service = Column(String)
