# 🚀 User Service API

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-20.10+-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Authentication-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

**Servicio de gestión de usuarios empresarial con autenticación JWT y auditoría completa**

[📖 Documentación](#-documentación) •
[🏗️ Arquitectura](#️-arquitectura) •
[🚀 Instalación](#-instalación-y-configuración) •
[🧪 Pruebas](#-pruebas) •
[📊 API](#-documentación-de-la-api)

</div>

---

## 📋 Tabla de Contenidos

- [🎯 Descripción del Proyecto](#-descripción-del-proyecto)
- [🏗️ Arquitectura](#️-arquitectura)
- [🎨 Patrones de Diseño](#-patrones-de-diseño)
- [🚀 Instalación y Configuración](#-instalación-y-configuración)
- [🐳 Docker](#-docker)
- [🧪 Pruebas](#-pruebas)
- [📊 Documentación de la API](#-documentación-de-la-api)
- [🔒 Seguridad](#-seguridad)
- [📈 Auditoría](#-auditoría)
- [🌐 Despliegue en la Nube](#-despliegue-en-la-nube)

---

## 🎯 Descripción del Proyecto

User Service es una API RESTful desarrollada con **FastAPI** que proporciona un sistema completo de gestión de usuarios empresariales. El servicio incluye autenticación JWT, autorización por roles, auditoría de acciones administrativas y validaciones de seguridad robustas.

### ✨ Características Principales

- 🔐 **Autenticación JWT** con tokens seguros
- 👥 **Gestión de usuarios** con roles (admin/usuario regular)
- 🛡️ **Autorización granular** basada en permisos
- 📝 **Auditoría completa** de acciones administrativas
- 🔒 **Validaciones de seguridad** (emails institucionales, contraseñas fuertes)
- 🗑️ **Soft delete** para integridad de datos
- 📊 **Documentación automática** con Swagger/OpenAPI
- 🐳 **Containerización** con Docker
- 🧪 **Suite de pruebas** automatizadas

---

## 🏗️ Arquitectura

El proyecto sigue una **arquitectura de capas** bien definida que separa responsabilidades y facilita el mantenimiento:

### Diagrama de Arquitectura

![Arquitectura del Sistema](docs/architecture.png)

### Capas del Sistema

1. **Client Layer**: Interfaz de usuario y clientes de testing
2. **API Layer**: FastAPI, autenticación JWT, documentación OpenAPI
3. **Business Logic Layer**: Controladores de endpoints y servicios de negocio
4. **Data Access Layer**: Operaciones CRUD, modelos y esquemas
5. **Database Layer**: PostgreSQL con tablas usuarios y auditoría

### Modelo de Datos

![Modelo de Datos](docs/database.png)

---

## 🎨 Patrones de Diseño

El proyecto implementa varios patrones de diseño para garantizar código mantenible y escalable:

### 1. **Repository Pattern** 🗄️

Centraliza la lógica de acceso a datos y proporciona una interfaz uniforme para las operaciones CRUD.

```python
# user_service/app/crud/base.py
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Clase base para operaciones CRUD (Create, Read, Update, Delete).
    Implementa el patrón Repository con métodos genéricos.
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        ).first()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
```

### 2. **Dependency Injection** 💉

Utiliza el sistema de dependencias de FastAPI para inyectar servicios y conexiones de base de datos.

```python
# user_service/app/api/deps.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Uso en endpoints
@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),  # ← Dependency Injection
    user_in: UserCreate,
):
    return crud_user.create(db, obj_in=user_in)
```

### 3. **Strategy Pattern** 🎯

Implementa diferentes estrategias de validación y procesamiento según el contexto.

```python
# user_service/app/schemas/user.py
class UserCreate(UserBase):
    @validator('email')
    def validate_institutional_email(cls, v):
        if not v.endswith('@perlametro.cl'):
            raise ValueError('El correo debe ser institucional (@perlametro.cl)')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        # Estrategia de validación de contraseña fuerte
        if len(v) < 8:
            raise ValueError('Contraseña debe tener al menos 8 caracteres')
        # ... más validaciones
        return v
```

### 4. **Factory Pattern** 🏭

Crea instancias de objetos específicos basados en parámetros.

```python
# user_service/app/core/auth.py
def create_access_token(
    subject: Union[str, Any],
    is_admin: bool,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Factory method para crear tokens JWT con diferentes configuraciones"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "is_admin": is_admin
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 5. **Template Method Pattern** 📋

Define la estructura de algoritmos en la clase base y permite que las subclases sobrescriban pasos específicos.

```python
# user_service/app/crud/user.py
class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def create(self, db: Session, *, obj_in: UserCreate, is_admin: bool = False) -> User:
        """Sobrescribe el método create para agregar lógica específica de usuario"""
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),  # ← Paso específico
            full_name=obj_in.full_name,
            is_admin=is_admin
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: uuid.UUID) -> User:
        """Implementa soft delete específico para usuarios"""
        obj = db.query(self.model).get(id)
        obj.deleted_at = func.now()  # ← Soft delete en lugar de eliminación física
        db.add(obj)
        db.commit()
        return obj
```

### 6. **Singleton Pattern** 🎱

Garantiza una única instancia de configuraciones globales.

```python
# user_service/app/core/config.py
class Settings(BaseSettings):
    PROJECT_NAME: str = "User Service"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()  # ← Instancia única global
```

### 7. **Observer Pattern** 👁️

Implementa un sistema de auditoría que "observa" acciones administrativas.

```python
# user_service/app/api/v1/endpoints/users.py
@router.delete("/{user_id}", response_model=User)
async def delete_user(*, db: Session = Depends(deps.get_db), user_id: uuid.UUID, ...):
    user = crud_user.remove(db, id=user_id)
    
    # Observer: Registra la acción en auditoría
    crud_audit.create_log(
        db,
        action="delete_user",
        entity_type="user",
        entity_id=user_id,
        performed_by=token_data.sub,
        details={
            "deleted_user_email": user.email,
            "soft_delete": True
        }
    )
    return user
```

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- **Python 3.9+**
- **Docker & Docker Compose** (para ejecución con contenedores)
- **PostgreSQL** (para ejecución local sin Docker)
- **Git**

### Enlaces de Descarga

- [🐳 Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [🐳 Docker Compose](https://docs.docker.com/compose/install/)
- [🐍 Python](https://www.python.org/downloads/)
- [🐘 PostgreSQL](https://www.postgresql.org/download/)

### 🐳 Opción 1: Con Docker Compose (Recomendado)

Esta es la forma más fácil de ejecutar el proyecto completo:

#### Linux/MacOS
```bash
# Clonar el repositorio
git clone <repository-url>
cd user-service

# Ejecutar con Docker Compose
./start-local.sh
```

#### Windows
```batch
# Clonar el repositorio
git clone <repository-url>
cd user-service

# Ejecutar con Docker Compose
start-local.bat
```

Los servicios estarán disponibles en:
- **User Service**: http://localhost:8000
- **Mock Main API**: http://localhost:8001
- **Base de datos**: localhost:5432

### 🐋 Opción 2: Solo Docker

Si prefieres mayor control sobre los contenedores:

```bash
# Construir las imágenes
docker-compose build

# Iniciar servicios en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f user_service

# Detener servicios
docker-compose down
```

### 💻 Opción 3: Ejecución Local (sin Docker)

Para desarrollo local sin contenedores:

#### 1. Configurar Base de Datos

```bash
# Instalar y configurar PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib  # Ubuntu/Debian
# o
brew install postgresql  # macOS

# Crear base de datos
sudo -u postgres psql
CREATE DATABASE user_service_db;
CREATE USER user_service WITH PASSWORD 'password123';
GRANT ALL PRIVILEGES ON DATABASE user_service_db TO user_service;
\q
```

#### 2. Configurar el Proyecto

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r user_service/requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones
```

#### 3. Ejecutar Aplicación

```bash
# Aplicar migraciones
cd user_service
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine)"

# Ejecutar seeders
python -m app.seeders.seed

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### ⚙️ Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DATABASE_URL=postgresql://user_service:password123@localhost:5432/user_service_db

# Seguridad
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Configuración de la aplicación
PROJECT_NAME=User Service
API_V1_STR=/api/v1
```

---

## 🧪 Pruebas

El proyecto incluye una suite completa de pruebas que valida todos los endpoints y funcionalidades.

### 🧪 Ejecución de Pruebas

#### 🏠 Pruebas Locales (Docker)

Ejecuta las pruebas contra tu entorno local de desarrollo:

##### Opción 1: Scripts Automatizados Nuevos 🆕

```bash
# Linux/macOS
./test_local.sh

# Windows
test_local.bat

# Python directo
python test_local.py
# o
python3 test_local.py
```

##### Opción 2: Scripts de Servicio + Pruebas (Método Anterior)

```bash
# 1. Iniciar los servicios
# Linux/macOS
./start_service.sh

# Windows
start_service.bat

# 2. Ejecutar pruebas (en otra terminal)
./run_tests.sh  # Linux/macOS
run_tests.bat   # Windows
```

#### ☁️ Pruebas de Producción

##### Configuración Inicial

1. Crea el archivo `.env.test` con la URL de tu servicio desplegado:

```bash
# .env.test
PRODUCTION_API_URL=https://tu-servicio.onrender.com
REQUEST_TIMEOUT=30
LOG_LEVEL=INFO
```

2. Ejecuta las pruebas:

```bash
# Linux/macOS
./test_production.sh

# Windows
test_production.bat

# Python directo
python test_production.py
# o
python3 test_production.py
```

#### 🐍 Con Python Virtual Environment (Método Manual)

```bash
# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate  # Windows

# Instalar dependencias de testing
pip install requests

# Ejecutar pruebas locales
export API_BASE_URL="http://localhost:8000"  # Linux/macOS
set API_BASE_URL=http://localhost:8000       # Windows
python test_api.py

# Ejecutar pruebas de producción
export API_BASE_URL="https://tu-servicio.onrender.com"  # Linux/macOS
set API_BASE_URL=https://tu-servicio.onrender.com       # Windows
python test_api.py
```

### 📊 Cobertura de Pruebas

Los scripts de prueba verifican:

- ✅ **Validaciones de entrada** (email institucional, contraseña fuerte)
- ✅ **Autenticación JWT** (login exitoso/fallido)
- ✅ **Autorización granular** (permisos por rol)
- ✅ **CRUD completo** (crear, leer, actualizar, eliminar)
- ✅ **Soft deletes** (eliminación lógica)
- ✅ **Logs de auditoría** (trazabilidad completa)
- ✅ **Restricciones de negocio** (solo admin puede eliminar)
- ✅ **Información de sesión** (datos del token)
- ✅ **Casos de error** (401, 403, 404, 422)
- ✅ **Conectividad** (verificación de servicios activos)

### Flujo de Autenticación

![Flujo de Autenticación](docs/auth_flow.png)

---

## 📊 Documentación de la API

### 🔗 Acceso a la Documentación

Una vez que el servicio esté ejecutándose, la documentación interactiva estará disponible en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### 🛠️ Endpoints Principales

#### Autenticación

| Método | Endpoint | Descripción | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/auth/login` | Iniciar sesión | ❌ |
| `GET` | `/api/v1/auth/session` | Info de sesión | ✅ |

#### Gestión de Usuarios

| Método | Endpoint | Descripción | Auth Required | Admin Required |
|--------|----------|-------------|---------------|----------------|
| `POST` | `/api/v1/users/` | Crear usuario | ❌ | ❌ |
| `GET` | `/api/v1/users/` | Listar usuarios | ✅ | ❌ |
| `GET` | `/api/v1/users/{user_id}` | Obtener usuario | ✅ | ❌ |
| `PUT` | `/api/v1/users/{user_id}` | Actualizar usuario | ✅ | ❌* |
| `DELETE` | `/api/v1/users/{user_id}` | Eliminar usuario | ✅ | ✅ |

*_Los usuarios pueden actualizar su propio perfil_

#### Auditoría

| Método | Endpoint | Descripción | Auth Required | Admin Required |
|--------|----------|-------------|---------------|----------------|
| `GET` | `/api/v1/audit-logs/` | Ver logs de auditoría | ✅ | ✅ |

### 📝 Ejemplos de Uso

#### Crear Usuario

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Juan Pérez",
       "email": "juan.perez@perlametro.cl",
       "password": "MiPassword123!"
     }'
```

#### Iniciar Sesión

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "juan.perez@perlametro.cl",
       "password": "MiPassword123!"
     }'
```

#### Listar Usuarios (con token)

```bash
curl -X GET "http://localhost:8000/api/v1/users/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

---

## 🔒 Seguridad

El servicio implementa múltiples capas de seguridad:

### 🛡️ Medidas de Seguridad Implementadas

1. **Autenticación JWT**
   - Tokens firmados con HMAC SHA256
   - Expiración automática (30 minutos por defecto)
   - Validación de integridad en cada request

2. **Contraseñas Seguras**
   - Hash bcrypt con salt automático
   - Validación de complejidad (8+ caracteres, mayús/minus, números, especiales)
   - Nunca se almacenan en texto plano

3. **Validación de Datos**
   - Emails institucionales únicamente (`@perlametro.cl`)
   - Schemas Pydantic para validación automática
   - Sanitización de inputs

4. **Autorización Granular**
   - Roles de usuario (admin/regular)
   - Permisos específicos por endpoint
   - Validación de pertenencia de recursos

5. **Protección de Datos**
   - Soft delete para preservar integridad
   - UUIDs como identificadores (no incrementales)
   - Logs de auditoría para trazabilidad

### 🚫 Políticas de Seguridad

- **Principio de menor privilegio**: Los usuarios solo acceden a lo necesario
- **Fail-safe defaults**: Por defecto, se deniega el acceso
- **Defense in depth**: Múltiples capas de validación
- **Audit trail**: Todas las acciones administrativas se registran

---

## 📈 Auditoría

### 📋 Sistema de Logs

El servicio mantiene un registro completo de todas las acciones administrativas:

#### Eventos Registrados

- 🗑️ **Eliminación de usuarios** (con detalles del usuario eliminado)
- 👤 **Modificaciones de perfil** (por administradores)
- 🔐 **Acciones sensibles** de administración

#### Estructura de Logs

```json
{
  "id": "uuid-v4",
  "action": "delete_user",
  "entity_type": "user",
  "entity_id": "user-uuid",
  "performed_by": "admin-uuid",
  "performed_at": "2024-01-15T10:30:00Z",
  "details": {
    "deleted_user_email": "usuario@perlametro.cl",
    "soft_delete": true
  }
}
```

#### Consulta de Logs

```bash
# Ver todos los logs (requiere permisos de admin)
curl -X GET "http://localhost:8000/api/v1/audit-logs/" \
     -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## 🌐 Despliegue en la Nube

### 🚀 URL del Servicio

Una vez desplegado, el servicio estará disponible en:

```
https://taller1-g43w.onrender.com
```

### 📊 Documentación en la Nube

- **Swagger UI**: https://taller1-g43w.onrender.com/docs
- **ReDoc**: https://taller1-g43w.onrender.com/redoc

### 🧪 Pruebas contra Servicio Desplegado

Para ejecutar las pruebas contra el servicio en la nube:

1. **Modificar la URL base** en `test_api.py`:
   ```python
   BASE_URL = "https://taller1-g43w.onrender.com"
   ```

2. **Ejecutar pruebas**:
   ```bash
   # Linux/macOS
   ./test.sh
   
   # Windows  
   test.bat
   ```

### ⚙️ Variables de Entorno en Producción

```env
DATABASE_URL=postgresql://user:pass@prod-db-host:5432/user_service_db
SECRET_KEY=super-secure-production-key-256-bits
PROJECT_NAME=User Service Production
API_V1_STR=/api/v1
ENVIRONMENT=production
```

---

## 🤝 Contribución

### 📋 Cómo Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### 🧪 Antes de Enviar PR

- ✅ Ejecuta todas las pruebas (`./test.sh`)
- ✅ Verifica que el código sigue las convenciones
- ✅ Agrega pruebas para nueva funcionalidad
- ✅ Actualiza la documentación si es necesario

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👥 Equipo

Desarrollado con ❤️ por el equipo de desarrollo de Perlametro.

---

<div align="center">

**¿Tienes preguntas?** 

[📧 Contacto](mailto:dev@perlametro.cl) • [📖 Wiki](./docs/) • [🐛 Reportar Bug](./issues)

---

⭐ **¡No olvides darle una estrella al proyecto si te fue útil!** ⭐

</div>
