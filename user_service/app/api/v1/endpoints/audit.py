from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
from app.crud import crud_audit
from app.schemas.audit import AuditLog
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AuditLog])
async def get_audit_logs(
    *,
    db: Session = Depends(deps.get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Get all audit logs. Only accessible by administrators.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token no proporcionado o formato inválido"
        )
    
    token = authorization.split(" ")[1]
    token_data = await get_current_user(token)
    
    if not token_data:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )
    
    if not token_data.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Se requieren privilegios de administrador para acceder a los logs de auditoría"
        )
    
    return crud_audit.get_all_logs(db)
