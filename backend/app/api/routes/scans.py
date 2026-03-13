from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import uuid
from datetime import datetime, timezone

from app.api.schemas import ScanCreate, ScanOut
from app.utils.user_utils import check_and_reset_api_limit
from app.models.scan import Scan
from app.models.target import Target
from app.models.project import Project
from app.models.user import User
from app.models.recon_enhancement import ReconEnhancementResult
from app.db.session import get_db
from app.dependencies import get_current_user
from app.services.scan_executor import execute_scan
from app.services.risk_history.summarizer import summarize_history
from app.services.risk_explain.recon_explain import explain_recon
from app.services.risk_explain.threat_explain import explain_threat
from app.services.risk_explain.active_explain import explain_active
from app.services.risk_explain.composer import compose_explanation
from app.services.risk_explain.formatter import format_explanation
from app.services.email_service import send_scan_notification
import json

from app.core.tasks import run_scan_task
import json
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/scans", tags=["Scans"])

def _get_risk_explanation(scan, recon_data):
    recon_exp = explain_recon(recon_data)
    threat_exp = explain_threat(scan.threat_summary)
    active_exp = explain_active(scan.aggregated_result)
    
    composed = compose_explanation(recon_exp, threat_exp, active_exp)
    return format_explanation(composed)

@router.get("/{scan_id}/export")
def export_scan_json(
    scan_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == user["sub"],
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Simple JSON export of the entire scan record
    export_data = {
        "scan_id": str(scan.id),
        "target": str(scan.target_id),
        "status": scan.status,
        "profile": scan.profile,
        "results": {
            "aggregated": scan.aggregated_result,
            "threat": scan.threat_summary,
            "passive": scan.passive_summary,
            "risk": scan.risk_summary,
            "ai": scan.ai_summary
        },
        "timestamps": {
            "created": scan.created_at.isoformat() if scan.created_at else None,
            "started": scan.started_at.isoformat() if scan.started_at else None,
            "finished": scan.finished_at.isoformat() if scan.finished_at else None,
        }
    }
    
    return JSONResponse(
        content=export_data,
        headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}.json"}
    )

@router.post(
    "/targets/{target_id}",
    status_code=201
)
def create_scan(
    target_id: UUID,
    data: ScanCreate,
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    user_payload=Depends(get_current_user),
):
    # 🔒 Ownership check
    target = (
        db.query(Target)
        .join(Project)
        .filter(
            Target.id == target_id,
            Project.user_id == user_payload["sub"]
        )
        .first()
    )

    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    # 🛑 API Limit Check
    db_user = db.query(User).filter(User.id == user_payload["sub"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    cost = 2 if data.profile == "full" else 1
    if db_user.api_limit_used + cost > db_user.api_limit_daily:
        raise HTTPException(
            status_code=403, 
            detail=f"API Limit Exceeded. Used: {db_user.api_limit_used}/{db_user.api_limit_daily}. Required: {cost}"
        )

    tool = data.tool
    profile = data.profile

    scan = Scan(
        id=uuid.uuid4(),
        target_id=target.id,
        user_id=user_payload["sub"],
        tool=tool,
        profile=profile,
        status="pending",
    )

    print(f"[SCAN_START] Initializing scan for target: {target.value}")

    try:
        # Increment limit
        print(f"[LIMIT] Pre-update: {db_user.email} used {db_user.api_limit_used}")
        db_user.api_limit_used += cost
        db.add(db_user)
        db.add(scan)
        db.commit()
        db.refresh(db_user)
        print(f"[LIMIT] Post-update: {db_user.email} used {db_user.api_limit_used}")
        db.refresh(scan)
        print(f"[SCAN_START] DB commit success for scan_id: {scan.id}")
    except Exception as e:
        print(f"[SCAN_START] DB commit FAILED: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database persistence failed")

    # 🚀 Background execution via abstraction layer
    run_scan_task(
        background_tasks,
        scan.id,
        tool,
        target.value,
        user_payload["sub"],
    )
    
    # Notify admin about new scan
    background_tasks.add_task(
        send_scan_notification,
        db_user.email,
        target.value,
        profile
    )

    return {
        "scan_id": str(scan.id),
        "status": scan.status,
    }


@router.get("/{scan_id}/status")
def get_scan_status(
    scan_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    db.expire_all()
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == user["sub"],
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    db.refresh(scan)
        
    return {
        "scan_id": str(scan.id),
        "status": scan.status,
        "progress": scan.progress,
        "current_layer": scan.current_phase, # Aliased for frontend compatibility
        "error": scan.error
    }


@router.get(
    "",
    response_model=List[ScanOut]
)
def get_all_user_scans(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    scans_with_targets = (
        db.query(Scan, Target.value)
        .join(Target, Scan.target_id == Target.id)
        .filter(Scan.user_id == user["sub"])
        .order_by(Scan.created_at.desc())
        .all()
    )
    
    results = []
    for scan, target_value in scans_with_targets:
        scan.target_value = target_value
        results.append(scan)
        
    return results


@router.get(
    "/targets/{target_id}",
    response_model=List[ScanOut]
)
def get_scans(
    target_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Verify ownership
    target = (
        db.query(Target)
        .join(Project)
        .filter(
            Target.id == target_id,
            Project.user_id == user["sub"],
        )
        .first()
    )
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    scans = db.query(Scan).filter(Scan.target_id == target_id).all()
    history = summarize_history(scans)
    
    # Pre-fetch recon enhancements for this target/user
    enhancements = (
        db.query(ReconEnhancementResult)
        .filter(
            ReconEnhancementResult.target == target.value,
            ReconEnhancementResult.user_id == user["sub"]
        )
        .all()
    )
    recon_data = {r.module: r.summary for r in enhancements}
    
    for scan in scans:
        scan.target_value = target.value
        scan.risk_history = history
        scan.risk_explanation = _get_risk_explanation(scan, recon_data)
        
        # Populate subdomains
        from app.models.subdomain import Subdomain
        sub_objs = db.query(Subdomain).filter(Subdomain.scan_id == scan.id).all()
        scan.subdomains = [s.subdomain for s in sub_objs]
        
    return scans


@router.get(
    "/{scan_id}",
    response_model=ScanOut
)
def get_scan(
    scan_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # 🔒 Verify scan belongs to user
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == user["sub"],
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Refresh to ensure we have background-updated fields
    db.refresh(scan)
    
    # Fetch target for recon data and target_value
    target = db.query(Target).filter(Target.id == scan.target_id).first()
    if target:
        scan.target_value = target.value
    
    # Fetch all scans for this target to compute history
    all_target_scans = db.query(Scan).filter(Scan.target_id == scan.target_id).all()
    
    # Fetch recon enhancements
    enhancements = (
        db.query(ReconEnhancementResult)
        .filter(
            ReconEnhancementResult.target == target.value if target else "",
            ReconEnhancementResult.user_id == user["sub"]
        )
        .all()
    )
    recon_data = {r.module: r.summary for r in enhancements}

    scan.risk_history = summarize_history(all_target_scans)
    scan.risk_explanation = _get_risk_explanation(scan, recon_data)
    
    # Populate subdomains
    from app.models.subdomain import Subdomain
    sub_objs = db.query(Subdomain).filter(Subdomain.scan_id == scan.id).all()
    scan.subdomains = [s.subdomain for s in sub_objs]
    
    return scan
    