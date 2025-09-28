@echo off
REM Script para ejecutar pruebas del API de usuarios en entorno LOCAL
REM Compatible con Windows

echo 🏠 INICIANDO PRUEBAS EN ENTORNO LOCAL
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
if not exist "test_local.py" (
    echo ❌ ERROR: No se encuentra test_local.py
    echo    Asegúrate de ejecutar este script desde la raíz del proyecto
    pause
    exit /b 1
)

REM Ejecutar el script Python
echo Ejecutando pruebas locales...
%PYTHON_CMD% test_local.py

REM Capturar código de salida
set exit_code=%errorlevel%

if %exit_code% equ 0 (
    echo.
    echo 🎉 ¡Pruebas locales completadas exitosamente!
) else (
    echo.
    echo ❌ Las pruebas locales fallaron (código: %exit_code%^)
    echo    Revisa la salida anterior para más detalles
)

pause
exit /b %exit_code%