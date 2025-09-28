"""
Schemas para autenticación y respuestas relacionadas con sesión.
"""

from pydantic import BaseModel

class LoginRequest(BaseModel):
    """Schema para la solicitud de inicio de sesión."""
    email: str
    password: str

class LoginResponse(BaseModel):
    """Schema para la respuesta de inicio de sesión exitoso."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    is_admin: bool

class SessionInfo(BaseModel):
    """Schema para información de la sesión actual."""
    user_id: str
    email: str
    is_admin: bool
    expires_at: str
