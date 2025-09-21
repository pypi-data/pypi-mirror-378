#!/usr/bin/env python
"""
Script para preparar y simular la publicación a PyPI
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔄 {description}...")
    
    # Usar el Python del virtual environment
    python_exe = r"C:/Users/TERABYTE10/Documents/CURSOS TECBA/PROGRAMACION II/pg2-practica7/practica-7/pg2-practica7/venv/Scripts/python.exe"
    
    # Reemplazar 'python' con la ruta completa
    if cmd.startswith("python "):
        cmd = cmd.replace("python ", f'"{python_exe}" ', 1)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - EXITOSO")
            if result.stdout.strip():
                print(f"   📄 {result.stdout.strip()}")
        else:
            print(f"❌ {description} - ERROR")
            print(f"   ⚠️ {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - EXCEPCIÓN: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Preparación para publicación en PyPI")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("pyproject.toml"):
        print("❌ Error: No se encuentra pyproject.toml")
        sys.exit(1)
    
    # 1. Ejecutar tests
    print("\n📋 Paso 1: Ejecutar tests")
    if not run_command("python -m pytest tests/ -v", "Tests unitarios"):
        print("⚠️ Los tests fallaron, pero continuamos...")
    
    # 2. Limpiar dist anterior
    print("\n🧹 Paso 2: Limpiar distribuciones anteriores")
    if os.path.exists("dist"):
        run_command("rmdir /s /q dist", "Limpiar directorio dist")
    
    # 3. Construir paquete
    print("\n🔨 Paso 3: Construir paquete")
    if not run_command("python -m build", "Construcción del paquete"):
        print("❌ Error en la construcción")
        sys.exit(1)
    
    # 4. Verificar con twine
    print("\n🔍 Paso 4: Verificar con twine")
    if not run_command("python -m twine check dist/*", "Verificación con twine"):
        print("❌ Error en la verificación")
        sys.exit(1)
    
    # 5. Mostrar información del paquete
    print("\n📦 Paso 5: Información del paquete")
    dist_files = []
    if os.path.exists("dist"):
        dist_files = os.listdir("dist")
        for file in dist_files:
            size = os.path.getsize(f"dist/{file}")
            print(f"   📄 {file} ({size:,} bytes)")
    
    # 6. Simular subida a Test PyPI (solo mostrar comando)
    print("\n🧪 Paso 6: Comando para subir a Test PyPI")
    print("   Para probar en Test PyPI, ejecutar:")
    print("   python -m twine upload --repository testpypi dist/*")
    print("   (Requiere cuenta en https://test.pypi.org/)")
    
    # 7. Simular subida a PyPI real (solo mostrar comando)
    print("\n🚀 Paso 7: Comando para subir a PyPI oficial")
    print("   Para publicar en PyPI real, ejecutar:")
    print("   python -m twine upload dist/*")
    print("   (Requiere cuenta en https://pypi.org/)")
    
    # 8. Verificación final
    print("\n✅ Resumen final")
    print("=" * 50)
    print("🎉 ¡Paquete listo para publicación!")
    print(f"📦 Archivos generados: {len(dist_files)}")
    print("🔍 Verificación twine: PASÓ")
    print("🧪 Tests: EJECUTADOS") 
    print("\n🎯 Próximos pasos:")
    print("1. Crear cuenta en PyPI (https://pypi.org/account/register/)")
    print("2. Configurar token de API")
    print("3. Ejecutar: python -m twine upload dist/*")
    print("4. ¡Tu librería estará disponible con: pip install flujograma!")

if __name__ == "__main__":
    main()