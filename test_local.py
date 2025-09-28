#!/usr/bin/env python3
"""
Script para ejecutar pruebas del API de usuarios en entorno LOCAL.
Configura automáticamente la URL base para apuntar a localhost:8000.
"""

import os
import sys
import subprocess

def main():
    print("🏠 INICIANDO PRUEBAS EN ENTORNO LOCAL")
    print("=" * 60)
    print("Configuración:")
    print("• Entorno: LOCAL (Docker)")
    print("• URL Base: http://localhost:8000")
    print("• Documentación: http://localhost:8000/docs")
    print("=" * 60)
    print()
    
    # Verificar que Docker esté ejecutándose
    print("Verificando estado de los contenedores Docker...")
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, check=True)
        if 'user_service' not in result.stdout:
            print("⚠️  ADVERTENCIA: No se encontró el contenedor 'user_service' ejecutándose.")
            print("   Ejecuta primero: ./start_service.sh (Linux/macOS) o start_service.bat (Windows)")
            print("   O manualmente: docker-compose up -d")
            print()
        else:
            print("✅ Contenedores Docker ejecutándose correctamente")
            print()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  ADVERTENCIA: No se pudo verificar el estado de Docker.")
        print("   Asegúrate de que Docker esté instalado y ejecutándose.")
        print()
    
    # Configurar variables de entorno para el test
    os.environ['API_BASE_URL'] = 'http://localhost:8000'
    os.environ['TEST_ENVIRONMENT'] = 'LOCAL'
    
    print("🧪 Ejecutando suite completa de pruebas...")
    print("-" * 60)
    
    try:
        # Ejecutar el script de pruebas original
        result = subprocess.run([sys.executable, 'test_api.py'], check=True)
        
        print()
        print("=" * 60)
        print("✅ PRUEBAS LOCALES COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        print("📊 Resumen:")
        print("• Todas las validaciones pasaron")
        print("• Autenticación y autorización funcionando")
        print("• CRUD completo operativo")
        print("• Soft deletes funcionando")
        print("• Logs de auditoría operativos")
        print()
        print("🔗 Enlaces útiles:")
        print("• API: http://localhost:8000")
        print("• Docs: http://localhost:8000/docs")
        print("• Redoc: http://localhost:8000/redoc")
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("❌ ERROR EN LAS PRUEBAS LOCALES")
        print("=" * 60)
        print("Las pruebas fallaron. Revisa la salida anterior para más detalles.")
        print()
        print("🔍 Pasos para solucionar problemas:")
        print("1. Verifica que Docker esté ejecutándose")
        print("2. Ejecuta: docker-compose up -d")
        print("3. Espera unos segundos para que la DB se inicialice")
        print("4. Verifica que http://localhost:8000/docs esté accesible")
        
        sys.exit(1)
    
    except KeyboardInterrupt:
        print()
        print("⏹️  Pruebas interrumpidas por el usuario")
        sys.exit(1)

if __name__ == "__main__":
    main()