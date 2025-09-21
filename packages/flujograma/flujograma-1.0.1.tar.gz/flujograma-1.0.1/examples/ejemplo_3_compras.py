import os
import sys

# Agregar src al path para importar flujograma
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flujograma import generate_diagram

"""
Ejemplo 3: Proceso de Compras Online
Demuestra un flujo de comercio electrónico completo
"""

def main():
    print("Ejemplo 3: Proceso de Compras Online")
    print("=" * 40)
    
    # Texto del diagrama en español
    texto_diagrama = """
INICIO
Mostrar catálogo de productos
Seleccionar producto
Agregar al carrito
SI carrito tiene productos ENTONCES proceder al pago SINO volver al catálogo
Ingresar datos de pago
Procesar transacción
Mostrar confirmación
FIN
    """
    
    # Generar diagrama
    try:
        archivo_generado = generate_diagram(
            text=texto_diagrama,
            language="es",
            filename="ejemplo_3_compras.png",
            title="Proceso de Compras Online"
        )
        
        print(f"Diagrama generado exitosamente: {archivo_generado}")
        print("Descripción: Flujo completo de compra en línea")
        print("Características: Proceso de negocio con validación")
        
    except Exception as e:
        print(f"Error al generar diagrama: {e}")

if __name__ == "__main__":
    main()
