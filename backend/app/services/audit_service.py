from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

def log_admin_action(
    db: Session,
    admin_id: str,
    action: str,
    target_user: str = None,
    details: str = None,
    ip_address: str = None
):
    try:
        log = AuditLog(
            admin_id=admin_id,
            action=action,
            target_user=target_user,
            details=details,
            ip_address=ip_address
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"[AUDIT] Failed to log action: {e}")
        db.rollback()
