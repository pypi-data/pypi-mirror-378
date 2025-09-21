"""
API principal del generador de diagramas de flujo
"""

import os
from typing import Optional
from .core.parser import FlowParser
from .core.diagram import FlowDiagram


def generate_diagram(
    text: str,
    language: str = "es",
    filename: Optional[str] = None,
    title: str = "Diagrama de Flujo",
    background_image: Optional[str] = None
) -> str:
    """
    Genera un diagrama de flujo en formato PNG de alta calidad automáticamente.
    
    Args:
        text (str): Texto que describe el diagrama en lenguaje natural
        language (str): Idioma del texto ('es' para español, 'en' para inglés)
        filename (str, optional): Nombre del archivo de salida. Si es None, se genera automáticamente
        title (str): Título del diagrama
        background_image (str, optional): Ruta a imagen de fondo
        style (str, optional): Estilo visual ('default', 'professional', 'colorful', 'dark')
    
    Returns:
        str: Ruta al archivo PNG generado en alta calidad
    
    Raises:
        ValueError: Si el idioma no está soportado
        ImportError: Si faltan dependencias requeridas
    
    Example:
        >>> # API simplificada - alta calidad automática
        >>> filename = generate_diagram(
        ...     text="Si la variable es mayor a 5, entonces imprimir mensaje sino incrementar contador",
        ...     language="es"
        ... )
        
        >>> # Con estilo personalizado
        >>> filename = generate_diagram(
        ...     text="Proceso con estilo colorido",
        ...     language="es",
        ...     style="colorful"
        ... )
        
        >>> # Con imagen de fondo
        >>> filename = generate_diagram(
        ...     text="Proceso con imagen de fondo",
        ...     language="es",
        ...     background_image="mi_fondo.jpg"
        ... )
    """
    
    # Validar parámetros
    supported_languages = ["es", "en"]
    if language not in supported_languages:
        raise ValueError(f"Idioma '{language}' no soportado. Idiomas disponibles: {supported_languages}")
    
    if not text.strip():
        raise ValueError("El texto no puede estar vacío")
    
    # Generar nombre de archivo si no se proporciona
    if filename is None:
        filename = f"flowchart.png"
    
    # Asegurar que el archivo tenga la extensión PNG
    if not filename.endswith(".png"):
        base_name = os.path.splitext(filename)[0]
        filename = f"{base_name}.png"
    
    try:
        # 1. Parsear el texto
        parser = FlowParser(language=language)
        diagram = parser.parse(text)
        diagram.title = title
        
        # 2. Validar el diagrama
        errors = diagram.validate()
        # Comentado para evitar ruido en consola
        # if errors:
        #     print(f"Advertencias en el diagrama: {errors}")
        
        # 3. Renderizar como PNG con dimensiones automáticas
        return _render_png(diagram, filename, background_image)
    
    except ImportError as e:
        raise ImportError(f"Dependencia faltante: {e}")
    except Exception as e:
        raise RuntimeError(f"Error generando el diagrama: {e}")


def _render_png(diagram: FlowDiagram, filename: str, background_image: str = None) -> str:
    """Renderiza el diagrama como imagen PNG con dimensiones automáticas"""
    try:
        from .renderers.pillow_renderer import PillowRenderer
    except ImportError:
        raise ImportError("Pillow no está instalado. Instale con: pip install Pillow")
    
    # El renderer ahora usa flechas mejoradas automáticamente
    renderer = PillowRenderer(diagram)
    return renderer.render(filename, background_image)


def parse_text(text: str, language: str = "es") -> FlowDiagram:
    """
    Parsea texto sin generar archivo de salida, útil para análisis o procesamiento adicional.
    
    Args:
        text (str): Texto que describe el diagrama
        language (str): Idioma del texto
    
    Returns:
        FlowDiagram: Objeto diagrama parsado
    """
    parser = FlowParser(language=language)
    return parser.parse(text)


def get_supported_languages() -> list:
    """
    Retorna la lista de idiomas soportados.
    
    Returns:
        list: Lista de códigos de idiomas soportados
    """
    return ["es", "en"]


def get_supported_formats() -> list:
    """
    Retorna la lista de formatos de salida soportados.
    
    Returns:
        list: Lista de formatos soportados
    """
    return ["png", "svg"]


def get_diagram_stats(text: str, language: str = "es") -> dict:
    """
    Obtiene estadísticas del diagrama sin generar archivo de salida.
    
    Args:
        text (str): Texto que describe el diagrama
        language (str): Idioma del texto
    
    Returns:
        dict: Diccionario con estadísticas del diagrama
    """
    diagram = parse_text(text, language)
    return diagram.get_stats()


# Función de conveniencia para uso rápido
def quick_diagram(text: str, language: str = "es", format: str = "png") -> str:
    """
    Función de conveniencia para generar rápidamente un diagrama con configuración por defecto.
    
    Args:
        text (str): Texto del diagrama
        language (str): Idioma
        format (str): Formato de salida
    
    Returns:
        str: Nombre del archivo generado
    """
    return generate_diagram(
        text=text,
        language=language,
        output_format=format,
        filename=f"quick_diagram.{format}"
    )


# Alias para compatibilidad
create_flowchart = generate_diagram
