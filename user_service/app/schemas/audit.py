from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, Dict, Any

class AuditLogBase(BaseModel):
    action: str
    entity_type: str
    entity_id: UUID4
    performed_by: UUID4
    details: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: UUID4
    performed_at: datetime

    class Config:
        from_attributes = True
