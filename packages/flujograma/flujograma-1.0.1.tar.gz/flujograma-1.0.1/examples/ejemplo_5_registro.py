import os
import sys

# Agregar src al path para importar flujograma
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flujograma import generate_diagram

"""
Ejemplo 5: Proceso de Registro de Usuario
Demuestra un flujo de registro con validaciones múltiples
"""

def main():
    print("Ejemplo 5: Proceso de Registro de Usuario")
    print("=" * 40)
    
    # Texto del diagrama en español
    texto_diagrama = """
INICIO
Mostrar formulario de registro
Leer nombre de usuario
Leer correo electrónico
Leer contraseña
SI datos son válidos ENTONCES crear cuenta SINO mostrar errores de validación
Enviar email de confirmación
Mostrar mensaje de éxito
FIN
    """
    
    # Generar diagrama
    try:
        archivo_generado = generate_diagram(
            text=texto_diagrama,
            language="es",
            filename="ejemplo_5_registro.png",
            title="Proceso de Registro de Usuario"
        )
        
        print(f"Diagrama generado exitosamente: {archivo_generado}")
        print("Descripción: Flujo completo de registro de nuevo usuario")
        print("Características: Proceso con validación y notificación")
        
    except Exception as e:
        print(f"Error al generar diagrama: {e}")

if __name__ == "__main__":
    main()
