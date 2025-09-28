@echo off
REM Script para ejecutar pruebas del API de usuarios en entorno de PRODUCCIÓN
REM Compatible con Windows

echo ☁️  INICIANDO PRUEBAS EN ENTORNO DE PRODUCCIÓN
echo ================================================================

REM Verificar si Python está disponible
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ ERROR: Python no está instalado o no está en PATH
        echo    Instala Python 3.8+ desde https://www.python.org/
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

REM Verificar si el script Python existe
if not exist "test_production.py" (
    echo ❌ ERROR: No se encuentra test_production.py
    echo    Asegúrate de ejecutar este script desde la raíz del proyecto
    pause
    exit /b 1
)

REM Verificar si existe el archivo de configuración
if not exist ".env.test" (
    echo ❌ ERROR: No se encuentra .env.test
    echo.
    echo Crea el archivo .env.test con el siguiente contenido:
    echo ---
    echo PRODUCTION_API_URL=https://tu-servicio.onrender.com
    echo REQUEST_TIMEOUT=30
    echo LOG_LEVEL=INFO
    echo ---
    pause
    exit /b 1
)

REM Ejecutar el script Python
echo Ejecutando pruebas de producción...
%PYTHON_CMD% test_production.py

REM Capturar código de salida
set exit_code=%errorlevel%

if %exit_code% equ 0 (
    echo.
    echo 🎉 ¡Pruebas de producción completadas exitosamente!
) else (
    echo.
    echo ❌ Las pruebas de producción fallaron (código: %exit_code%^)
    echo    Revisa la salida anterior para más detalles
)

pause
exit /b %exit_code%