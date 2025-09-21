"""
Clase base para definir reglas de idiomas
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LanguageRules(ABC):
    """Clase base abstracta para reglas de idiomas"""
    
    def __init__(self):
        self.conditional_patterns = self.get_conditional_patterns()
        self.loop_patterns = self.get_loop_patterns()
        self.input_output_patterns = self.get_input_output_patterns()
        self.process_patterns = self.get_process_patterns()
        self.start_patterns = self.get_start_patterns()
        self.end_patterns = self.get_end_patterns()
        self.input_keywords = self.get_input_keywords()
        self.output_keywords = self.get_output_keywords()
    
    @abstractmethod
    def get_conditional_patterns(self) -> List[str]:
        """Retorna patrones regex para estructuras condicionales"""
        pass
    
    @abstractmethod
    def get_loop_patterns(self) -> List[str]:
        """Retorna patrones regex para bucles"""
        pass
    
    @abstractmethod
    def get_input_output_patterns(self) -> List[str]:
        """Retorna patrones regex para entrada/salida"""
        pass
    
    @abstractmethod
    def get_process_patterns(self) -> List[str]:
        """Retorna patrones regex para procesos"""
        pass
    
    @abstractmethod
    def get_start_patterns(self) -> List[str]:
        """Retorna patrones regex para nodos de inicio"""
        pass
    
    @abstractmethod
    def get_end_patterns(self) -> List[str]:
        """Retorna patrones regex para nodos de fin"""
        pass
    
    @abstractmethod
    def get_input_keywords(self) -> List[str]:
        """Retorna palabras clave para operaciones de entrada"""
        pass
    
    @abstractmethod
    def get_output_keywords(self) -> List[str]:
        """Retorna palabras clave para operaciones de salida"""
        pass
    
    @abstractmethod
    def get_start_text(self) -> str:
        """Retorna el texto para el nodo de inicio"""
        pass
    
    @abstractmethod
    def get_end_text(self) -> str:
        """Retorna el texto para el nodo de fin"""
        pass
    
    def normalize_text(self, text: str) -> str:
        """Normaliza el texto según las reglas del idioma"""
        # Implementación base simple
        return text.strip().lower()
    
    def get_all_patterns(self) -> Dict[str, List[str]]:
        """Retorna todos los patrones organizados por tipo"""
        return {
            "conditional": self.conditional_patterns,
            "loop": self.loop_patterns,
            "input_output": self.input_output_patterns,
            "process": self.process_patterns,
            "end": self.end_patterns
        }
