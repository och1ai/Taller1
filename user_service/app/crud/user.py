"""
Módulo CRUD específico para usuarios.

Implementa operaciones específicas para el modelo de Usuario,
incluyendo manejo de contraseñas, búsqueda por email y soft delete.
Extiende la funcionalidad base del CRUDBase.
"""

from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from sqlalchemy import func
import uuid

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD para operaciones específicas de Usuario.
    
    Extiende CRUDBase con funcionalidades específicas:
    - Búsqueda por email
    - Manejo seguro de contraseñas
    - Soft delete
    - Filtros de búsqueda avanzados
    """
    def get_user_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Busca un usuario por su correo electrónico.

        Args:
            db: Sesión de la base de datos
            email: Correo electrónico a buscar

        Returns:
            Usuario encontrado o None si no existe o está eliminado
        """
        return db.query(User).filter(
            User.email == email,
            User.deleted_at.is_(None)
        ).first()

    def create(self, db: Session, *, obj_in: UserCreate, is_admin: bool = False) -> User:
        """
        Crea un nuevo usuario.

        Args:
            db: Sesión de la base de datos
            obj_in: Datos del nuevo usuario
            is_admin: Flag para crear usuario administrador (solo usado por el seeder)

        Returns:
            Usuario creado

        Note:
            La contraseña se hashea automáticamente antes de guardarla
            El parámetro is_admin solo debe usarse desde el seeder
        """
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_admin=is_admin
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Actualiza un usuario existente.

        Args:
            db: Sesión de la base de datos
            db_obj: Usuario a actualizar
            obj_in: Datos de actualización

        Returns:
            Usuario actualizado

        Note:
            Si se actualiza la contraseña, se hashea automáticamente
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        full_name: str = None,
        email: str = None,
        is_active: bool = None
    ) -> List[User]:
        """
        Obtiene múltiples usuarios con filtros.

        Args:
            db: Sesión de la base de datos
            skip: Registros a saltar (paginación)
            limit: Límite de registros
            full_name: Filtro por nombre (búsqueda parcial)
            email: Filtro por email (búsqueda parcial)
            is_active: Filtro por estado

        Returns:
            Lista de usuarios que cumplen los criterios
        """
        query = db.query(self.model).filter(self.model.deleted_at.is_(None))
        if full_name:
            query = query.filter(self.model.full_name.ilike(f"%{full_name}%"))
        if email:
            query = query.filter(self.model.email.ilike(f"%{email}%"))
        if is_active is not None:
            query = query.filter(self.model.is_active == is_active)
        return query.offset(skip).limit(limit).all()

    def remove(self, db: Session, *, id: uuid.UUID) -> User:
        """
        Realiza un soft delete de un usuario.

        Args:
            db: Sesión de la base de datos
            id: UUID del usuario a eliminar

        Returns:
            Usuario marcado como eliminado

        Note:
            No elimina físicamente el registro, solo marca la fecha de eliminación
        """
        obj = db.query(self.model).get(id)
        obj.deleted_at = func.now()
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

user = CRUDUser(User)
