from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.project import Project
from app.dependencies import get_current_user
from app.api.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut

router = APIRouter()


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    project = Project(
        name=data.name,
        description=data.description,
        user_id=user["sub"],
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=List[ProjectOut])
def get_projects(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return (
        db.query(Project)
        .filter(Project.user_id == user["sub"])
        .all()
    )


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user["sub"],
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user["sub"],
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()