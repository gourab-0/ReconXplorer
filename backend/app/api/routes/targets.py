from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.models.target import Target
from app.models.project import Project
from app.dependencies import get_current_user
from app.api.schemas.target import TargetCreate, TargetOut

router = APIRouter(
    prefix="/projects/{project_id}/targets",
    tags=["Targets"],
)


# ---------------- CREATE TARGET ----------------
@router.post(
    "",
    response_model=TargetOut,
    status_code=status.HTTP_201_CREATED,
)
def create_target(
    project_id: UUID,
    data: TargetCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # 🔒 Ensure project belongs to user
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user["sub"],
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    target = Target(
        project_id=project.id,
        value=data.value,
    )

    db.add(target)
    db.commit()
    db.refresh(target)
    return target


# ---------------- LIST TARGETS ----------------
@router.get(
    "",
    response_model=List[TargetOut],
)
def list_targets(
    project_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # 🔒 Verify ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user["sub"],
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return db.query(Target).filter(
        Target.project_id == project.id
    ).all()
