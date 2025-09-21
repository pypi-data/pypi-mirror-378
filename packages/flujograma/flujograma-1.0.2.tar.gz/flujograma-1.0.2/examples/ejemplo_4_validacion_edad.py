from flujograma import generate_diagram

"""
Ejemplo 4: Validación de Edad
Demuestra un proceso de validación con múltiples condiciones
"""

def main():
    print("Ejemplo 4: Validación de Edad")
    print("=" * 40)
    
    # Texto del diagrama en español
    texto_diagrama = """
INICIO
Solicitar fecha de nacimiento
Calcular edad actual
SI edad es mayor a 18 ENTONCES permitir acceso SINO denegar acceso
Registrar intento de acceso
Mostrar mensaje al usuario
FIN
    """
    
    # Generar diagrama
    try:
        archivo_generado = generate_diagram(
            text=texto_diagrama,
            language="es",
            filename="ejemplo_4_validacion_edad.png",
            title="Validación de Edad"
        )
        
        print(f"Diagrama generado exitosamente: {archivo_generado}")
        print("Descripción: Sistema de control de acceso por edad")
        print("Características: Validación con cálculo de edad")
        
    except Exception as e:
        print(f"Error al generar diagrama: {e}")

if __name__ == "__main__":
    main()
