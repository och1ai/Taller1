#!/usr/bin/env python3
"""
Script para ejecutar pruebas del API de usuarios en entorno de PRODUCCIÓN.
Lee la configuración desde el archivo .env.test para obtener la URL del servicio.
"""

import os
import sys
import subprocess
from pathlib import Path

def load_env_file(env_file_path='.env.test'):
    """Carga variables de entorno desde un archivo .env"""
    env_file = Path(env_file_path)
    
    if not env_file.exists():
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    
    return True

def main():
    print("☁️  INICIANDO PRUEBAS EN ENTORNO DE PRODUCCIÓN")
    print("=" * 60)
    
    # Cargar configuración desde .env.test
    if not load_env_file('.env.test'):
        print("❌ ERROR: No se encontró el archivo .env.test")
        print()
        print("Crea el archivo .env.test con el siguiente contenido:")
        print("---")
        print("PRODUCTION_API_URL=https://tu-servicio.onrender.com")
        print("REQUEST_TIMEOUT=30")
        print("LOG_LEVEL=INFO")
        print("---")
        print()
        sys.exit(1)
    
    # Obtener URL de producción
    production_url = os.environ.get('PRODUCTION_API_URL')
    if not production_url:
        print("❌ ERROR: PRODUCTION_API_URL no está definida en .env.test")
        print()
        print("Añade la línea en .env.test:")
        print("PRODUCTION_API_URL=https://tu-servicio.onrender.com")
        print()
        sys.exit(1)
    
    # Mostrar configuración
    print("Configuración:")
    print(f"• Entorno: PRODUCCIÓN (Cloud)")
    print(f"• URL Base: {production_url}")
    print(f"• Timeout: {os.environ.get('REQUEST_TIMEOUT', '30')} segundos")
    print(f"• Log Level: {os.environ.get('LOG_LEVEL', 'INFO')}")
    print("=" * 60)
    print()
    
    # Verificar conectividad
    print("Verificando conectividad con el servicio...")
    try:
        import requests
        
        # Test básico de conectividad
        response = requests.get(
            f"{production_url}/docs", 
            timeout=int(os.environ.get('REQUEST_TIMEOUT', '30'))
        )
        
        if response.status_code == 200:
            print("✅ Servicio accesible - Swagger UI disponible")
        else:
            print(f"⚠️  ADVERTENCIA: Swagger UI no accesible (código: {response.status_code})")
            print("   Esto puede ser normal si la documentación está deshabilitada en producción")
        
        print()
        
    except ImportError:
        print("⚠️  ADVERTENCIA: requests no está instalado. Saltando verificación de conectividad.")
        print("   Instala con: pip install requests")
        print()
    except Exception as e:
        print(f"⚠️  ADVERTENCIA: No se pudo verificar conectividad: {str(e)}")
        print("   Las pruebas pueden fallar si el servicio no está disponible.")
        print()
    
    # Configurar variables de entorno para el test
    os.environ['API_BASE_URL'] = production_url
    os.environ['TEST_ENVIRONMENT'] = 'PRODUCTION'
    
    print("🧪 Ejecutando suite completa de pruebas contra PRODUCCIÓN...")
    print("-" * 60)
    print("⚠️  NOTA: Las pruebas crearán usuarios temporales que serán eliminados automáticamente")
    print()
    
    try:
        # Ejecutar el script de pruebas original
        result = subprocess.run([sys.executable, 'test_api.py'], check=True)
        
        print()
        print("=" * 60)
        print("✅ PRUEBAS DE PRODUCCIÓN COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        print("📊 Resumen:")
        print("• Todas las validaciones pasaron")
        print("• Autenticación y autorización funcionando")
        print("• CRUD completo operativo")
        print("• Soft deletes funcionando")
        print("• Logs de auditoría operativos")
        print("• Servicio en producción estable")
        print()
        print("🔗 Enlaces útiles:")
        print(f"• API: {production_url}")
        print(f"• Docs: {production_url}/docs")
        print(f"• Redoc: {production_url}/redoc")
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("❌ ERROR EN LAS PRUEBAS DE PRODUCCIÓN")
        print("=" * 60)
        print("Las pruebas fallaron. Revisa la salida anterior para más detalles.")
        print()
        print("🔍 Pasos para solucionar problemas:")
        print("1. Verifica que la URL en .env.test sea correcta")
        print("2. Confirma que el servicio esté desplegado y ejecutándose")
        print("3. Revisa los logs del servicio en tu plataforma de hosting")
        print("4. Verifica la conectividad de red")
        print(f"5. Prueba acceder manualmente a: {production_url}/docs")
        
        sys.exit(1)
    
    except KeyboardInterrupt:
        print()
        print("⏹️  Pruebas interrumpidas por el usuario")
        sys.exit(1)

if __name__ == "__main__":
    main()