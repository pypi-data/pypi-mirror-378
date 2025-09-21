"""
Sistema de conectores (Edges) inspirado en diagrams.mingrammer.com
Implementación con Pillow para máximo rendimiento offline
"""

from typing import Dict, Any, Optional, Tuple
from enum import Enum


class EdgeStyle(Enum):
    """Estilos de línea disponibles"""
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"
    BOLD = "bold"


class EdgeColor:
    """Colores predefinidos para las conexiones"""
    BLACK = "#000000"
    GRAY = "#808080"
    RED = "#FF0000"
    GREEN = "#008000"
    BLUE = "#0000FF"
    ORANGE = "#FFA500"
    PURPLE = "#800080"
    BROWN = "#A52A2A"
    FIREBRICK = "#B22222"
    DARKGREEN = "#006400"
    DARKORANGE = "#FF8C00"


class Edge:
    """
    Representa una conexión entre dos nodos con estilo personalizable
    Inspirado en diagrams.mingrammer.com pero usando Pillow
    """
    
    def __init__(self, 
                 source_node=None, 
                 target_node=None, 
                 label: str = "",
                 color: str = EdgeColor.BLACK,
                 style: EdgeStyle = EdgeStyle.SOLID,
                 width: int = 2,
                 **kwargs):
        """
        Inicializa una conexión entre nodos
        
        Args:
            source_node: Nodo origen
            target_node: Nodo destino  
            label: Texto a mostrar en la conexión
            color: Color de la línea (hex)
            style: Estilo de línea (EdgeStyle)
            width: Grosor de la línea
            **kwargs: Parámetros adicionales
        """
        self.source_node = source_node
        self.target_node = target_node
        self.label = label
        self.color = color
        self.style = style
        self.width = width
        
        # Parámetros adicionales de diagrams
        self.minlen = kwargs.get('minlen', 1)
        self.constraint = kwargs.get('constraint', True)
        self.head_port = kwargs.get('head_port', None)
        self.tail_port = kwargs.get('tail_port', None)
        
    def __rshift__(self, other):
        """Operador >> para encadenar conexiones"""
        if hasattr(other, 'connect_to'):
            return self.target_node.connect_to(other, self._get_style_dict())
        return other
        
    def __lshift__(self, other):
        """Operador << para conexiones inversas"""
        if hasattr(other, 'connect_to'):
            return other.connect_to(self.source_node, self._get_style_dict())
        return other
        
    def _get_style_dict(self) -> Dict[str, Any]:
        """Retorna el diccionario de estilo para esta conexión"""
        return {
            'color': self.color,
            'style': self.style,
            'width': self.width,
            'label': self.label
        }
        
    def get_render_params(self) -> Dict[str, Any]:
        """Retorna parámetros para el renderer de Pillow"""
        return {
            'color': self.color,
            'style': self.style.value,
            'width': self.width,
            'label': self.label,
            'source_x': getattr(self.source_node, 'x', 0),
            'source_y': getattr(self.source_node, 'y', 0),
            'target_x': getattr(self.target_node, 'x', 0),
            'target_y': getattr(self.target_node, 'y', 0),
            'source_width': getattr(self.source_node, 'width', 120),
            'source_height': getattr(self.source_node, 'height', 80),
            'target_width': getattr(self.target_node, 'width', 120),
            'target_height': getattr(self.target_node, 'height', 80)
        }


# ===== FUNCIONES DE CONVENIENCIA =====
def edge(color: str = EdgeColor.BLACK, 
         style: EdgeStyle = EdgeStyle.SOLID,
         label: str = "",
         width: int = 2) -> Dict[str, Any]:
    """
    Función de conveniencia para crear estilos de edge
    Uso: node1 >> edge(color="red", style=EdgeStyle.DASHED) >> node2
    """
    return {
        'color': color,
        'style': style,
        'label': label,
        'width': width
    }


def red_edge(label: str = "", style: EdgeStyle = EdgeStyle.SOLID) -> Dict[str, Any]:
    """Edge rojo"""
    return edge(color=EdgeColor.RED, label=label, style=style)


def green_edge(label: str = "", style: EdgeStyle = EdgeStyle.SOLID) -> Dict[str, Any]:
    """Edge verde"""
    return edge(color=EdgeColor.GREEN, label=label, style=style)


def blue_edge(label: str = "", style: EdgeStyle = EdgeStyle.SOLID) -> Dict[str, Any]:
    """Edge azul"""
    return edge(color=EdgeColor.BLUE, label=label, style=style)


def dashed_edge(color: str = EdgeColor.BLACK, label: str = "") -> Dict[str, Any]:
    """Edge punteado"""
    return edge(color=color, style=EdgeStyle.DASHED, label=label)


def dotted_edge(color: str = EdgeColor.BLACK, label: str = "") -> Dict[str, Any]:
    """Edge con puntos"""
    return edge(color=color, style=EdgeStyle.DOTTED, label=label)


def bold_edge(color: str = EdgeColor.BLACK, label: str = "") -> Dict[str, Any]:
    """Edge grueso"""
    return edge(color=color, style=EdgeStyle.BOLD, label=label, width=4)


# ===== EJEMPLOS DE USO =====
"""
Ejemplos de uso inspirados en diagrams.mingrammer.com:

# Conexión simple
node1 >> node2

# Conexión con estilo
node1 >> edge(color="red", style=EdgeStyle.DASHED) >> node2

# Conexión con etiqueta
node1 >> edge(label="process") >> node2

# Conexiones múltiples
node1 >> [node2, node3, node4]

# Conexión compleja como en diagrams
metrics << Edge(color="firebrick", style="dashed") << monitoring
grpcsvc >> Edge(color="brown") >> primary
aggregator >> Edge(label="parse") >> kafka >> Edge(color="black", style="bold") >> spark
"""