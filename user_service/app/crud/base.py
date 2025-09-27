"""
Módulo base para operaciones CRUD.

Este módulo implementa un patrón Repository genérico que proporciona
operaciones CRUD básicas para cualquier modelo. Se utiliza como clase
base para implementaciones específicas de modelos.

Generic Types:
    ModelType: Tipo del modelo SQLAlchemy
    CreateSchemaType: Schema Pydantic para creación
    UpdateSchemaType: Schema Pydantic para actualización
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Clase base para operaciones CRUD (Create, Read, Update, Delete).
    
    Implementa el patrón Repository con métodos genéricos que pueden
    ser heredados y sobrescritos por clases específicas de modelo.
    
    Attributes:
        model: Clase del modelo SQLAlchemy
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Inicializa el repositorio CRUD.

        Args:
            model: Clase del modelo SQLAlchemy para las operaciones CRUD
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Obtiene un registro por su ID.

        Args:
            db: Sesión de la base de datos
            id: Identificador único del registro

        Returns:
            El registro encontrado o None si no existe o está eliminado
        """
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        ).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Obtiene múltiples registros con paginación.

        Args:
            db: Sesión de la base de datos
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar

        Returns:
            Lista de registros encontrados
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Crea un nuevo registro.

        Args:
            db: Sesión de la base de datos
            obj_in: Datos del nuevo registro (schema de creación)

        Returns:
            El registro creado
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Actualiza un registro existente.

        Args:
            db: Sesión de la base de datos
            db_obj: Instancia del registro a actualizar
            obj_in: Datos de actualización (schema o diccionario)

        Returns:
            El registro actualizado
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        Elimina un registro.

        Args:
            db: Sesión de la base de datos
            id: Identificador único del registro a eliminar

        Returns:
            El registro eliminado
        
        Note:
            Este método realiza una eliminación física. Para soft delete,
            las clases hijas deben sobrescribir este método.
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
