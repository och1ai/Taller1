"""
Modelo de Usuario para la base de datos.

Este modelo representa la estructura de la tabla de usuarios en la base de datos PostgreSQL.
Implementa el patrón Active Record a través de SQLAlchemy ORM.

Attributes:
    id (UUID): Identificador único del usuario utilizando UUID v4
    full_name (str): Nombre completo del usuario
    email (str): Correo electrónico institucional del usuario (único)
    hashed_password (str): Contraseña hasheada utilizando bcrypt
    is_active (bool): Estado del usuario en el sistema
    created_at (datetime): Fecha y hora de creación del usuario
    deleted_at (datetime): Fecha y hora de eliminación suave del usuario
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    # Identificador único usando UUID v4 para mayor seguridad y distribución
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Nombre completo del usuario con índice para búsquedas eficientes
    full_name = Column(String, index=True)
    
    # Correo electrónico con índice para búsquedas y unicidad
    email = Column(String, index=True, nullable=False)
    
    # Contraseña hasheada (nunca se almacena en texto plano)
    hashed_password = Column(String, nullable=False)
    
    # Estado del usuario (activo/inactivo)
    is_active = Column(Boolean(), default=True)
    
    # Timestamps para auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Para soft delete
