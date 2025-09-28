#!/bin/bash

# Script para ejecutar pruebas del API de usuarios en entorno LOCAL
# Compatible con Linux y macOS

echo "🏠 INICIANDO PRUEBAS EN ENTORNO LOCAL"
echo "================================================================"

# Verificar si Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 no está instalado o no está en PATH"
    echo "   Instala Python 3.8+ desde https://www.python.org/"
    exit 1
fi

# Verificar si el script Python existe
if [ ! -f "test_local.py" ]; then
    echo "❌ ERROR: No se encuentra test_local.py"
    echo "   Asegúrate de ejecutar este script desde la raíz del proyecto"
    exit 1
fi

# Dar permisos de ejecución al script Python si es necesario
chmod +x test_local.py

# Ejecutar el script Python
echo "Ejecutando pruebas locales..."
python3 test_local.py

# Capturar código de salida
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "🎉 ¡Pruebas locales completadas exitosamente!"
else
    echo ""
    echo "❌ Las pruebas locales fallaron (código: $exit_code)"
    echo "   Revisa la salida anterior para más detalles"
fi

exit $exit_code