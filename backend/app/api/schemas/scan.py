from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime


class ScanCreate(BaseModel):
    tool: str = Field(
        ...,
        description="Scan tool (nmap, whatweb, etc.)"
    )
    profile: str = Field(
        default="full",
        description="Scan profile (passive, active, full)"
    )


class ScanOut(BaseModel):
    id: UUID
    target_id: UUID
    target_value: Optional[str] = None
    resolved_ip: Optional[str] = None
    tool: str
    profile: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    summary: Optional[str] = None
    result: Optional[Dict] = None
    output: Optional[str] = None
    error: Optional[str] = None

    # Core Result Summaries
    passive_summary: Optional[Dict[str, Any]] = None
    threat_summary: Optional[Dict[str, Any]] = None
    aggregated_result: Optional[Dict[str, Any]] = None

    # Risk Analysis (Phase 2.5 & 2.6)
    risk_summary: Dict[str, Any] = Field(default_factory=dict)
    risk_score: int = Field(default=0)
    risk_level: str = Field(default="low")
    risk_history: Dict[str, Any] = Field(default_factory=dict)
    risk_explanation: Dict[str, Any] = Field(default_factory=dict)

    # AI Insights
    ai_summary: Optional[str] = None
    
    # New Recon Data
    subdomains: Optional[list[str]] = None

    @field_validator("risk_summary", "risk_history", "risk_explanation", mode="before")
    @classmethod
    def ensure_dict(cls, v: Any) -> Dict[str, Any]:
        return v if v is not None else {}

    @field_validator("risk_score", mode="before")
    @classmethod
    def ensure_int(cls, v: Any) -> int:
        return v if v is not None else 0

    @field_validator("risk_level", mode="before")
    @classmethod
    def ensure_str(cls, v: Any) -> str:
        return v if v is not None else "low"

    class Config:
        from_attributes = True
