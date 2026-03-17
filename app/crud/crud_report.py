from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.report import Report, ReportStatus
from app.schemas.report import ReportCreate, ReportUpdate

def create_report(db: Session, report: ReportCreate, reporter_id: int):
    db_report = Report(
        reporter_id=reporter_id,
        post_id=report.post_id,
        reason=report.reason
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_report(db: Session, report_id: int):
    return db.query(Report).filter(Report.id == report_id).first()

def get_reports(db: Session, skip: int = 0, limit: int = 100, status: Optional[ReportStatus] = None):
    query = db.query(Report)
    if status:
        query = query.filter(Report.status == status)
    return query.offset(skip).limit(limit).all()

def update_report(db: Session, db_report: Report, report_in: ReportUpdate):
    db_report.status = report_in.status
    if report_in.status != ReportStatus.PENDING:
        db_report.resolved_at = datetime.now()
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report
