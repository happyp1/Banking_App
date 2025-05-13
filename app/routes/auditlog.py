from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal, get_db
from app.models.auditlog import AuditLog
from app.schemas.auditlog import AuditLogResponse
from app.utils.security import is_banker_or_admin
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(db: Session = Depends(get_db), _: User = Depends(is_banker_or_admin)):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
