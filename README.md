# User Service API - Perla Metro

Este servicio gestiona la información de los usuarios del sistema de Perla Metro, proporcionando una API RESTful para la gestión segura de usuarios.

## Arquitectura

El proyecto sigue una arquitectura en capas con un diseño modular, implementando los siguientes patrones de diseño:

### Patrones de Diseño

1. **Repository Pattern**
   - Implementado en la capa CRUD para abstraer las operaciones de la base de datos
   - Permite cambiar fácilmente la implementación del almacenamiento sin afectar la lógica de negocio

2. **Dependency Injection**
   - Utilizado para la inyección de dependencias en los endpoints
   - Facilita el testing y mantiene el código desacoplado

3. **Factory Pattern**
   - Implementado en la creación de la base de datos y sesiones
   - Centraliza la creación de objetos complejos

### Capas de la Aplicación

1. **API Layer (`app/api/`)**
   - Maneja las rutas y endpoints
   - Implementa la validación de datos de entrada
   - Gestiona las respuestas HTTP

2. **Service Layer (`app/crud/`)**
   - Implementa la lógica de negocio
   - Gestiona las operaciones CRUD
   - Maneja las reglas de negocio específicas

3. **Model Layer (`app/models/`)**
   - Define los modelos de la base de datos
   - Implementa las relaciones y constraints

4. **Schema Layer (`app/schemas/`)**
   - Define los modelos de datos para la API
   - Implementa la validación de datos
   - Maneja la serialización/deserialización

## Consultas Disponibles

### Usuarios (`/api/v1/users/`)

1. **Crear Usuario (POST `/`)**
   ```json
   {
     "full_name": "string",
     "email": "user@perlametro.cl",
     "password": "string"
   }
   ```
   - Valida correo institucional (@perlametro.cl)
   - Valida contraseña segura (8+ caracteres, mayúsculas, minúsculas, números y caracteres especiales)

2. **Listar Usuarios (GET `/`)**
   - Parámetros opcionales:
     - `skip`: número de registros a saltar
     - `limit`: límite de registros
     - `full_name`: filtrar por nombre
     - `email`: filtrar por correo
     - `is_active`: filtrar por estado

3. **Obtener Usuario (GET `/{user_id}`)**
   - Retorna los datos del usuario por ID
   - Excluye información sensible

4. **Actualizar Usuario (PUT `/{user_id}`)**
   ```json
   {
     "full_name": "string",
     "email": "user@perlametro.cl",
     "password": "string"
   }
   ```
   - Todos los campos son opcionales
   - Mantiene las mismas validaciones que la creación

5. **Eliminar Usuario (DELETE `/{user_id}`)**
   - Implementa soft delete
   - Mantiene el registro en la base de datos pero lo marca como eliminado

## Ejecución del Proyecto

### Prerrequisitos

- Docker
- Docker Compose
- Git

### Pasos de Instalación

1. **Clonar el Repositorio**
   ```bash
   git clone <repository-url>
   cd Taller1
   ```

2. **Configurar Variables de Entorno**
   ```bash
   # En user_service/.env
   DATABASE_URL=postgresql://user:password@db:5432/user_db
   SECRET_KEY=a_very_secret_key
   ```

3. **Iniciar los Servicios**
   ```bash
   ./start-local.sh
   ```
   Este script:
   - Construye las imágenes Docker
   - Inicia los contenedores
   - Ejecuta las migraciones
   - Carga los datos iniciales

4. **Verificar la Instalación**
   ```bash
   python3 test_api.py
   ```
   Ejecuta las pruebas funcionales para verificar que todo funciona correctamente

### Estructura del Proyecto

```
user_service/
├── app/
│   ├── api/                 # Endpoints y rutas
│   │   ├── v1/
│   │   └── deps.py         # Dependencias (DB, etc.)
│   ├── core/               # Configuración central
│   │   ├── config.py       # Variables de configuración
│   │   ├── database.py     # Configuración de DB
│   │   └── security.py     # Funciones de seguridad
│   ├── crud/               # Operaciones de base de datos
│   │   ├── base.py         # CRUD base genérico
│   │   └── user.py         # CRUD específico de usuarios
│   ├── models/             # Modelos SQLAlchemy
│   │   └── user.py         # Modelo de Usuario
│   ├── schemas/            # Schemas Pydantic
│   │   └── user.py         # Schemas de Usuario
│   └── main.py            # Punto de entrada de la aplicación
├── migrations/            # Migraciones de SQL
├── Dockerfile            # Configuración de Docker
└── requirements.txt      # Dependencias Python
```

## Testing

### Tests Unitarios
```bash
# En desarrollo
```

### Tests Funcionales
```bash
python3 test_api.py
```

Este script prueba:
- Validaciones de entrada (correo y contraseña)
- Operaciones CRUD completas
- Soft delete
- Restricciones de unicidad

## Contribución

1. Fork el repositorio
2. Cree una rama para su característica (`git checkout -b feature/AmazingFeature`)
3. Commit sus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abra un Pull Request
# Taller1
