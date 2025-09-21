"""
Reglas de idioma para inglés
"""

from typing import List
from .base import LanguageRules


class EnglishRules(LanguageRules):
    """Implementación de reglas para el idioma inglés"""
    
    def get_conditional_patterns(self) -> List[str]:
        """Patrones para estructuras condicionales en inglés"""
        return [
            r'if\s+(.+?)\s*,?\s*then\s+(.+?)(?:\s+else\s+(.+?))?[.]?$',
            r'if\s+(.+?)\s*,?\s*(.+?)(?:\s+otherwise\s+(.+?))?[.]?$',
            r'when\s+(.+?)\s*,?\s*(.+?)[.]?$',
            r'in\s+case\s+(?:of\s+)?(.+?)\s*,?\s*(.+?)[.]?$'
        ]
    
    def get_loop_patterns(self) -> List[str]:
        """Patrones para bucles en inglés"""
        return [
            r'while\s+(.+?)\s*,?\s*(.+?)[.]?$',
            r'repeat\s+(.+?)\s+while\s+(.+?)[.]?$',
            r'for\s+each\s+(.+?)\s+in\s+(.+?)\s*,?\s*(.+?)[.]?$',
            r'iterate\s+(.+?)\s+times\s*,?\s*(.+?)[.]?$',
            r'loop\s+(.+?)\s+until\s+(.+?)[.]?$'
        ]
    
    def get_input_output_patterns(self) -> List[str]:
        """Patrones para entrada/salida en inglés"""
        return [
            r'(?:read|input|get|capture|request)\s+(.+?)[.]?$',
            r'(?:print|display|show|write|output)\s+(.+?)[.]?$',
            r'(?:input|enter):\s*(.+?)[.]?$',
            r'(?:output|result):\s*(.+?)[.]?$'
        ]
    
    def get_process_patterns(self) -> List[str]:
        """Patrones para procesos en inglés"""
        return [
            r'(?:calculate|compute|process)\s+(.+?)[.]?$',
            r'(?:assign|set|define)\s+(.+?)[.]?$',
            r'(?:execute|perform|do)\s+(.+?)[.]?$',
            r'(?:call|invoke)\s+(.+?)[.]?$'
        ]
    
    def get_start_patterns(self) -> List[str]:
        """Patrones para nodos de inicio en inglés"""
        return [
            r'^(?:start|begin|initialize|init|commence)[.]?$',
        ]
    
    def get_end_patterns(self) -> List[str]:
        """Patrones para nodos de fin en inglés"""
        return [
            r'^(?:end|finish|terminate|stop)[.]?$',
            r'^(?:exit|return|quit)[.]?$'
        ]
    
    def get_input_keywords(self) -> List[str]:
        """Palabras clave para operaciones de entrada en inglés"""
        return [
            'read', 'input', 'get', 'capture', 'request', 'ask',
            'enter', 'type', 'scan', 'obtain'
        ]
    
    def get_output_keywords(self) -> List[str]:
        """Palabras clave para operaciones de salida en inglés"""
        return [
            'print', 'display', 'show', 'write', 'output', 'present',
            'console', 'screen', 'visualize', 'render'
        ]
    
    def get_start_text(self) -> str:
        """Texto para el nodo de inicio en inglés"""
        return "START"
    
    def get_end_text(self) -> str:
        """Texto para el nodo de fin en inglés"""
        return "END"
    
    def normalize_text(self, text: str) -> str:
        """Normaliza texto en inglés"""
        # Implementación específica para inglés
        text = super().normalize_text(text)
        
        # Contracciones comunes en inglés
        contractions = {
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'ll": " will",
            "'re": " are",
            "'ve": " have",
            "'d": " would"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        return text
