from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True