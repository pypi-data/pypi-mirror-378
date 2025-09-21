"""
Flujograma

Una librería Python para generar diagramas de flujo a partir de texto en lenguaje natural controlado.
"""

__version__ = "0.1.0"
__author__ = "CubeFreaKLab"

from .main import generate_diagram, get_diagram_stats, parse_text

__all__ = ["generate_diagram", "get_diagram_stats", "parse_text"]
