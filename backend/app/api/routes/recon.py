from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.services.passive_recon.runner import run_passive_recon
from app.services.threat_intel.runner import run_threat_intel
from app.services.recon_enhancements.runner import run_wayback_recon, run_recon_enhancements

router = APIRouter(prefix="/recon", tags=["Recon"])


@router.get("/passive")
def get_passive_recon(
    target: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return run_passive_recon(target, db=db, user_id=user["sub"])


@router.get("/threat")
def get_threat_intel(
    target: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return run_threat_intel(target, db=db, user_id=user["sub"])


@router.get("/enhanced/wayback")
def wayback_recon(
    target: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return run_wayback_recon(
        target=target,
        db=db,
        user_id=user["sub"],
    )


@router.get("/enhanced/full")
def enhanced_recon(
    target: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return run_recon_enhancements(
        target=target,
        db=db,
        user_id=user["sub"]
    )
