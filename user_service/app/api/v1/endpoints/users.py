from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_user
from app.schemas import UserCreate, UserUpdate, User
from app.core.security import validate_password
from app.core.auth import get_current_user
from typing import List, Optional
import uuid

router = APIRouter()

async def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verify JWT token and return token data.
    Raises HTTPException if token is invalid.
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
    
    return token_data

@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
):
    """
    Create new user.
    """
    if not validate_password(user_in.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.",
        )
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud_user.create(db, obj_in=user_in)
    return user

@router.get("/", response_model=List[User])
async def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    full_name: str = None,
    email: str = None,
    is_active: bool = None,
    authorization: Optional[str] = Header(None),
):
    """
    Retrieve users. Requires authentication.
    """
    await verify_token(authorization)
    
    users = crud_user.get_multi(
        db,
        skip=skip,
        limit=limit,
        full_name=full_name,
        email=email,
        is_active=is_active,
    )
    return users

@router.get("/{user_id}", response_model=User)
async def read_user_by_id(
    user_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Get a specific user by id. Requires authentication.
    """
    await verify_token(authorization)
    
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    user_in: UserUpdate,
    authorization: Optional[str] = Header(None),
):
    """
    Update a user. Requires authentication.
    """
    token_data = await verify_token(authorization)
    
    # Solo permitir que los usuarios actualicen sus propios datos o que los admins actualicen cualquier usuario
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    if not token_data.is_admin and str(user_id) != token_data.sub:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para actualizar este usuario"
        )
    
    if user_in.password and not validate_password(user_in.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.",
        )
    
    user = crud_user.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=User)
async def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    authorization: Optional[str] = Header(None),
):
    """
    Delete a user. Requires admin privileges.
    """
    token_data = await verify_token(authorization)
    
    if not token_data.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Se requieren privilegios de administrador para eliminar usuarios"
        )
    
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
        
    # Prevenir que se elimine al último administrador
    if user.is_admin:
        admin_count = len([u for u in crud_user.get_multi(db) if u.is_admin and u.id != user_id])
        if admin_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar al último usuario administrador"
            )
    
    user = crud_user.remove(db, id=user_id)
    return user
