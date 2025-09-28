#!/bin/bash

# Script para ejecutar pruebas del API de usuarios en entorno de PRODUCCIÓN
# Compatible con Linux y macOS

echo "☁️  INICIANDO PRUEBAS EN ENTORNO DE PRODUCCIÓN"
echo "================================================================"

# Verificar si Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 no está instalado o no está en PATH"
    echo "   Instala Python 3.8+ desde https://www.python.org/"
    exit 1
fi

# Verificar si el script Python existe
if [ ! -f "test_production.py" ]; then
    echo "❌ ERROR: No se encuentra test_production.py"
    echo "   Asegúrate de ejecutar este script desde la raíz del proyecto"
    exit 1
fi

# Verificar si existe el archivo de configuración
if [ ! -f ".env.test" ]; then
    echo "❌ ERROR: No se encuentra .env.test"
    echo ""
    echo "Crea el archivo .env.test con el siguiente contenido:"
    echo "---"
    echo "PRODUCTION_API_URL=https://tu-servicio.onrender.com"
    echo "REQUEST_TIMEOUT=30"
    echo "LOG_LEVEL=INFO"
    echo "---"
    exit 1
fi

# Dar permisos de ejecución al script Python si es necesario
chmod +x test_production.py

# Ejecutar el script Python
echo "Ejecutando pruebas de producción..."
python3 test_production.py

# Capturar código de salida
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "🎉 ¡Pruebas de producción completadas exitosamente!"
else
    echo ""
    echo "❌ Las pruebas de producción fallaron (código: $exit_code)"
    echo "   Revisa la salida anterior para más detalles"
fi

exit $exit_code