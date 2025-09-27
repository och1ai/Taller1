"""
Schemas de Usuario para la API.

Este módulo define los modelos Pydantic para la validación de datos y serialización
en la API de usuarios. Implementa diferentes schemas para diferentes operaciones:
- UserBase: Schema base con campos comunes
- UserCreate: Para crear usuarios
- UserUpdate: Para actualizar usuarios
- User: Para respuestas de la API

Cada schema implementa sus propias validaciones y transformaciones de datos.
"""

from pydantic import BaseModel, EmailStr, Field, validator
import uuid
from datetime import datetime
from typing import Optional
import re

class UserBase(BaseModel):
    """Schema base para usuarios con campos comunes."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    """
    Schema para la creación de usuarios.
    
    Implementa validaciones específicas:
    - Correo electrónico institucional (@perlametro.cl)
    - Contraseña segura con múltiples requisitos
    """
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('email')
    def validate_institutional_email(cls, v):
        """
        Valida que el correo electrónico sea institucional.
        
        Args:
            v (str): El correo electrónico a validar
            
        Returns:
            str: El correo electrónico si es válido
            
        Raises:
            ValueError: Si el correo no es institucional
        """
        # Permitir el correo admin@example.com
        if v == "admin@example.com":
            return v
        if not v.endswith('@perlametro.cl'):
            raise ValueError('El correo electrónico debe ser institucional (@perlametro.cl)')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """
        Valida que la contraseña cumpla con los requisitos de seguridad.
        
        Requisitos:
        - Mínimo 8 caracteres
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número
        - Al menos un carácter especial
        
        Args:
            v (str): La contraseña a validar
            
        Returns:
            str: La contraseña si es válida
            
        Raises:
            ValueError: Si la contraseña no cumple los requisitos
        """
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return v

class UserUpdate(UserBase):
    """
    Schema para actualizar usuarios.
    
    Similar a UserCreate pero todos los campos son opcionales.
    Mantiene las mismas validaciones cuando se proporcionan valores.
    """
    password: Optional[str] = Field(None, min_length=8)
    
    @validator('email')
    def validate_institutional_email(cls, v):
        """Valida el correo institucional si se proporciona uno nuevo."""
        if v is not None and not v.endswith('@perlametro.cl'):
            raise ValueError('El correo electrónico debe ser institucional (@perlametro.cl)')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """
        Valida la nueva contraseña si se proporciona una.
        Aplica las mismas reglas que en la creación.
        """
        if v is not None:
            if len(v) < 8:
                raise ValueError('La contraseña debe tener al menos 8 caracteres')
            if not any(c.isupper() for c in v):
                raise ValueError('La contraseña debe contener al menos una letra mayúscula')
            if not any(c.islower() for c in v):
                raise ValueError('La contraseña debe contener al menos una letra minúscula')
            if not any(c.isdigit() for c in v):
                raise ValueError('La contraseña debe contener al menos un número')
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
                raise ValueError('La contraseña debe contener al menos un carácter especial')
        return v

class UserInDBBase(UserBase):
    """
    Schema base para usuarios en la base de datos.
    
    Incluye los campos que siempre están presentes en la BD:
    - id: UUID v4 único
    - created_at: Timestamp de creación
    """
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True  # Permite la conversión desde modelos SQLAlchemy

class User(UserInDBBase):
    """
    Schema para respuestas de la API.
    
    Este schema hereda de UserInDBBase pero no incluye
    información sensible como la contraseña hasheada.
    """
    is_admin: bool  # Solo se incluye en la respuesta, no en la creación

class UserInDB(UserInDBBase):
    """
    Schema interno para operaciones de base de datos.
    
    Incluye la contraseña hasheada para operaciones internas,
    pero nunca se expone en la API.
    """
    hashed_password: str
