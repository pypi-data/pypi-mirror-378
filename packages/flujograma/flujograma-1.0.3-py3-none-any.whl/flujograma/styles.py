"""
Configuración de estilos visuales para los diagramas de flujo
Modifica estos valores para personalizar la apariencia de tus diagramas
"""

from typing import Dict, Tuple


class DiagramStyles:
    """Clase que contiene todos los estilos configurables del diagrama"""
    
    def __init__(self):
        # =================================================================
        # DIMENSIONES Y ESPACIADO
        # =================================================================
        self.base_width = 1800          # Ancho base del canvas
        self.margin = 100               # Márgenes del diagrama
        self.node_width = 200           # Ancho de los nodos
        self.node_height = 100          # Alto de los nodos
        self.spacing_y = 180            # Espaciado vertical entre nodos
        self.spacing_x = 250            # Espaciado horizontal entre ramas
        
        # =================================================================
        # FUENTES Y TEXTO
        # =================================================================
        self.font_size = 16             # Tamaño de fuente principal
        self.font_title_size = 32       # Tamaño de fuente del título
        self.font_small_size = 14       # Tamaño de fuente pequeña
        
        # =================================================================
        # COLORES - Modifica estos para cambiar la apariencia
        # =================================================================
        self.colors = {
            # Fondo general
            'background': (242, 231, 208),      # #f2e7d0 - Fondo beige cálido
            
            # Nodos de proceso (rectángulos)
            'node_fill': (237, 141, 114),       # Salmón #ed8d72
            'node_border': (237, 141, 114),     # Sin borde visible - mismo color  
            'node_border_width': 0,             # Sin borde
            
            # Nodos de decisión (rombos)
            'decision_fill': (241, 187, 110),   # Amarillo suave #f1bb6e
            'decision_border': (241, 187, 110), # Sin borde visible - mismo color
            'decision_border_width': 0,         # Sin borde
            
            # Nodos de inicio/fin (óvalos)
            'start_end_fill': (70, 114, 207),   # Azul #4672cf
            'start_end_border': (70, 114, 207), # Sin borde visible - mismo color
            'start_end_border_width': 0,        # Sin borde
            
            # Nodos de entrada/salida (paralelogramos)
            'input_output_fill': (36, 82, 76),  # Verde oscuro #24524c
            'input_output_border': (36, 82, 76), # Sin borde visible - mismo color
            'input_output_border_width': 0,      # Sin borde
            
            # Texto
            'text': (30, 30, 30),               # Gris muy oscuro
            'text_title': (0, 0, 0),            # Negro para título
            
            # Conexiones y flechas
            'connection': (80, 80, 80),         # Gris para líneas
            'arrow_fill': (60, 60, 60),         # Color de relleno de flechas
            'arrow_outline': (40, 40, 40),      # Color del borde de flechas
        }
        
        # =================================================================
        # CONFIGURACIÓN DE FLECHAS
        # =================================================================
        self.arrow_config = {
            'line_width': 3,                    # Grosor de la línea
            'arrow_length': 18,                 # Longitud de la punta
            'arrow_width': 12,                  # Ancho de la punta
            'curve_depth': 8,                   # Profundidad de la curva interna
            'style': 'programmatic',            # 'programmatic' o 'image'
            'image_path': None,                 # Ruta a imagen PNG si usas style='image'
        }
        
        # =================================================================
        # EFECTOS VISUALES
        # =================================================================
        self.effects = {
            'drop_shadow': True,                # Sombra en los nodos
            'shadow_offset': (3, 3),            # Desplazamiento de sombra
            'shadow_color': (200, 200, 200),    # Color de sombra
            'rounded_corners': True,            # Esquinas redondeadas
            'corner_radius': 10,                # Radio de las esquinas
            'gradient_fill': False,             # Relleno con gradiente
        }
        
    def get_node_style(self, node_type: str) -> Dict:
        """Retorna el estilo para un tipo específico de nodo"""
        styles = {
            'process': {
                'fill': self.colors['node_fill'],
                'border': self.colors['node_border'],
                'border_width': self.colors['node_border_width'],
                'shape': 'rectangle'
            },
            'decision': {
                'fill': self.colors['decision_fill'],
                'border': self.colors['decision_border'],
                'border_width': self.colors['decision_border_width'],
                'shape': 'diamond'
            },
            'start': {
                'fill': self.colors['start_end_fill'],
                'border': self.colors['start_end_border'],
                'border_width': self.colors['start_end_border_width'],
                'shape': 'oval'
            },
            'end': {
                'fill': self.colors['start_end_fill'],
                'border': self.colors['start_end_border'],
                'border_width': self.colors['start_end_border_width'],
                'shape': 'oval'
            },
            'input_output': {
                'fill': self.colors['input_output_fill'],
                'border': self.colors['input_output_border'],
                'border_width': self.colors['input_output_border_width'],
                'shape': 'parallelogram'
            }
        }
        return styles.get(node_type, styles['process'])


# Estilos predefinidos que puedes usar

def get_professional_style():
    """Estilo profesional con colores sobrios"""
    style = DiagramStyles()
    style.colors.update({
        'background': (248, 248, 248),
        'node_fill': (255, 255, 255),
        'node_border': (100, 100, 100),
        'decision_fill': (240, 240, 255),
        'decision_border': (100, 100, 200),
        'start_end_fill': (245, 255, 245),
        'start_end_border': (100, 150, 100),
        'connection': (100, 100, 100),
    })
    return style

def get_colorful_style():
    """Estilo colorido y llamativo"""
    style = DiagramStyles()
    style.colors.update({
        'background': (250, 250, 255),
        'node_fill': (255, 250, 240),
        'node_border': (200, 100, 50),
        'decision_fill': (255, 240, 245),
        'decision_border': (220, 20, 60),
        'start_end_fill': (240, 255, 240),
        'start_end_border': (50, 205, 50),
        'input_output_fill': (240, 248, 255),
        'input_output_border': (30, 144, 255),
        'connection': (70, 70, 70),
    })
    return style

def get_dark_style():
    """Estilo oscuro/modo nocturno"""
    style = DiagramStyles()
    style.colors.update({
        'background': (45, 45, 45),
        'node_fill': (70, 70, 70),
        'node_border': (200, 200, 200),
        'decision_fill': (80, 60, 80),
        'decision_border': (255, 180, 100),
        'start_end_fill': (60, 80, 60),
        'start_end_border': (150, 255, 150),
        'input_output_fill': (60, 70, 90),
        'input_output_border': (100, 180, 255),
        'text': (240, 240, 240),
        'text_title': (255, 255, 255),
        'connection': (180, 180, 180),
    })
    return style
