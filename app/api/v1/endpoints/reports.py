from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.models.report import ReportStatus

router = APIRouter()

from app.core import rate_limit

@router.post("/", response_model=schemas.report.Report, dependencies=[Depends(rate_limit.rate_limit_reports)])
def create_report(
    *,
    db: Session = Depends(deps.get_db),
    report_in: schemas.report.ReportCreate,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Reportar una publicación ofensiva o inapropiada.
    """
    post = crud.crud_post.get_post(db, post_id=report_in.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
        
    return crud.crud_report.create_report(db, report=report_in, reporter_id=current_user.id)

@router.get("/", response_model=List[schemas.report.Report])
def read_reports(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[ReportStatus] = None,
    current_user: models.user.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Listar reportes (Solo Admin).
    """
    return crud.crud_report.get_reports(db, skip=skip, limit=limit, status=status)

@router.put("/{report_id}", response_model=schemas.report.Report)
def update_report(
    *,
    db: Session = Depends(deps.get_db),
    report_id: int,
    report_in: schemas.report.ReportUpdate,
    current_user: models.user.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Resolver o desestimar un reporte (Solo Admin).
    """
    report = crud.crud_report.get_report(db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
        
    return crud.crud_report.update_report(db, db_report=report, report_in=report_in)
