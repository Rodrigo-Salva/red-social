from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.report import ReportStatus

# Shared properties
class ReportBase(BaseModel):
    post_id: int
    reason: str

# Properties to receive on report creation
class ReportCreate(ReportBase):
    pass

# Properties to receive on report update (Admin)
class ReportUpdate(BaseModel):
    status: ReportStatus

# Properties shared by models stored in DB
class ReportInDBBase(ReportBase):
    id: int
    reporter_id: int
    status: ReportStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Properties to return to client
class Report(ReportInDBBase):
    pass
