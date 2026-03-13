from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class TargetCreate(BaseModel):
    value: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Domain or IP (example.com)"
    )


class TargetOut(BaseModel):
    id: UUID
    project_id: UUID
    value: str
    created_at: datetime

    class Config:
        from_attributes = True
