import os
import sys

# Agregar src al path para importar flujograma
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flujograma import generate_diagram

"""
Ejemplo 1: Sistema de Login
Demuestra un proceso de autenticación básico con validación
"""

def main():
    print("Ejemplo 1: Sistema de Login")
    print("=" * 40)
    
    # Texto del diagrama en español
    texto_diagrama = """
Mostrar pantalla de login
Leer nombre de usuario
Leer contraseña
SI credenciales son válidas ENTONCES mostrar dashboard SINO mostrar mensaje de error
FIN
    """
    
    # Generar diagrama
    try:
        archivo_generado = generate_diagram(
            text=texto_diagrama,
            language="es",
            filename="ejemplo_1_sistema_login.png",
            title="Sistema de Login"
        )
        
        print(f"Diagrama generado exitosamente: {archivo_generado}")
        print("Descripción: Proceso de autenticación de usuario")
        print("Características: Condicional simple con dos ramas")
        
    except Exception as e:
        print(f"Error al generar diagrama: {e}")

if __name__ == "__main__":
    main()
