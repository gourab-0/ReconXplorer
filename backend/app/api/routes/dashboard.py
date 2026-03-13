from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from typing import List, Dict, Any

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.scan import Scan
from app.models.target import Target
from app.models.project import Project
from app.models.user import User
from app.models.vulnerability import Vulnerability
from app.utils.user_utils import check_and_reset_api_limit

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    user_payload=Depends(get_current_user),
):
    user_id = user_payload["sub"]
    db_user = db.query(User).filter(User.id == user_id).first()
    
    # 1. Total Scans
    total_scans = db.execute(text("SELECT count(*) FROM scans WHERE user_id = :user_id"), {"user_id": user_id}).scalar() or 0

    # 2. Critical Risks
    critical_risks = 0
    try:
        critical_risks = db.execute(
            text("SELECT count(*) FROM scans WHERE user_id = :user_id AND lower(risk_level) = 'critical'"),
            {"user_id": user_id}
        ).scalar() or 0
    except Exception:
        db.rollback()

    # 3. Active Targets
    active_targets = db.query(Target).join(Project).filter(
        Project.user_id == user_id
    ).count()

    # 4. Total Vulnerabilities found across all scans
    total_vulns = 0
    try:
        total_vulns = (
            db.query(Vulnerability)
            .join(Scan, Vulnerability.scan_id == Scan.id)
            .filter(Scan.user_id == user_id)
            .count()
        )
    except Exception:
        db.rollback()

    # 5. Recent Scans
    recent_scans = []
    try:
        # Fetching specific columns to avoid missing ones like ai_summary
        recent_scans_raw = db.execute(
            text("""
                SELECT s.id, t.value as target, s.status, s.risk_level, s.created_at, s.risk_score 
                FROM scans s 
                JOIN targets t ON s.target_id = t.id 
                WHERE s.user_id = :user_id 
                ORDER BY s.created_at DESC 
                LIMIT 5
            """),
            {"user_id": user_id}
        ).fetchall()

        for row in recent_scans_raw:
            recent_scans.append({
                "id": str(row.id),
                "target": row.target,
                "status": row.risk_level if row.status == "completed" else row.status,
                "date": row.created_at.isoformat() if row.created_at else None,
                "risk_score": row.risk_score
            })
    except Exception:
        db.rollback()

    if total_scans > 0:
        avg_risk = 0
        try:
            # We calculate health based on scans from the last 30 days.
            # We weight serious risks more than minor ones for a more intuitive "Health" score.
            avg_risk = db.execute(
                text("""
                    SELECT AVG(
                        CASE 
                            WHEN risk_score >= 60 THEN risk_score 
                            WHEN risk_score >= 30 THEN risk_score * 0.4
                            ELSE risk_score * 0.1 
                        END
                    ) FROM scans 
                    WHERE user_id = :user_id 
                    AND created_at > (now() - interval '30 days')
                """),
                {"user_id": user_id}
            ).scalar()
            
            # If no recent scans, fallback to all-time average but still weighted
            if avg_risk is None:
                avg_risk = db.execute(
                    text("""
                        SELECT AVG(
                            CASE 
                                WHEN risk_score >= 60 THEN risk_score 
                                WHEN risk_score >= 30 THEN risk_score * 0.4
                                ELSE risk_score * 0.1 
                            END
                        ) FROM scans WHERE user_id = :user_id
                    """),
                    {"user_id": user_id}
                ).scalar() or 0
                
        except Exception:
            db.rollback()
        
        health_score = max(0, 100 - int(avg_risk))
    else:
        health_score = 100

    return {
        "stats": {
            "totalScans": total_scans,
            "criticalRisks": critical_risks,
            "activeTargets": active_targets,
            "healthScore": health_score,
            "apiUsed": db_user.api_limit_used if db_user else 0,
            "apiLimit": db_user.api_limit_daily if db_user else 50,
            "vulnerabilities": total_vulns,
            "assets": active_targets
        },
        "recentScans": recent_scans
    }
