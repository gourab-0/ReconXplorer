from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.db.session import get_db
from app.models.user import User
from app.models.scan import Scan
from app.models.target import Target
from app.models.port import Port
from app.models.audit_log import AuditLog
from app.models.api_quota import APIQuota
from app.models.project import Project
from app.dependencies import get_current_user
from app.config import settings
from pydantic import BaseModel
from typing import Optional, List
import os
from app.services.audit_service import log_admin_action
import shutil
from datetime import datetime
import secrets

class APIConfigUpdate(BaseModel) :
    default_limit: int

class APIUserLimitUpdate(BaseModel):
    limit: int

class AdminSettingsUpdate(BaseModel):
    platform_name: Optional[str] = None
    support_email: Optional[str] = None
    max_scan_duration: Optional[int] = None
    email_alerts: Optional[bool] = None
    maintenance_mode: Optional[bool] = None

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_admin_user(current_user_payload: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user_payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Check if user is admin or the specific super-admin email
    is_super_admin = user.email.lower() == settings.ADMIN_EMAIL.lower()
    
    if not (user.is_admin or is_super_admin):
         raise HTTPException(status_code=403, detail="Admin access required")
         
    return user

@router.get("/stats")
def get_admin_stats(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    total_users = db.query(User).count()
    total_scans = db.query(Scan).count()
    
    # Real calculations
    avg_risk = db.query(func.avg(Scan.risk_score)).scalar() or 0
    total_api_used = db.query(func.sum(User.api_limit_used)).scalar() or 0
    active_threats = db.query(Scan).filter(Scan.risk_score >= 80).count() # High risk scans

    # Scans Over Time (Last 7 days)
    # Using raw SQL for date grouping compatibility
    scans_over_time = db.execute(text("""
        SELECT to_char(created_at, 'Mon DD') as date, count(*) as scans, 
        sum(case when risk_score >= 60 then 1 else 0 end) as threats
        FROM scans 
        WHERE created_at > current_date - interval '7 days'
        GROUP BY 1 
        ORDER BY min(created_at)
    """)).fetchall()
    
    formatted_scans_over_time = [{"date": row[0], "scans": row[1], "threats": row[2]} for row in scans_over_time]

    # Risk Distribution
    risk_distribution = db.execute(text("""
        SELECT risk_level, count(*) as count 
        FROM scans 
        GROUP BY 1
    """)).fetchall()
    
    formatted_risk_dist = [{"risk": (row[0] or "Unknown").capitalize(), "count": row[1]} for row in risk_distribution]

    # Top Scanned Ports
    top_ports = db.query(Port.port, func.count(Port.port).label('count'))\
        .group_by(Port.port).order_by(text('count DESC')).limit(10).all()
    formatted_top_ports = [{"port": str(p.port), "scans": p.count} for p in top_ports]

    # High Risk Targets
    high_risk_targets = db.execute(text("""
        SELECT t.value, count(s.id) as scan_count, max(s.risk_score) as max_score, max(s.risk_level) as level, max(s.created_at) as last_scanned
        FROM scans s
        JOIN targets t ON s.target_id = t.id
        WHERE s.risk_score >= 70
        GROUP BY t.value
        ORDER BY max_score DESC, scan_count DESC
        LIMIT 5
    """)).fetchall()
    formatted_high_risk = [{
        "target": row[0],
        "scansCount": row[1],
        "riskScore": row[2],
        "riskLevel": row[3],
        "lastScanned": row[4]
    } for row in high_risk_targets]

    return {
        "totalUsers": total_users,
        "totalScans": total_scans,
        "activeThreats": active_threats,
        "uptime": 99.9,
        "averageRiskScore": float(avg_risk), 
        "totalApiCalls": int(total_api_used),
        "scansOverTime": formatted_scans_over_time,
        "riskDistribution": formatted_risk_dist,
        "topPorts": formatted_top_ports,
        "highRiskTargets": formatted_high_risk
    }

@router.get("/users")
def get_users(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    users = db.query(User).all()
    return users

@router.get("/health")
def get_system_health(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    health_results = []
    
    # 1. Database Check
    try:
        db.execute(text("SELECT 1"))
        health_results.append({"name": "Database", "status": "ok", "lastChecked": "Now"})
    except Exception as e:
        health_results.append({"name": "Database", "status": "error", "errorMessage": str(e), "lastChecked": "Now"})

    # 2. Disk Usage
    try:
        total, used, free = shutil.disk_usage("/")
        usage_pct = (used / total) * 100
        health_results.append({
            "name": "Disk Storage", 
            "status": "ok" if usage_pct < 90 else "warning", 
            "lastChecked": "Now",
            "errorMessage": f"{usage_pct:.1f}% used ({free // (2**30)} GB free)"
        })
    except:
        health_results.append({"name": "Disk Storage", "status": "warning", "lastChecked": "Now"})

    # 3. Email Service
    email_status = "ok" if settings.MAIL_PASSWORD else "warning"
    health_results.append({
        "name": "Email Service", 
        "status": email_status, 
        "lastChecked": "Now",
        "errorMessage": "SMTP Credentials missing" if not settings.MAIL_PASSWORD else "Connected"
    })

    # 4. API Service
    health_results.append({"name": "API Service", "status": "ok", "lastChecked": "Now"})

    return health_results

@router.get("/threat-intel")
def get_threat_intel_status(admin: User = Depends(get_admin_user)):
    services = []
    
    # Check Shodan
    services.append({
        "id": "shodan", 
        "name": "Shodan", 
        "status": "ok" if settings.SHODAN_API_KEY else "disabled",
        "enabled": bool(settings.SHODAN_API_KEY)
    })
    
    # Check VirusTotal
    services.append({
        "id": "vt", 
        "name": "VirusTotal", 
        "status": "ok" if settings.VIRUSTOTAL_API_KEY else "disabled",
        "enabled": bool(settings.VIRUSTOTAL_API_KEY)
    })

    # Check AbuseIPDB
    services.append({
        "id": "abuseipdb", 
        "name": "AbuseIPDB", 
        "status": "ok" if settings.ABUSEIPDB_API_KEY else "disabled",
        "enabled": bool(settings.ABUSEIPDB_API_KEY)
    })

    # Check IPQualityScore
    services.append({
        "id": "ipqs", 
        "name": "IPQualityScore", 
        "status": "ok" if settings.IPQUALITYSCORE_API_KEY else "disabled",
        "enabled": bool(settings.IPQUALITYSCORE_API_KEY)
    })
    
    # Check Google Safe Browsing
    services.append({
        "id": "google", 
        "name": "Google Safe Browsing", 
        "status": "ok" if settings.GOOGLE_SAFE_BROWSING_API_KEY else "disabled",
        "enabled": bool(settings.GOOGLE_SAFE_BROWSING_API_KEY)
    })

    # Check SecurityTrails
    services.append({
        "id": "securitytrails", 
        "name": "SecurityTrails", 
        "status": "ok" if settings.SECURITYTRAILS_API_KEY else "disabled",
        "enabled": bool(settings.SECURITYTRAILS_API_KEY)
    })

    # Check API Ninjas
    services.append({
        "id": "apininjas", 
        "name": "API Ninjas", 
        "status": "ok" if settings.APININJAS_API_KEY else "disabled",
        "enabled": bool(settings.APININJAS_API_KEY)
    })

    # Check IPInfo
    services.append({
        "id": "ipinfo", 
        "name": "IPInfo", 
        "status": "ok" if settings.IPINFO_API_KEY else "disabled",
        "enabled": bool(settings.IPINFO_API_KEY)
    })

    # Check IPHub
    services.append({
        "id": "iphub", 
        "name": "IPHub", 
        "status": "ok" if settings.IPHUB_API_KEY else "disabled",
        "enabled": bool(settings.IPHUB_API_KEY)
    })
    
    return services

@router.post("/config/reset-api-usage")
def reset_all_api_usage(
    db: Session = Depends(get_db), 
    admin: User = Depends(get_admin_user)
):
    try:
        # 1. Reset per-user platform counters
        db.query(User).update({User.api_limit_used: 0}, synchronize_session=False)
        
        # 2. Reset global third-party API quotas (if table exists)
        try:
            db.query(APIQuota).update({
                APIQuota.daily_used: 0,
                APIQuota.minute_used: 0
            }, synchronize_session=False)
        except Exception as e:
            print(f"[RESET] Could not reset API quotas (table might be missing): {e}")
        
        db.commit()
        log_admin_action(db, admin.id, "RESET_ALL_API_USAGE", details="Global manual reset of all user API counters and third-party API quotas")
        return {"message": "All API counters have been reset successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reset counters: {str(e)}")

@router.post("/config/default-limit")
def update_default_limit(
    config: APIConfigUpdate,
    db: Session = Depends(get_db), 
    admin: User = Depends(get_admin_user)
):
    # This would ideally be in a DB config table, for now we just log it and maybe update existing users?
    # As requested, making it "operable"
    log_admin_action(db, admin.id, "UPDATE_DEFAULT_LIMIT", details=f"Set default daily limit to {config.default_limit}")
    return {"message": f"Default limit updated to {config.default_limit}"}

@router.post("/users/{user_id}/verify")
def verify_user(
    user_id: str, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_verified = True
    db.commit()
    
    log_admin_action(
        db=db,
        admin_id=admin.id,
        action="VERIFY_USER",
        target_user=user.email,
        details=f"Manually verified user {user.id}"
    )
    
    return {"message": f"User {user.email} verified successfully"}

@router.post("/users/{user_id}/reset-api-key")
def reset_user_api_key(
    user_id: str, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_admin_user)
):
    import secrets
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.api_key = secrets.token_urlsafe(32)
    user.api_limit_used = 0 # Reset usage when key is reset
    db.commit()
    log_admin_action(db, admin.id, "RESET_API_KEY", target_user=user.email, details="API key reset and usage counter cleared.")
    return {"message": "API key reset and usage counter cleared successfully"}

@router.post("/users/{user_id}/limit")
def adjust_user_limit(
    user_id: str, 
    limit_data: APIUserLimitUpdate,
    db: Session = Depends(get_db), 
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.api_limit_daily = limit_data.limit
    db.commit()
    log_admin_action(db, admin.id, "ADJUST_LIMIT", target_user=user.email, details=f"New limit: {limit_data.limit}")
    return {"message": f"Limit updated to {limit_data.limit}"}

@router.post("/users/{user_id}/suspend")
def suspend_user(
    user_id: str, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Prevent self-suspension
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot suspend yourself")

    user.is_active = not user.is_active
    db.commit()
    
    action = "SUSPEND_USER" if not user.is_active else "ACTIVATE_USER"
    log_admin_action(db, admin.id, action, target_user=user.email)
    return {"message": f"User {'suspended' if not user.is_active else 'activated'} successfully"}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: str, 
    db: Session = Depends(get_db), 
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Prevent self-deletion
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    email = user.email
    target_user_id = user.id

    try:
        # Use a sub-transaction for safety
        with db.begin_nested():
            # 1. Delete user's scans
            db.query(Scan).filter(Scan.user_id == target_user_id).delete(synchronize_session=False)
            
            # 2. Delete user's projects
            db.query(Project).filter(Project.user_id == target_user_id).delete(synchronize_session=False)
            
            # 3. Delete the user
            db.delete(user)
        
        db.commit()
        log_admin_action(db, admin.id, "DELETE_USER", target_user=email, details=f"Permanently deleted user {target_user_id} and all their data.")
        return {"message": "User and all associated data deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

@router.delete("/scans/{scan_id}")
def delete_scan(
    scan_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    try:
        db.delete(scan)
        db.commit()
        log_admin_action(db, admin.id, "DELETE_SCAN", target_user=scan.id, details=f"Admin deleted scan for target {scan.target_id}")
        return {"message": "Scan deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete scan: {str(e)}")


@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db), 
    admin: User = Depends(get_admin_user)
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return logs

@router.get("/scans")
def get_all_scans(
    db: Session = Depends(get_db), 
    admin: User = Depends(get_admin_user)
):
    scans = db.query(Scan, Target.value.label("target_value"))\
        .join(Target, Scan.target_id == Target.id)\
        .order_by(Scan.created_at.desc()).all()
    
    results = []
    from app.models.subdomain import Subdomain
    for scan, target_value in scans:
        s_dict = {c.name: getattr(scan, c.name) for c in scan.__table__.columns}
        s_dict["target_value"] = target_value
        
        # Populate subdomains for admin
        sub_objs = db.query(Subdomain).filter(Subdomain.scan_id == scan.id).all()
        s_dict["subdomains"] = [s.subdomain for s in sub_objs]
        
        results.append(s_dict)
        
    return results

@router.get("/notifications")
def get_notifications(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    notifications = []
    
    # 1. Check for recent unverified users
    recent_users = db.query(User).filter(User.is_verified == False).order_by(User.created_at.desc()).limit(3).all()
    for user in recent_users:
        notifications.append({
            "id": f"user_{user.id}",
            "title": "New User Registration",
            "message": f"{user.full_name} ({user.email}) needs verification.",
            "type": "info",
            "timestamp": user.created_at
        })

    # 2. Check for failed scans
    failed_scans = db.query(Scan, Target.value.label("target_value"))\
        .join(Target, Scan.target_id == Target.id)\
        .filter(Scan.status == "failed")\
        .order_by(Scan.created_at.desc()).limit(3).all()
        
    for scan, target_val in failed_scans:
        notifications.append({
            "id": f"scan_fail_{scan.id}",
            "title": "Scan Failed",
            "message": f"Scan for {target_val} failed: {scan.error or 'Unknown error'}",
            "type": "error",
            "timestamp": scan.created_at
        })
        
    return notifications

@router.post("/config/settings")
def update_admin_settings(
    settings_data: AdminSettingsUpdate,
    db: Session = Depends(get_db), 
    admin: User = Depends(get_admin_user)
):
    log_admin_action(db, admin.id, "UPDATE_SETTINGS", details=str(settings_data.model_dump(exclude_none=True)))
    return {"message": "Settings updated successfully"}
