"""
Reglas de idioma para español
"""

from typing import List
from .base import LanguageRules


class SpanishRules(LanguageRules):
    """Implementación de reglas para el idioma español"""
    
    def get_conditional_patterns(self) -> List[str]:
        """Patrones para estructuras condicionales en español"""
        return [
            r'si\s+(.+?)\s*,?\s*entonces\s+(.+?)(?:\s+sino\s+(.+?))?[.]?$',
            r'si\s+(.+?)\s*,?\s*(.+?)(?:\s+de\s+lo\s+contrario\s+(.+?))?[.]?$',
            r'cuando\s+(.+?)\s*,?\s*(.+?)[.]?$',
            r'en\s+caso\s+de\s+que\s+(.+?)\s*,?\s*(.+?)[.]?$'
        ]
    
    def get_loop_patterns(self) -> List[str]:
        """Patrones para bucles en español"""
        return [
            r'mientras\s+(.+?)\s*,?\s*(.+?)[.]?$',
            r'repetir\s+(.+?)\s+mientras\s+(.+?)[.]?$',
            r'para\s+cada\s+(.+?)\s+en\s+(.+?)\s*,?\s*(.+?)[.]?$',
            r'iterar\s+(.+?)\s+veces\s*,?\s*(.+?)[.]?$'
        ]
    
    def get_input_output_patterns(self) -> List[str]:
        """Patrones para entrada/salida en español"""
        return [
            r'(?:leer|ingresar|capturar|solicitar)\s+(.+?)[.]?$',
            r'(?:imprimir|mostrar|escribir|visualizar)\s+(.+?)[.]?$',
            r'(?:entrada|input):\s*(.+?)[.]?$',
            r'(?:salida|output):\s*(.+?)[.]?$'
        ]
    
    def get_process_patterns(self) -> List[str]:
        """Patrones para procesos en español"""
        return [
            r'(?:calcular|computar|procesar)\s+(.+?)[.]?$',
            r'(?:asignar|establecer|definir)\s+(.+?)[.]?$',
            r'(?:ejecutar|realizar|hacer)\s+(.+?)[.]?$',
            r'(?:llamar|invocar)\s+(.+?)[.]?$'
        ]
    
    def get_start_patterns(self) -> List[str]:
        """Patrones para nodos de inicio en español"""
        return [
            r'^(?:inicio|iniciar|comenzar|empezar|start)[.]?$',
        ]
    
    def get_end_patterns(self) -> List[str]:
        """Patrones para nodos de fin en español"""
        return [
            r'^(?:fin|final|terminar|acabar)[.]?$',
            r'^(?:salir|exit|return)[.]?$'
        ]
    
    def get_input_keywords(self) -> List[str]:
        """Palabras clave para operaciones de entrada en español"""
        return [
            'leer', 'ingresar', 'capturar', 'solicitar', 'pedir',
            'entrada', 'input', 'introducir', 'teclear'
        ]
    
    def get_output_keywords(self) -> List[str]:
        """Palabras clave para operaciones de salida en español"""
        return [
            'imprimir', 'mostrar', 'escribir', 'visualizar', 'presentar',
            'salida', 'output', 'pantalla', 'consola', 'display'
        ]
    
    def get_start_text(self) -> str:
        """Texto para el nodo de inicio en español"""
        return "INICIO"
    
    def get_end_text(self) -> str:
        """Texto para el nodo de fin en español"""
        return "FIN"
    
    def normalize_text(self, text: str) -> str:
        """Normaliza texto en español"""
        # Implementación específica para español
        text = super().normalize_text(text)
        
        # Reemplazos específicos del español
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u'
        }
        
        for accented, plain in replacements.items():
            text = text.replace(accented, plain)
        
        return text
