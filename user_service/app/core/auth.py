"""
Módulo de autenticación y manejo de JWT.
Implementa la creación, validación y decodificación de tokens JWT.
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Configuración de JWT
SECRET_KEY = "your-secret-key-keep-it-secret"  # En producción, usar variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    """Schema para el token de acceso."""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Schema para el contenido del token JWT."""
    sub: str  # ID del usuario
    exp: int  # Timestamp de expiración
    is_admin: bool  # Flag de administrador

def create_access_token(
    subject: Union[str, Any],
    is_admin: bool,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de acceso.
    
    Args:
        subject: ID del usuario (sub claim)
        is_admin: Si el usuario es administrador
        expires_delta: Tiempo de expiración opcional
        
    Returns:
        Token JWT firmado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "is_admin": is_admin
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña coincide con su hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera un hash bcrypt de una contraseña."""
    return pwd_context.hash(password)

async def get_current_user(token: str) -> Optional[TokenPayload]:
    """
    Valida un token JWT y retorna la información del usuario.
    
    Args:
        token: Token JWT a validar
        
    Returns:
        TokenPayload con la información del usuario
        
    Raises:
        JWTError: Si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(
            sub=payload["sub"],
            exp=payload["exp"],
            is_admin=payload["is_admin"]
        )
        
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            return None
            
        return token_data
    except JWTError:
        return None
