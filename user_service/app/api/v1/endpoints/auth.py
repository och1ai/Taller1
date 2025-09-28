"""
Endpoints relacionados con autenticación y manejo de sesiones.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.auth import (
    create_access_token,
    verify_password,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas.auth import LoginRequest, LoginResponse, SessionInfo
from app.api import deps
from app.crud import crud_user

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Inicia sesión y retorna un token JWT.
    """
    # Buscar usuario por email y verificar credenciales
    # Nota: Siempre retornamos el mismo mensaje de error para no revelar si el usuario existe
    user = crud_user.get_user_by_email(db, email=login_data.email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )
    
    # Verificar contraseña
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )
    
    # Crear token
    access_token = create_access_token(
        subject=str(user.id),
        is_admin=user.is_admin,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return LoginResponse(
        access_token=access_token,
        user_id=str(user.id),
        email=user.email,
        is_admin=user.is_admin
    )

@router.get("/session", response_model=SessionInfo)
async def get_session(authorization: Optional[str] = Header(None)):
    """
    Retorna información sobre la sesión actual.
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
    
    return SessionInfo(
        user_id=token_data.sub,
        email="email@example.com",  # TODO: Obtener email del usuario
        is_admin=token_data.is_admin,
        expires_at=datetime.fromtimestamp(token_data.exp).isoformat()
    )
