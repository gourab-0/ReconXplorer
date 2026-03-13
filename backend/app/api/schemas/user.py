from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    organization: Optional[str] = None
    is_admin: bool
    is_verified: bool
    api_limit_daily: int
    api_limit_used: int
    last_limit_reset: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    organization: Optional[str] = None
