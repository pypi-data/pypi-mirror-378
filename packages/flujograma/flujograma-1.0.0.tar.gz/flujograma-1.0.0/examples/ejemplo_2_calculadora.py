import os
import sys

# Agregar src al path para importar flujograma
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flujograma import generate_diagram


"""
Ejemplo 2: Calculadora de Números
Demuestra un proceso de cálculo con validación de entrada
"""

def main():
    print("Ejemplo 2: Calculadora de Números")
    print("=" * 40)
    
    # Texto del diagrama en español
    texto_diagrama = """
INICIO
Mostrar menú de operaciones
Leer opción del usuario
Leer primer número
Leer segundo número
SI opción es suma ENTONCES calcular suma SINO verificar otras operaciones
Mostrar resultado
FIN
    """
    
    # Generar diagrama
    try:
        archivo_generado = generate_diagram(
            text=texto_diagrama,
            language="es",
            filename="ejemplo_2_calculadora.png",
            title="Calculadora de Números"
        )
        
        print(f"Diagrama generado exitosamente: {archivo_generado}")
        print("Descripción: Proceso de cálculo matemático básico")
        print("Características: Flujo secuencial con decisión")
        
    except Exception as e:
        print(f"Error al generar diagrama: {e}")

if __name__ == "__main__":
    main()
