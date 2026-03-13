from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class Subdomain(Base):
    __tablename__ = "subdomains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), nullable=False)
    subdomain = Column(String, nullable=False)
