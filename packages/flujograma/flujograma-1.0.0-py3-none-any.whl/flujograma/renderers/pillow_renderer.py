"""
Renderizador usando Pillow para generar imágenes PNG
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Dict, Optional
import math
import os
from pathlib import Path
from ..core.diagram import FlowDiagram
from ..core.ast_nodes import FlowNode, NodeType
from ..styles import DiagramStyles


class PillowRenderer:
    """Renderizador que usa Pillow para crear imágenes PNG de diagramas de flujo de alta calidad"""
    
    def __init__(self, diagram: FlowDiagram, style: DiagramStyles = None):
        self.diagram = diagram
        
        # Configuración automática de alta calidad (manteniendo tu diseño original)
        self.base_width = 1000    # Ancho base un poco más amplio para aspecto más cuadrado
        self.margin = 50          # Márgenes más ajustados
        self.node_width = 200     # Nodos más grandes para mejor legibilidad
        self.node_height = 100    # Altura aumentada
        self.font_size = 18       # Fuente MÁS GRANDE: de 16 a 18px
        self.spacing_y = 400      # ESPACIADO MUCHO MAYOR: de 300 a 400px para flechas largas
        
        # Colores mejorados con fondo #ececec (manteniendo tu diseño)
        self.colors = {
            'background': (242, 231, 208),      # Fondo #f2e7d0 (beige cálido)
            'node_fill': (237, 141, 114),       # Rectángulos #ed8d72 (salmón)
            'node_border': (237, 141, 114),     # Sin borde visible - mismo color
            'decision_fill': (241, 187, 110),   # Rombos #f1bb6e (amarillo suave)
            'decision_border': (241, 187, 110), # Sin borde visible - mismo color
            'start_end_fill': (70, 114, 207),   # Óvalos #4672cf (azul)
            'start_end_border': (70, 114, 207), # Sin borde visible - mismo color
            'input_output_fill': (36, 82, 76),  # Paralelogramos #24524c (verde oscuro)
            'input_output_border': (36, 82, 76), # Sin borde visible - mismo color
            'text': (30, 30, 30),               # Gris muy oscuro para legibilidad
            'connection': (80, 80, 80),          # Gris para flechas
            'decision_label_fill': (149, 140, 222), # Círculos para Sí/No #958cde
            'decision_label_text': (255, 255, 255)  # Texto blanco en círculos
        }
        
        # Configuración de flechas mejoradas
        self.arrow_config = {
            'line_width': 2,             # Reducido de 3 a 2 para líneas más finas
            'arrow_length': 18,
            'arrow_width': 12,
            'curve_depth': 8,
            'use_png_arrow': True,  # Para usar tu arrow.png
        }
        
        # Intentar cargar fuentes mejores
        self.font = self._load_best_font(self.font_size, bold=True)  # NEGRITA para texto de nodos
        self.font_bold = self._load_best_font(self.font_size + 2, bold=True)  # Aún más negrita
        self.font_title = self._load_best_font(36, bold=True)  # Título más grande: 36px (era 32px)
        self.font_small = self._load_best_font(self.font_size - 2)
    
    def _load_best_font(self, size: int, bold: bool = False):
        """Carga la mejor fuente disponible, priorizando las incluidas en el paquete"""
        import os
        from pathlib import Path
        
        # Ruta a las fuentes incluidas en el paquete
        package_dir = Path(__file__).parent.parent
        fonts_dir = package_dir / "assets" / "fonts"
        
        font_paths = []
        
        if bold:
            font_paths = [
                # 1. Fuentes incluidas en el paquete (PRIORIDAD MÁXIMA)
                str(fonts_dir / "ProductSans-Bold.ttf"),
                str(fonts_dir / "Roboto-Bold.ttf"),
                str(fonts_dir / "GoogleSans-Bold.ttf"),
                
                # 2. Fuentes del sistema (Windows)
                "C:/Windows/Fonts/ProductSans-Bold.ttf",
                "C:/Windows/Fonts/Product Sans Bold.ttf",
                "C:/Windows/Fonts/segoeuib.ttf",   # Segoe UI Bold
                "C:/Windows/Fonts/arialbd.ttf",    # Arial Bold
                "C:/Windows/Fonts/calibrib.ttf",   # Calibri Bold
                
                # 3. macOS
                "/System/Library/Fonts/SF-Pro-Text-Bold.ttf",
                "/System/Library/Fonts/Arial Bold.ttf",
                
                # 4. Linux
                "/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
            ]
        else:
            font_paths = [
                # 1. Fuentes incluidas en el paquete (PRIORIDAD MÁXIMA)
                str(fonts_dir / "ProductSans-Regular.ttf"),
                str(fonts_dir / "Roboto-Regular.ttf"),
                str(fonts_dir / "GoogleSans-Regular.ttf"),
                
                # 2. Fuentes del sistema (Windows)
                "C:/Windows/Fonts/ProductSans-Regular.ttf",
                "C:/Windows/Fonts/Product Sans Regular.ttf",
                "C:/Windows/Fonts/segoeui.ttf",    # Segoe UI
                "C:/Windows/Fonts/arial.ttf",      # Arial
                "C:/Windows/Fonts/calibri.ttf",    # Calibri
                
                # 3. macOS
                "/System/Library/Fonts/SF-Pro-Text-Regular.ttf",
                "/System/Library/Fonts/Arial.ttf",
                
                # 4. Linux
                "/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
            ]
        
        # Intentar cargar fuentes en orden de prioridad
        for font_path in font_paths:
            try:
                if Path(font_path).exists():
                    return ImageFont.truetype(font_path, size)
            except Exception:
                continue
        
        # Fallback final: fuente por defecto del sistema
        return ImageFont.load_default()

    def _calculate_optimal_dimensions(self):
        """Calcula las dimensiones óptimas del canvas basado en el contenido"""
        if not self.diagram.nodes:
            return self.base_width, 600
        
        # Calcular layout si no está hecho
        if not any(hasattr(node, 'position') and node.position for node in self.diagram.nodes):
            self.diagram.calculate_layout()
        
        # Encontrar el rango de posiciones
        min_x = min(node.position[0] if hasattr(node, 'position') and node.position else 0 
                   for node in self.diagram.nodes)
        max_x = max(node.position[0] if hasattr(node, 'position') and node.position else 0 
                   for node in self.diagram.nodes)
        min_y = min(node.position[1] if hasattr(node, 'position') and node.position else 0 
                   for node in self.diagram.nodes)
        max_y = max(node.position[1] if hasattr(node, 'position') and node.position else 0 
                   for node in self.diagram.nodes)
        
        # Calcular dimensiones necesarias
        content_width = max_x - min_x + self.node_width
        content_height = max_y - min_y + self.node_height
        
        # Agregar márgenes y espacio para título más grande
        self.width = max(self.base_width, content_width + 2 * self.margin)
        self.height = content_height + 2 * self.margin + 140  # +140 para título más grande (era +100)
        
        # Asegurar calidad mínima ajustada al contenido
        self.width = max(self.width, 600)   # Reducido de 1600 a 600
        self.height = max(self.height, 400) # Reducido de 800 a 400
        
        return self.width, self.height

    def _draw_custom_arrow(self, draw, start_pos, end_pos, color=(80, 80, 80)):
        """Dibuja una flecha personalizada elegante como en tu imagen"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Calcular ángulo de la flecha
        import math
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
            
        # Normalizar dirección
        dx_norm = dx / length
        dy_norm = dy / length
        
        # Dibujar línea principal más gruesa y suave
        line_width = 3
        draw.line([x1, y1, x2, y2], fill=color, width=line_width)
        
        # Parámetros de la punta de flecha (más elegante)
        arrow_length = 15
        arrow_width = 8
        
        # Calcular puntos de la punta de flecha
        back_x = x2 - arrow_length * dx_norm
        back_y = y2 - arrow_length * dy_norm
        
        # Perpendicular para los lados de la flecha
        perp_x = -dy_norm * arrow_width
        perp_y = dx_norm * arrow_width
        
        # Puntos de la punta de flecha
        arrow_points = [
            (x2, y2),  # Punta
            (back_x + perp_x, back_y + perp_y),  # Lado izquierdo
            (back_x, back_y),  # Base (centro)
            (back_x - perp_x, back_y - perp_y),  # Lado derecho
        ]
        
        # Dibujar la punta de flecha rellena
        draw.polygon(arrow_points, fill=color, outline=color)

    def _draw_arrow_with_png(self, draw, start_pos, end_pos, label="", main_image=None):
        """Dibuja una flecha mejorada entre dos nodos - REEMPLAZA línea con PNG"""
        # Calcular puntos de borde de los nodos
        edge_start = self._get_node_edge_point(start_pos[0], start_pos[1], end_pos[0], end_pos[1])
        edge_end = self._get_node_edge_point(end_pos[0], end_pos[1], start_pos[0], start_pos[1])
        
        # Verificar si es etiqueta de decisión para no dibujar flecha
        is_decision_label = label and label.lower() in ['sí', 'si', 'no', 'yes', 'no']
        
        # INTENTAR PRIMERO CON PNG: Solo si NO es etiqueta de decisión
        if self.arrow_config['use_png_arrow'] and main_image is not None and not is_decision_label:
            if self._draw_real_png_arrow(main_image, edge_start, edge_end):
                # ¡ÉXITO! PNG dibujado, dibujar etiqueta si existe
                if label:
                    self._draw_arrow_label(draw, edge_start, edge_end, label)
                return  # ¡NO DIBUJAR LÍNEA!
        
        # Para etiquetas de decisión: solo línea, sin flecha
        if is_decision_label:
            line_width = 2
            draw.line([edge_start, edge_end], fill=self.colors['connection'], width=line_width)
            # Dibujar etiqueta
            if label:
                self._draw_arrow_label(draw, edge_start, edge_end, label)
            return
        
        # FALLBACK: Solo si PNG falló y NO es etiqueta de decisión, dibujar línea + flecha programática
        line_width = 2
        draw.line([edge_start, edge_end], fill=self.colors['connection'], width=line_width)
        self._draw_programmatic_arrow(draw, edge_start, edge_end)
        
        # Dibujar etiqueta si existe
        if label:
            self._draw_arrow_label(draw, edge_start, edge_end, label)

    def _draw_real_png_arrow(self, main_image, start_pos, end_pos):
        """REEMPLAZA la línea completamente con tu flecha PNG - DE PUNTA A PUNTA"""
        try:
            # Buscar la imagen de flecha en assets
            package_dir = Path(__file__).parent.parent
            arrow_path = package_dir / "assets" / "arrow.png"
            
            if not arrow_path.exists():
                print(f"❌ No se encontró arrow.png en: {arrow_path}")
                return False
                
            # Cargar la imagen de flecha
            arrow_img = Image.open(arrow_path).convert("RGBA")
            
            # Calcular dirección y longitud COMPLETA de la línea
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            length = math.sqrt(dx*dx + dy*dy)
            
            if length == 0:
                return False
            
            # Calcular ángulo - tu PNG apunta hacia la derecha
            angle_radians = math.atan2(dy, dx)
            angle_degrees = math.degrees(angle_radians)
            
            # FLECHA LARGA Y DELGADA - como una flecha real estilizada
            arrow_length = length * 0.85  # 85% de la longitud (casi completa)
            arrow_height = 30  # MÁS DELGADA: de 45 a 30 píxeles (bien flaca)
            
            # Redimensionar la flecha para que tenga estas dimensiones
            arrow_img = arrow_img.resize((int(arrow_length), int(arrow_height)), Image.LANCZOS)
            
            # Rotar la flecha según la dirección
            rotated_arrow = arrow_img.rotate(angle_degrees, expand=True)
            
            # Posicionar la flecha CENTRADA entre start_pos y end_pos
            center_x = (start_pos[0] + end_pos[0]) // 2
            center_y = (start_pos[1] + end_pos[1]) // 2
            
            arrow_w, arrow_h = rotated_arrow.size
            paste_x = int(center_x - arrow_w // 2)
            paste_y = int(center_y - arrow_h // 2)
            
            # Asegurar que esté dentro del canvas
            paste_x = max(0, min(paste_x, main_image.width - arrow_w))
            paste_y = max(0, min(paste_y, main_image.height - arrow_h))
            
            # PEGAR LA FLECHA PNG GRUESA
            main_image.paste(rotated_arrow, (paste_x, paste_y), rotated_arrow)
            
            return True
            
        except Exception as e:
            print(f"❌ Error con PNG: {e}")
            return False

    def _draw_png_arrow(self, draw, start_pos, end_pos):
        """Dibuja flecha usando tu imagen PNG de assets/arrow.png"""
        try:
            # Buscar la imagen de flecha en assets
            package_dir = Path(__file__).parent.parent
            arrow_path = package_dir / "assets" / "arrow.png"
            
            if not arrow_path.exists():
                print(f"No se encontró arrow.png en: {arrow_path}")
                return False
                
            # Cargar la imagen de flecha
            arrow_img = Image.open(arrow_path).convert("RGBA")
            
            # Calcular ángulo y longitud
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            length = math.sqrt(dx*dx + dy*dy)
            
            if length == 0:
                return False
                
            angle = math.degrees(math.atan2(dy, dx))
            
            # Dibujar línea de conexión
            line_width = self.arrow_config['line_width']
            draw.line([start_pos, end_pos], fill=self.colors['connection'], width=line_width)
            
            # Redimensionar la flecha si es necesario (tamaño razonable)
            arrow_size = 30  # Tamaño fijo de 30px para la flecha
            original_w, original_h = arrow_img.size
            
            # Mantener proporción al redimensionar
            if original_w > arrow_size:
                new_h = int(original_h * arrow_size / original_w)
                arrow_img = arrow_img.resize((arrow_size, new_h), Image.LANCZOS)
            
            # Rotar la imagen de flecha según el ángulo
            rotated_arrow = arrow_img.rotate(-angle, expand=True)
            
            # Calcular posición para centrar la flecha en el punto final
            arrow_w, arrow_h = rotated_arrow.size
            paste_x = int(end_pos[0] - arrow_w // 2)
            paste_y = int(end_pos[1] - arrow_h // 2)
            
            # Usar polígono para simular la flecha
            self._draw_curved_arrow_like_png(draw, end_pos, angle)
            
            print(f"✅ Usando arrow.png: {arrow_path}")
            return True
            
        except Exception as e:
            print(f"Error cargando arrow.png: {e}")
            return False

    def _draw_curved_arrow_like_png(self, draw, end_point, angle):
        """Dibuja una flecha curvada similar a tu PNG"""
        x2, y2 = end_point
        
        # Dimensiones basadas en tu imagen
        arrow_length = 25
        arrow_width = 15
        curve_radius = 8
        
        # Puntos de la flecha curvada (similar a tu PNG)
        base_points = [
            (0, 0),                              # Punta
            (-arrow_length, -arrow_width),       # Lado superior
            (-arrow_length + curve_radius, -curve_radius//2),  # Curva superior
            (-arrow_length + curve_radius, curve_radius//2),   # Curva inferior  
            (-arrow_length, arrow_width),        # Lado inferior
        ]
        
        # Rotar y trasladar los puntos
        rotated_points = []
        for px, py in base_points:
            # Rotar punto
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            
            # Trasladar al punto final
            final_x = x2 + rx
            final_y = y2 + ry
            rotated_points.append((final_x, final_y))
        
        # Dibujar la flecha con el estilo de tu PNG
        draw.polygon(rotated_points, fill=self.colors['connection'], outline=self.colors['connection'])

    def _draw_image_arrow(self, draw, start_pos, end_pos, arrow_image_path):
        """Dibuja una flecha usando una imagen PNG"""
        try:
            # Cargar la imagen de flecha
            arrow_img = Image.open(arrow_image_path).convert("RGBA")
            
            # Calcular ángulo y rotación necesaria
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            length = math.sqrt(dx*dx + dy*dy)
            
            if length == 0:
                return
                
            angle = math.degrees(math.atan2(dy, dx))
            
            # Dibujar línea de conexión
            line_width = self.style.arrow_config['line_width']
            draw.line([start_pos, end_pos], fill=self.colors['connection'], width=line_width)
            
            # Rotar la imagen de flecha
            rotated_arrow = arrow_img.rotate(-angle, expand=True)
            
            # Calcular posición para centrar la flecha en el punto final
            arrow_w, arrow_h = rotated_arrow.size
            paste_x = int(end_pos[0] - arrow_w // 2)
            paste_y = int(end_pos[1] - arrow_h // 2)
            
            # Pegar la flecha rotada en la imagen principal
            # Crear una imagen temporal para la composición
            temp_img = Image.new("RGBA", (arrow_w, arrow_h), (0, 0, 0, 0))
            temp_img.paste(rotated_arrow, (0, 0))
            
            # Convertir el canvas principal a RGBA temporalmente para soportar transparencia
            canvas_img = Image.new("RGBA", (paste_x + arrow_w, paste_y + arrow_h), (0, 0, 0, 0))
            canvas_img.paste(temp_img, (paste_x, paste_y), temp_img)
            
        except Exception as e:
            print(f"Error cargando imagen de flecha {arrow_image_path}: {e}")
            # Fallback a flecha programática
            self._draw_programmatic_arrow(draw, start_pos, end_pos)

    def _draw_programmatic_arrow(self, draw, start_pos, end_pos):
        """Dibuja una flecha mejorada usando formas geométricas"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Calcular ángulo para rotación
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
            
        angle = math.atan2(dy, dx)
        
        # Usar configuración mejorada
        line_width = self.arrow_config['line_width']
        arrow_length = self.arrow_config['arrow_length']
        arrow_width = self.arrow_config['arrow_width']
        
        # Dibujar línea recta más gruesa
        draw.line([start_pos, end_pos], fill=self.colors['connection'], width=line_width)
        
        # Dibujar la punta de flecha mejorada
        self._draw_arrowhead(draw, end_pos, angle)

    def _draw_arrowhead(self, draw, end_point, angle):
        """Dibuja una punta de flecha mejorada"""
        x2, y2 = end_point
        
        # Usar configuración
        arrow_length = self.arrow_config['arrow_length']
        arrow_width = self.arrow_config['arrow_width']
        curve_depth = self.arrow_config['curve_depth']
        
        # Puntos de la flecha más elegante
        base_points = [
            (0, 0),                              # Punta
            (-arrow_length, -arrow_width),       # Lado superior
            (-arrow_length + curve_depth, 0),    # Curvatura interna (hace la flecha más elegante)
            (-arrow_length, arrow_width),        # Lado inferior
        ]
        
        # Rotar y trasladar los puntos
        rotated_points = []
        for px, py in base_points:
            # Rotar punto
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            
            # Trasladar al punto final
            final_x = x2 + rx
            final_y = y2 + ry
            rotated_points.append((final_x, final_y))
        
        # Dibujar la punta de flecha sólida
        draw.polygon(rotated_points, fill=self.colors['connection'], outline=self.colors['connection'])

    def _draw_arrow_label(self, draw, start_pos, end_pos, label):
        """Dibuja la etiqueta de una flecha con círculos para decisiones"""
        # Para etiquetas de decisión, posicionar cerca del nodo de origen (diamante)
        # pero no tan cerca para evitar solapamiento con nodos destino
        if label.lower() in ['sí', 'si', 'no', 'yes', 'no']:
            # Calcular posición al 35% del camino para mejor visibilidad
            mid_x = start_pos[0] + int((end_pos[0] - start_pos[0]) * 0.35)
            mid_y = start_pos[1] + int((end_pos[1] - start_pos[1]) * 0.35)
            
            # Dibujar círculo pequeño para etiquetas de decisión
            circle_radius = 16  # Ligeramente más grande para mejor legibilidad
            
            # Círculo de fondo
            circle_bbox = [
                mid_x - circle_radius,
                mid_y - circle_radius,
                mid_x + circle_radius,
                mid_y + circle_radius
            ]
            draw.ellipse(circle_bbox, fill=self.colors['decision_label_fill'], 
                       outline=self.colors['decision_label_fill'])
            
            # Texto centrado en el círculo - cálculo más preciso del centrado
            bbox = draw.textbbox((0, 0), label, font=self.font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Centrado más preciso - ajuste tanto horizontal como vertical
            text_x = mid_x - text_width // 2
            text_y = mid_y - text_height // 2 - 2  # Mejor ajuste vertical
            
            draw.text((text_x, text_y), label, 
                     fill=self.colors['decision_label_text'], font=self.font)
        else:
            # Etiqueta normal con fondo rectangular - punto medio para otras etiquetas
            mid_x = (start_pos[0] + end_pos[0]) // 2
            mid_y = (start_pos[1] + end_pos[1]) // 2
            
            bbox = draw.textbbox((0, 0), label, font=self.font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            label_bg = [
                mid_x - text_width // 2 - 2,
                mid_y - text_height // 2 - 1,
                mid_x + text_width // 2 + 2,
                mid_y + text_height // 2 + 1
            ]
            draw.rectangle(label_bg, fill=self.colors['background'], 
                         outline=self.colors['background'])
            
            # Texto de la etiqueta
            draw.text((mid_x - text_width // 2, mid_y - text_height // 2), 
                     label, fill=self.colors['text'], font=self.font)

    def _draw_svg_style_arrow(self, draw, start_pos, end_pos, color=(80, 80, 80)):
        """Dibuja una flecha que mantiene la forma del SVG original, solo rotando"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Calcular ángulo para rotación
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
            
        angle = math.atan2(dy, dx)
        
        # Dibujar línea recta (como en el SVG original)
        draw.line([start_pos, end_pos], fill=color, width=3)
        
        # Dibujar la flecha con la forma exacta del SVG, pero rotada
        self._draw_svg_arrowhead(draw, end_pos, angle, color)

    def _draw_svg_arrowhead(self, draw, end_point, angle, color):
        """Dibuja la punta de flecha con la forma exacta del SVG original"""
        x2, y2 = end_point
        
        # Dimensiones de la flecha basadas en el SVG original
        # El SVG original apunta hacia la izquierda, así que ajustamos
        arrow_length = 18
        arrow_width = 12
        curve_depth = 8
        
        # Puntos base de la flecha (forma del SVG original apuntando derecha)
        base_points = [
            (0, 0),                              # Punta
            (-arrow_length, -arrow_width),       # Lado superior
            (-arrow_length + curve_depth, 0),    # Curvatura interna
            (-arrow_length, arrow_width),        # Lado inferior
        ]
        
        # Rotar y trasladar los puntos según el ángulo necesario
        rotated_points = []
        for px, py in base_points:
            # Rotar punto
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            
            # Trasladar al punto final
            final_x = x2 + rx
            final_y = y2 + ry
            rotated_points.append((final_x, final_y))
        
        # Dibujar la punta de flecha sólida
        draw.polygon(rotated_points, fill=color, outline=color)
    
    def render(self, filename: str = "flujograma.png", background_image: str = None) -> str:
        """
        Renderiza el flujograma con dimensiones y calidad automáticas optimizadas
        
        Args:
            filename: Nombre del archivo de salida
            background_image: Ruta a imagen de fondo (opcional)
        """
        # Calcular posiciones si no están calculadas
        if not any(hasattr(node, 'position') and node.position for node in self.diagram.nodes):
            self.diagram.calculate_layout()
        
        # Calcular dimensiones óptimas automáticamente
        self._calculate_optimal_dimensions()
        
        # Centrar el diagrama en el canvas
        self._center_diagram()
        
        # Crear imagen base con las dimensiones calculadas
        if background_image and os.path.exists(background_image):
            # Usar imagen de fondo
            try:
                bg_image = Image.open(background_image)
                # Redimensionar imagen de fondo al tamaño del canvas
                bg_image = bg_image.resize((self.width, self.height), Image.Resampling.LANCZOS)
                image = bg_image.convert('RGBA')
                
                # Crear overlay semitransparente para mejorar legibilidad
                overlay = Image.new('RGBA', (self.width, self.height), (236, 236, 236, 180))
                image = Image.alpha_composite(image, overlay)
                image = image.convert('RGB')
                
            except Exception as e:
                print(f"⚠️ Error cargando imagen de fondo: {e}")
                # Fallback a color sólido
                image = Image.new('RGB', (self.width, self.height), self.colors['background'])
        else:
            # Usar color de fondo sólido (#ececec)
            image = Image.new('RGB', (self.width, self.height), self.colors['background'])
        
        # Configurar draw con antialiasing mejorado
        draw = ImageDraw.Draw(image)
        
        # Añadir título si existe
        if self.diagram.title:
            self._draw_title(draw)
        
        # Dibujar conexiones primero con flechas personalizadas
        self._draw_connections_with_custom_arrows(draw, image)
        
        # Dibujar nodos con antialiasing
        self._draw_nodes(draw)
        
        # Agregar marca de agua
        self._draw_watermark(image)
        
        # Guardar imagen con máxima calidad
        image.save(filename, 'PNG', quality=100, optimize=False)
        return filename
    
    def _center_diagram(self):
        """Centra el diagrama en el canvas asegurando que no se corte"""
        if not self.diagram.nodes:
            return
        
        # Encontrar límites del diagrama incluyendo el tamaño de los nodos
        positions = [node.position for node in self.diagram.nodes if node.position]
        if not positions:
            return
        
        min_x = min(pos[0] for pos in positions) - self.node_width // 2
        max_x = max(pos[0] for pos in positions) + self.node_width // 2
        min_y = min(pos[1] for pos in positions) - self.node_height // 2
        max_y = max(pos[1] for pos in positions) + self.node_height // 2
        
        # Calcular dimensiones del diagrama
        diagram_width = max_x - min_x
        diagram_height = max_y - min_y
        
        # Calcular offset para centrar, considerando márgenes
        available_width = self.width - 2 * self.margin
        available_height = self.height - 2 * self.margin
        
        # Espacio para título más compacto (más cerca del diagrama)
        title_space = 40 if self.diagram.title else 0
        available_height -= title_space
        
        offset_x = (available_width - diagram_width) // 2 + self.margin - min_x
        offset_y = (available_height - diagram_height) // 2 + self.margin + title_space - min_y
        
        # Aplicar offset a todos los nodos
        for node in self.diagram.nodes:
            if node.position:
                x, y = node.position
                node.position = (x + offset_x, y + offset_y)
    
    def _draw_title(self, draw: ImageDraw.Draw):
        """Dibuja el título del diagrama con fuente grande y elegante"""
        # Calcular posición centrada con fuente grande
        bbox = draw.textbbox((0, 0), self.diagram.title, font=self.font_title)
        text_width = bbox[2] - bbox[0]
        text_x = (self.width - text_width) // 2
        text_y = 40  # Más margen desde arriba (era 10, ahora 40)
        
        # Dibujar título con fuente grande y elegante
        draw.text((text_x, text_y), self.diagram.title, 
                 fill=self.colors['text'], font=self.font_title)
    
    def _draw_nodes(self, draw: ImageDraw.Draw):
        """Dibuja todos los nodos del diagrama"""
        for node in self.diagram.nodes:
            if not node.position:
                continue
            
            x, y = node.position
            
            if node.type == NodeType.START or node.type == NodeType.END:
                self._draw_oval_node(draw, x, y, node.text, 
                                   self.colors['start_end_fill'],
                                   self.colors['start_end_border'])
            
            elif node.type == NodeType.DECISION:
                self._draw_diamond_node(draw, x, y, node.text,
                                      self.colors['decision_fill'],
                                      self.colors['decision_border'])
            
            elif node.type == NodeType.INPUT_OUTPUT:
                self._draw_parallelogram_node(draw, x, y, node.text,
                                            self.colors['input_output_fill'],
                                            self.colors['input_output_border'])
            
            else:  # PROCESS y otros
                self._draw_rectangle_node(draw, x, y, node.text,
                                        self.colors['node_fill'],
                                        self.colors['node_border'])
    
    def _draw_rectangle_node(self, draw: ImageDraw.Draw, x: int, y: int, 
                           text: str, fill_color: Tuple, border_color: Tuple):
        """Dibuja un nodo rectangular (proceso)"""
        left = x - self.node_width // 2
        top = y - self.node_height // 2
        right = x + self.node_width // 2
        bottom = y + self.node_height // 2
        
        # Dibujar rectángulo
        draw.rectangle([left, top, right, bottom], 
                      fill=fill_color, outline=border_color, width=2)
        
        # Dibujar texto centrado
        self._draw_centered_text(draw, x, y, text)
    
    def _draw_oval_node(self, draw: ImageDraw.Draw, x: int, y: int, 
                       text: str, fill_color: Tuple, border_color: Tuple):
        """Dibuja un nodo oval (inicio/fin)"""
        left = x - self.node_width // 2
        top = y - self.node_height // 2
        right = x + self.node_width // 2
        bottom = y + self.node_height // 2
        
        # Dibujar óvalo
        draw.ellipse([left, top, right, bottom],
                    fill=fill_color, outline=border_color, width=2)
        
        # Dibujar texto centrado
        self._draw_centered_text(draw, x, y, text)
    
    def _draw_diamond_node(self, draw: ImageDraw.Draw, x: int, y: int,
                          text: str, fill_color: Tuple, border_color: Tuple):
        """Dibuja un nodo de diamante (decisión) más pequeño y sin borde"""
        # Hacer el diamante más pequeño para que no tape otros elementos
        diamond_size = max(self.node_width, self.node_height) // 2 - 10
        
        # Puntos del diamante
        points = [
            (x, y - diamond_size),  # Arriba
            (x + diamond_size, y),  # Derecha
            (x, y + diamond_size),  # Abajo
            (x - diamond_size, y)   # Izquierda
        ]
        
        # Dibujar diamante sin borde
        draw.polygon(points, fill=fill_color, outline=fill_color, width=0)
        
        # Dibujar texto centrado con espacio específico para diamante
        self._draw_centered_text(draw, x, y, text, max_width=diamond_size * 1.2)
    
    def _draw_parallelogram_node(self, draw: ImageDraw.Draw, x: int, y: int,
                               text: str, fill_color: Tuple, border_color: Tuple):
        """Dibuja un nodo de paralelogramo (entrada/salida)"""
        offset = 20
        left = x - self.node_width // 2
        top = y - self.node_height // 2
        right = x + self.node_width // 2
        bottom = y + self.node_height // 2
        
        # Puntos del paralelogramo
        points = [
            (left + offset, top),
            (right, top),
            (right - offset, bottom),
            (left, bottom)
        ]
        
        # Dibujar paralelogramo
        draw.polygon(points, fill=fill_color, outline=border_color, width=2)
        
        # Dibujar texto centrado
        self._draw_centered_text(draw, x, y, text)
    
    def _draw_centered_text(self, draw: ImageDraw.Draw, x: int, y: int, text: str, max_width: int = None):
        """Dibuja texto centrado en las coordenadas dadas con mejor manejo de texto"""
        if max_width is None:
            max_width = self.node_width - 20
        
        # Dividir texto en líneas si es muy largo
        lines = self._wrap_text(text, max_width)
        
        # Calcular altura total del texto con espaciado mejorado
        line_height = self.font_size + 4  # Más espacio entre líneas
        total_height = len(lines) * line_height
        
        # Posición inicial
        start_y = y - total_height // 2
        
        for i, line in enumerate(lines):
            # Obtener dimensiones del texto
            bbox = draw.textbbox((0, 0), line, font=self.font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calcular posición centrada
            text_x = x - text_width // 2
            text_y = start_y + i * line_height
            
            # Dibujar texto con mejor contraste
            draw.text((text_x, text_y), line, fill=self.colors['text'], font=self.font)
    
    def _wrap_text(self, text: str, max_width: int) -> list:
        """Divide el texto en líneas que caben en el ancho especificado"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Estimar ancho de la línea actual + nueva palabra
            test_line = ' '.join(current_line + [word])
            
            # Usar el font real para calcular el ancho más precisamente
            try:
                bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=self.font)
                text_width = bbox[2] - bbox[0]
            except:
                # Fallback a estimación si hay error
                text_width = len(test_line) * 7
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Palabra muy larga, añadirla de todas formas
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _draw_connections_with_custom_arrows(self, draw: ImageDraw.Draw, main_image=None):
        """Dibuja todas las conexiones entre nodos con flechas personalizadas"""
        for node in self.diagram.nodes:
            if not node.position:
                continue
            
            for connection in node.connections:
                target = connection.target
                if not target.position:
                    continue
                
                self._draw_arrow_with_png(draw, node.position, target.position, connection.label, main_image)
    
    def _draw_connections(self, draw: ImageDraw.Draw):
        """Dibuja todas las conexiones entre nodos"""
        for node in self.diagram.nodes:
            if not node.position:
                continue
            
            for connection in node.connections:
                target = connection.target
                if not target.position:
                    continue
                
                self._draw_arrow(draw, node.position, target.position, connection.label)
    
    def _draw_arrow(self, draw: ImageDraw.Draw, start: Tuple[int, int], 
                   end: Tuple[int, int], label: str = ""):
        """Dibuja una flecha entre dos puntos"""
        x1, y1 = start
        x2, y2 = end
        
        # Calcular puntos de borde de los nodos
        edge_start = self._get_node_edge_point(x1, y1, x2, y2)
        edge_end = self._get_node_edge_point(x2, y2, x1, y1)
        
        # Verificar si es etiqueta de decisión
        is_decision_label = label and label.lower() in ['sí', 'si', 'no', 'yes', 'no']
        
        # Dibujar línea
        draw.line([edge_start, edge_end], fill=self.colors['connection'], width=2)
        
        # Dibujar punta de flecha solo si NO es etiqueta de decisión
        if not is_decision_label:
            self._draw_arrowhead(draw, edge_start, edge_end)
        
        # Dibujar etiqueta si existe
        if label:
            # Para etiquetas de decisión, posicionar al 35% del camino para mejor visibilidad
            if label.lower() in ['sí', 'si', 'no', 'yes', 'no']:
                # Posición al 35% del camino para evitar solapamiento
                mid_x = edge_start[0] + int((edge_end[0] - edge_start[0]) * 0.35)
                mid_y = edge_start[1] + int((edge_end[1] - edge_start[1]) * 0.35)
                
                # Dibujar círculo pequeño para etiquetas de decisión
                circle_radius = 16  # Ligeramente más grande
                
                # Círculo de fondo
                circle_bbox = [
                    mid_x - circle_radius,
                    mid_y - circle_radius,
                    mid_x + circle_radius,
                    mid_y + circle_radius
                ]
                draw.ellipse(circle_bbox, fill=self.colors['decision_label_fill'], 
                           outline=self.colors['decision_label_fill'])
                
                # Texto centrado en el círculo
                bbox = draw.textbbox((0, 0), label, font=self.font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                text_x = mid_x - text_width // 2
                text_y = mid_y - text_height // 2 - 2  # Mejor ajuste vertical
                
                draw.text((text_x, text_y), label, 
                         fill=self.colors['decision_label_text'], font=self.font)
            else:
                # Etiqueta normal en punto medio
                mid_x = (edge_start[0] + edge_end[0]) // 2
                mid_y = (edge_start[1] + edge_end[1]) // 2
                
                # Etiqueta normal con fondo rectangular
                bbox = draw.textbbox((0, 0), label, font=self.font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                label_bg = [
                    mid_x - text_width // 2 - 2,
                    mid_y - text_height // 2 - 1,
                    mid_x + text_width // 2 + 2,
                    mid_y + text_height // 2 + 1
                ]
                draw.rectangle(label_bg, fill=self.colors['background'], 
                             outline=self.colors['background'])
                
                # Texto de la etiqueta
                draw.text((mid_x - text_width // 2, mid_y - text_height // 2), 
                         label, fill=self.colors['text'], font=self.font)
    
    def _get_node_edge_point(self, x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
        """Calcula el punto en el borde del nodo para la conexión"""
        # Calcular ángulo
        angle = math.atan2(y2 - y1, x2 - x1)
        
        # Calcular offset desde el centro del nodo
        offset_x = int(self.node_width // 2 * math.cos(angle))
        offset_y = int(self.node_height // 2 * math.sin(angle))
        
        return (x1 + offset_x, y1 + offset_y)
    
    def _draw_arrowhead(self, draw: ImageDraw.Draw, start: Tuple[int, int], 
                       end: Tuple[int, int]):
        """Dibuja la punta de una flecha"""
        x1, y1 = start
        x2, y2 = end
        
        # Calcular ángulo y longitud de la punta
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_length = 10
        arrow_angle = math.pi / 6  # 30 grados
        
        # Puntos de la punta de flecha
        point1_x = x2 - arrow_length * math.cos(angle - arrow_angle)
        point1_y = y2 - arrow_length * math.sin(angle - arrow_angle)
        
        point2_x = x2 - arrow_length * math.cos(angle + arrow_angle)
        point2_y = y2 - arrow_length * math.sin(angle + arrow_angle)
        
        # Dibujar punta de flecha
        points = [(x2, y2), (point1_x, point1_y), (point2_x, point2_y)]
        draw.polygon(points, fill=self.colors['connection'])

    def _draw_watermark(self, image):
        """Dibuja la marca de agua en la esquina inferior derecha"""
        try:
            # Buscar la marca de agua en assets
            package_dir = Path(__file__).parent.parent
            watermark_path = package_dir / "assets" / "marca-agua.png"
            
            if not watermark_path.exists():
                print(f"⚠️ No se encontró marca-agua.png en: {watermark_path}")
                return
                
            # Cargar la marca de agua
            watermark = Image.open(watermark_path).convert("RGBA")
            
            # Redimensionar la marca de agua si es muy grande (máximo 100px de alto)
            max_height = 80
            if watermark.height > max_height:
                ratio = max_height / watermark.height
                new_width = int(watermark.width * ratio)
                watermark = watermark.resize((new_width, max_height), Image.Resampling.LANCZOS)
            
            # Calcular posición en esquina inferior derecha con margen
            margin = 20
            x = image.width - watermark.width - margin
            y = image.height - watermark.height - margin
            
            # Pegar la marca de agua con transparencia
            image.paste(watermark, (x, y), watermark)
            
        except Exception as e:
            print(f"⚠️ Error al agregar marca de agua: {e}")
