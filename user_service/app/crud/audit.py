from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogCreate
import uuid

class CRUDAudit(CRUDBase[AuditLog, AuditLogCreate, None]):
    def create_log(
        self,
        db: Session,
        *,
        action: str,
        entity_type: str,
        entity_id: uuid.UUID,
        performed_by: uuid.UUID,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        audit_data = {
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "performed_by": performed_by,
            "details": details
        }
        db_obj = AuditLog(**audit_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_all_logs(self, db: Session) -> List[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.performed_at.desc()).all()

crud_audit = CRUDAudit(AuditLog)
