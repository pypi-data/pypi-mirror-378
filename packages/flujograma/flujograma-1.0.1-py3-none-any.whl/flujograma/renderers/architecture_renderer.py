"""
Renderer específico para diagramas de arquitectura horizontales
Mantiene el estilo visual pero con nodos cuadrados y flechas arrow.png
"""

import os
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any, Tuple, Optional
from ..core.nodes import BaseNode
from ..core.edges import Edge


class ArchitectureRenderer:
    """
    Renderer especializado para diagramas de arquitectura horizontales
    Estilo: Título arriba, nodos cuadrados, flechas arrow.png horizontales
    """
    
    def __init__(self):
        # Configuración para diseño como en la imagen: icono arriba, texto abajo
        self.canvas_width = 1200
        self.canvas_height = 800
        self.title_height = 100
        
        # Nodos más grandes como en la imagen de referencia
        self.icon_size = 120  # Tamaño del cuadrado/icono (aumentado a 120px)
        self.text_height = 35  # Altura para el texto debajo
        self.node_total_height = self.icon_size + self.text_height + 25  # Total con espaciado
        self.node_spacing = 180  # Espaciado horizontal entre nodos (aumentado)
        self.row_spacing = 180   # Espaciado vertical entre filas (aumentado)
        self.margin = 100
        
        # Colores del estilo como en tu imagen
        self.background_color = "#f2e7d0"  # Fondo beige como en diagramas de flujo originales
        self.node_colors = {
            'ELB': "#9b59b6",     # Púrpura para Load Balancer
            'EC2': "#e67e22",     # Naranja para servidores
            'RDS': "#3498db",     # Azul para base de datos
            'S3': "#27ae60",      # Verde para almacenamiento
            'default': "#95a5a6"  # Gris por defecto
        }
        self.text_color = "#333333"  # Texto oscuro debajo
        self.title_color = "#333333"
        
        # Paths
        self.assets_path = os.path.join(os.path.dirname(__file__), "..", "assets")
        self.arrow_path = os.path.join(self.assets_path, "arrow.png")
        self.watermark_path = os.path.join(self.assets_path, "marca-agua.png")
        
    def render_architecture_diagram(self, 
                                   title: str,
                                   nodes: List[BaseNode],
                                   connections: List[Tuple[BaseNode, BaseNode]],
                                   sequences: List[List[BaseNode]] = None,
                                   filename: str = "architecture.png") -> str:
        """
        Renderiza un diagrama de arquitectura horizontal
        
        Args:
            title: Título del diagrama
            nodes: Lista de nodos a renderizar
            connections: Lista de tuplas (origen, destino)
            sequences: Lista de secuencias (filas) opcional
            filename: Nombre del archivo de salida
            
        Returns:
            Ruta del archivo generado
        """
        
        # Usar las secuencias si están disponibles, sino organizar automáticamente
        if sequences and len(sequences) > 0:
            # IMPORTANTE: Crear copias de nodos para cada fila para evitar problemas de cache
            rows = self._create_unique_nodes_per_row(sequences)
        else:
            # Fallback: organizar automáticamente
            rows = self._organize_nodes_in_rows(nodes, connections)
        
        # Calcular dimensiones del canvas
        canvas_width, canvas_height = self._calculate_canvas_size(rows)
        self.canvas_width = canvas_width  # Actualizar para usar en otros métodos
        self.canvas_height = canvas_height
        
        # Crear imagen
        img = Image.new('RGB', (canvas_width, canvas_height), self.background_color)
        draw = ImageDraw.Draw(img)
        
        # Dibujar título
        self._draw_title(draw, title, canvas_width)
        
        # Dibujar nodos
        node_positions = self._draw_nodes(draw, rows)
        
        # Dibujar conexiones por fila (sistema que funcionaba)
        self._draw_connections_by_rows(draw, rows, node_positions)
        
        # Dibujar marca de agua
        self._draw_watermark(img)
        
        # Guardar imagen
        output_path = os.path.abspath(filename)
        img.save(output_path, 'PNG', quality=95, optimize=True)
        
        return output_path
        
    def _organize_nodes_in_rows(self, nodes: List[BaseNode], connections: List[Tuple[BaseNode, BaseNode]]) -> List[List[BaseNode]]:
        """
        Organiza nodos en un layout inteligente para mostrar las conexiones correctamente
        Similar a diagrams.mingrammer.com
        """
        
        if not nodes:
            return []
        
        # Para diagrams.mingrammer.com style, organizamos en una estructura que muestre el flujo
        # Detectar nodos de entrada (que no son target de ninguna conexión)
        targets = {target for _, target in connections}
        sources = {source for source, _ in connections}
        
        # Nodos de entrada: aparecen como source pero no como target
        entry_nodes = [node for node in sources if node not in targets]
        
        # Si no hay nodos de entrada claros, usar el primero
        if not entry_nodes:
            entry_nodes = [nodes[0]] if nodes else []
        
        # Crear una organización simple pero efectiva
        # Fila 1: Nodos principales en secuencia de conexión
        main_sequence = []
        
        # Comenzar con nodos de entrada
        processed = set()
        for entry_node in entry_nodes:
            if entry_node not in processed:
                sequence = self._build_sequence_from_node(entry_node, connections, processed)
                main_sequence.extend(sequence)
        
        # Agregar nodos restantes
        for node in nodes:
            if node not in processed:
                main_sequence.append(node)
                processed.add(node)
        
        return [main_sequence] if main_sequence else []
    
    def _build_sequence_from_node(self, start_node: BaseNode, connections: List[Tuple[BaseNode, BaseNode]], processed: set) -> List[BaseNode]:
        """
        Construye una secuencia siguiendo las conexiones desde un nodo
        """
        sequence = []
        current = start_node
        
        while current and current not in processed:
            sequence.append(current)
            processed.add(current)
            
            # Buscar el siguiente nodo en la secuencia
            next_node = None
            for source, target in connections:
                if source == current and target not in processed:
                    next_node = target
                    break
            
            current = next_node
        
        return sequence
        
    def _calculate_canvas_size(self, rows: List[List[BaseNode]]) -> Tuple[int, int]:
        """Calcula el tamaño del canvas basado en las filas (actualizado para nuevo diseño)"""
        if not rows:
            return 800, 600
            
        max_nodes_in_row = max(len(row) for row in rows) if rows else 1
        
        # Ancho: máximo nodos en fila + espaciado + márgenes (usar icon_size)
        width = (max_nodes_in_row * self.icon_size + 
                (max_nodes_in_row - 1) * self.node_spacing + 
                2 * self.margin)
        
        # Alto: todas las filas + espaciado + título + márgenes (usar node_total_height)
        height = (len(rows) * self.node_total_height + 
                 (len(rows) - 1) * self.row_spacing + 
                 self.title_height + 
                 2 * self.margin)
        
        # Tamaño más ajustado al contenido real
        return max(width, 600), max(height, 400)
        
    def _create_unique_nodes_per_row(self, sequences: List[List[BaseNode]]) -> List[List[BaseNode]]:
        """
        Crea copias únicas de nodos para cada fila para evitar problemas de posicionamiento
        """
        class UniqueArchitectureNode(BaseNode):
            """Nodo temporal para renderizado único por fila"""
            def __init__(self, label: str, node_type: str = "default"):
                super().__init__(label)
                self.node_type = node_type
                
            def get_shape_type(self) -> str:
                return "rectangle"
        
        unique_rows = []
        
        for row_idx, row in enumerate(sequences):
            unique_row = []
            for node in row:
                # Obtener el tipo del nodo original
                original_type = self._get_node_type(node)
                
                # Crear una copia del nodo con un identificador único
                unique_node = UniqueArchitectureNode(node.label, original_type)
                # Identificador único para debug
                unique_node._row_id = row_idx
                unique_node._original_node = node
                unique_row.append(unique_node)
            unique_rows.append(unique_row)
            
        return unique_rows
        
    def _draw_title(self, draw: ImageDraw.Draw, title: str, canvas_width: int):
        """Dibuja el título en la parte superior"""
        try:
            # Intentar cargar fuente personalizada
            font_path = os.path.join(self.assets_path, "fonts", "ProductSans-Bold.ttf")
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 32)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
            
        # Calcular posición centrada
        bbox = draw.textbbox((0, 0), title, font=font)
        title_width = bbox[2] - bbox[0]
        title_x = (canvas_width - title_width) // 2
        title_y = 30
        
        # Dibujar título
        draw.text((title_x, title_y), title, fill=self.title_color, font=font)
        
    def _draw_nodes(self, draw: ImageDraw.Draw, rows: List[List[BaseNode]]) -> Dict[BaseNode, Tuple[int, int]]:
        """
        Dibuja los nodos en múltiples filas: cuadrado arriba, texto abajo
        Retorna diccionario con posiciones de cada nodo (centro del icono)
        """
        node_positions = {}
        
        if not rows:
            return node_positions
        
        # Calcular altura total disponible para todas las filas
        total_content_height = len(rows) * self.node_total_height + (len(rows) - 1) * self.row_spacing
        start_y = self.title_height + (self.canvas_height - self.title_height - total_content_height) // 2
        
        for row_idx, row in enumerate(rows):
            if not row:
                continue
                
            # Calcular Y para esta fila
            row_y = start_y + row_idx * (self.node_total_height + self.row_spacing)
            
            # Calcular espaciado para centrar la fila horizontalmente
            total_row_width = len(row) * self.icon_size + (len(row) - 1) * self.node_spacing
            start_x = (self.canvas_width - total_row_width) // 2
            
            for node_idx, node in enumerate(row):
                icon_x = start_x + node_idx * (self.icon_size + self.node_spacing)
                icon_y = row_y
                
                # Determinar color del nodo
                node_type = self._get_node_type(node)
                color = self.node_colors.get(node_type, self.node_colors['default'])
                
                # 1. Dibujar el cuadrado/icono arriba
                self._draw_node_icon(draw, icon_x, icon_y, color, node_type)
                
                # 2. Dibujar el texto debajo del icono
                text_y = icon_y + self.icon_size + 8  # 8px de separación
                self._draw_node_label(draw, node.label, icon_x, text_y)
                
                # Guardar posición (centro del icono para las conexiones)
                center_x = icon_x + self.icon_size // 2
                center_y = icon_y + self.icon_size // 2
                node_positions[node] = (center_x, center_y)
                
        return node_positions
        
    def _draw_node_icon(self, draw: ImageDraw.Draw, x: int, y: int, color: str, node_type: str):
        """
        Dibuja el icono/cuadrado del nodo (como en la imagen de referencia)
        """
        # Dibujar cuadrado con esquinas redondeadas
        self._draw_rounded_rectangle(
            draw, 
            [x, y, x + self.icon_size, y + self.icon_size],
            radius=12,  # Esquinas más redondeadas como en la imagen
            fill=color
        )
        
        # Intentar cargar y dibujar icono PNG
        if self._try_draw_png_icon(draw, x, y, node_type):
            return
        
        # Si no hay PNG, usar icono simple como fallback
        self._draw_simple_icon(draw, x, y, node_type)
    
    def _try_draw_png_icon(self, draw: ImageDraw.Draw, x: int, y: int, node_type: str) -> bool:
        """
        Intenta cargar y dibujar un icono PNG. Retorna True si tuvo éxito.
        """
        from PIL import Image
        
        # Determinar path del icono según el tipo de nodo
        icon_paths = {
            'EC2': 'aws/compute/ec2.png',
            'RDS': 'aws/database/rds.png',
            'S3': 'aws/storage/s3.png', 
            'ELB': 'aws/network/elb.png'
        }
        
        if node_type not in icon_paths:
            return False
            
        icon_path = os.path.join(self.assets_path, "icons", icon_paths[node_type])
        
        if not os.path.exists(icon_path):
            return False
        
        try:
            # Cargar imagen PNG
            icon_img = Image.open(icon_path).convert("RGBA")
            
            # Redimensionar al tamaño del icono con margen
            icon_size = self.icon_size - 20  # 10px de margen por cada lado
            icon_img = icon_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            
            # Calcular posición centrada
            paste_x = x + 10  # 10px de margen
            paste_y = y + 10  # 10px de margen
            
            # Obtener la imagen principal del canvas
            canvas_img = draw._image
            canvas_img.paste(icon_img, (paste_x, paste_y), icon_img)
            
            return True
            
        except Exception as e:
            return False
    
    def _draw_simple_icon(self, draw: ImageDraw.Draw, x: int, y: int, node_type: str):
        """
        Dibuja un icono simple dentro del cuadrado como placeholder
        Más tarde se reemplazará con iconos PNG reales
        """
        center_x = x + self.icon_size // 2
        center_y = y + self.icon_size // 2
        icon_size = 20
        
        if node_type == 'ELB':
            # Icono de load balancer (tres líneas horizontales)
            for i in range(3):
                line_y = center_y - icon_size//2 + i * 8
                draw.line([center_x - icon_size//2, line_y, center_x + icon_size//2, line_y], 
                         fill='white', width=3)
        elif node_type == 'EC2':
            # Icono de servidor (rectángulo con líneas)
            draw.rectangle([center_x - icon_size//2, center_y - icon_size//2, 
                           center_x + icon_size//2, center_y + icon_size//2], 
                          outline='white', width=3)
            draw.line([center_x - icon_size//3, center_y, center_x + icon_size//3, center_y], 
                     fill='white', width=2)
        elif node_type == 'RDS':
            # Icono de base de datos (cilindro)
            draw.ellipse([center_x - icon_size//2, center_y - icon_size//2, 
                         center_x + icon_size//2, center_y - icon_size//4], 
                        outline='white', width=3)
            draw.ellipse([center_x - icon_size//2, center_y + icon_size//4, 
                         center_x + icon_size//2, center_y + icon_size//2], 
                        outline='white', width=3)
        elif node_type == 'S3':
            # Icono de almacenamiento (cubo)
            points = [
                (center_x - icon_size//2, center_y + icon_size//2),
                (center_x - icon_size//3, center_y - icon_size//2),
                (center_x + icon_size//3, center_y - icon_size//2),
                (center_x + icon_size//2, center_y + icon_size//2)
            ]
            draw.polygon(points, outline='white', width=3)
    
    def _draw_node_label(self, draw: ImageDraw.Draw, label: str, x: int, y: int):
        """
        Dibuja el texto debajo del icono
        """
        try:
            font_path = os.path.join(self.assets_path, "fonts", "ProductSans-Regular.ttf")
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 16)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
            
        # Calcular posición centrada horizontalmente
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        
        text_x = x + (self.icon_size - text_width) // 2
        
        draw.text((text_x, y), label, fill=self.text_color, font=font)
    
    def _get_node_type(self, node: BaseNode) -> str:
        """Determina el tipo de nodo basado en su clase o atributo node_type"""
        
        # Si tiene el atributo node_type (nodos únicos), usarlo
        if hasattr(node, 'node_type'):
            return node.node_type
            
        # Fallback: usar el nombre de la clase
        class_name = node.__class__.__name__
        
        if 'ELB' in class_name:
            return 'ELB'
        elif 'EC2' in class_name:
            return 'EC2'
        elif 'RDS' in class_name:
            return 'RDS'
        elif 'S3' in class_name:
            return 'S3'
        else:
            return 'default'
            
    def _draw_rounded_rectangle(self, draw: ImageDraw.Draw, coords: List[int], radius: int, fill: str):
        """Dibuja un rectángulo con esquinas redondeadas"""
        x1, y1, x2, y2 = coords
        
        # Dibujar rectángulo principal
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        
        # Dibujar esquinas redondeadas
        draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill)
        draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill)
        
    def _draw_node_text(self, draw: ImageDraw.Draw, text: str, x: int, y: int):
        """Dibuja el texto del nodo centrado"""
        try:
            font_path = os.path.join(self.assets_path, "fonts", "ProductSans-Regular.ttf")
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 14)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
            
        # Calcular posición centrada
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = x + (self.node_size - text_width) // 2
        text_y = y + (self.node_size - text_height) // 2
        
        draw.text((text_x, text_y), text, fill=self.text_color, font=font)
        
    def _draw_connections(self, draw: ImageDraw.Draw, connections: List[Tuple[BaseNode, BaseNode]], 
                         node_positions: Dict[BaseNode, Tuple[int, int]]):
        """Dibuja conexiones horizontales dentro de cada fila"""
        
        # Organizar conexiones por filas
        for source, target in connections:
            if source not in node_positions or target not in node_positions:
                continue
                
            source_pos = node_positions[source]
            target_pos = node_positions[target]
            
            # Solo dibujar conexiones si están en la misma fila (misma Y aproximada)
            if abs(source_pos[1] - target_pos[1]) < 50:  # Misma fila (tolerancia de 50px)
                
                # Determinar dirección de la conexión
                if source_pos[0] < target_pos[0]:
                    # Conexión hacia la derecha
                    start_x = source_pos[0] + self.icon_size//2
                    end_x = target_pos[0] - self.icon_size//2
                    start_y = end_y = source_pos[1]
                    arrow_direction = "right"
                else:
                    # Conexión hacia la izquierda
                    start_x = source_pos[0] - self.icon_size//2
                    end_x = target_pos[0] + self.icon_size//2
                    start_y = end_y = source_pos[1]
                    arrow_direction = "left"
                
                # Dibujar línea horizontal
                draw.line([(start_x, start_y), (end_x, end_y)], fill="#333333", width=2)
                
                # Dibujar flecha en el destino
                self._draw_directional_arrow(draw, end_x, end_y, arrow_direction)
    
    def _draw_connections_by_rows(self, draw: ImageDraw.Draw, rows: List[List[BaseNode]], 
                                 node_positions: Dict[BaseNode, Tuple[int, int]]):
        """Dibuja conexiones secuenciales dentro de cada fila con direcciones inteligentes"""
        
        for row_idx, row in enumerate(rows):
            if len(row) < 2:
                continue
                
            # Dibujar conexiones secuenciales en esta fila
            for i in range(len(row) - 1):
                source = row[i]
                target = row[i + 1]
                
                if source not in node_positions or target not in node_positions:
                    continue
                    
                source_pos = node_positions[source]
                target_pos = node_positions[target]
                
                # Determinar dirección basándose en posiciones X
                if source_pos[0] < target_pos[0]:
                    # Conexión hacia la derecha (normal)
                    start_x = source_pos[0] + self.icon_size//2
                    end_x = target_pos[0] - self.icon_size//2
                    start_y = end_y = source_pos[1]
                    arrow_direction = "right"
                else:
                    # Conexión hacia la izquierda (para operador <<)
                    start_x = source_pos[0] - self.icon_size//2
                    end_x = target_pos[0] + self.icon_size//2
                    start_y = end_y = source_pos[1]
                    arrow_direction = "left"
                
                # Dibujar línea horizontal
                draw.line([(start_x, start_y), (end_x, end_y)], fill="#333333", width=2)
                
                # Dibujar flecha en la dirección correcta
                self._draw_directional_arrow(draw, end_x if arrow_direction == "right" else start_x, 
                                           end_y, arrow_direction)
    
    def _draw_connections_with_directions(self, draw: ImageDraw.Draw, 
                                        connections: List[tuple], 
                                        node_positions: Dict[BaseNode, Tuple[int, int]]):
        """Dibuja conexiones usando las direcciones originales de los operadores"""
        
        for connection in connections:
            # Verificar si la conexión tiene 3 elementos (source, target, direction)
            if len(connection) == 3:
                source, target, direction = connection
            else:
                # Compatibilidad con conexiones antiguas sin dirección
                source, target = connection
                direction = "right"
            
            # Verificar que tenemos nodos únicos (no los originales del cache)
            source_pos = None
            target_pos = None
            
            # Buscar nodos por etiqueta en las posiciones (porque son nodos únicos)
            for node, pos in node_positions.items():
                if node.label == source.label and source_pos is None:
                    source_pos = pos
                elif node.label == target.label and target_pos is None:
                    target_pos = pos
                    
            if source_pos is None or target_pos is None:
                continue
                
            # Calcular posiciones de conexión
            if direction == "right":
                # Flecha hacia la derecha: source → target
                start_x = source_pos[0] + self.icon_size//2
                end_x = target_pos[0] - self.icon_size//2
                start_y = end_y = source_pos[1]
                arrow_direction = "right"
            else:  # direction == "left"
                # Flecha hacia la izquierda
                start_x = source_pos[0] - self.icon_size//2
                end_x = target_pos[0] + self.icon_size//2
                start_y = end_y = source_pos[1]
                arrow_direction = "left"
            
            # Dibujar línea horizontal
            draw.line([(start_x, start_y), (end_x, end_y)], fill="#333333", width=3)
            
            # Dibujar flecha en la dirección correcta
            if direction == "right":
                self._draw_directional_arrow(draw, end_x, end_y, "right")
            else:
                self._draw_directional_arrow(draw, start_x, start_y, "left")
    
    def _draw_directional_arrow(self, draw: ImageDraw.Draw, x: int, y: int, direction: str):
        """Dibuja una flecha direccional (derecha o izquierda)"""
        size = 10
        
        if direction == "right":
            # Flecha apuntando a la derecha (>>)
            points = [
                (x, y),
                (x - size, y - size//2),
                (x - size, y + size//2)
            ]
        else:  # direction == "left"
            # Flecha apuntando a la izquierda (<<)
            points = [
                (x, y),
                (x + size, y - size//2),
                (x + size, y + size//2)
            ]
        
        draw.polygon(points, fill="#333333")
            
    def _draw_arrow(self, draw: ImageDraw.Draw, start_x: int, start_y: int, end_x: int, end_y: int):
        """Dibuja la flecha en la conexión"""
        # Usar flecha simple
        self._draw_simple_arrow(draw, end_x, end_y)
            
    def _draw_simple_arrow(self, draw: ImageDraw.Draw, x: int, y: int):
        """Dibuja una flecha simple como fallback"""
        size = 8
        points = [
            (x, y),
            (x - size, y - size//2),
            (x - size, y + size//2)
        ]
        draw.polygon(points, fill="#666666")
        
    def _draw_watermark(self, img: Image.Image):
        """Dibuja la marca de agua en la esquina inferior derecha"""
        
        if not os.path.exists(self.watermark_path):
            return
            
        try:
            watermark = Image.open(self.watermark_path)
            
            # Mantener proporciones originales del logo
            original_width, original_height = watermark.size
            max_size = 45  # Tamaño máximo
            
            # Calcular nuevo tamaño manteniendo proporciones
            if original_width > original_height:
                new_width = max_size
                new_height = int((original_height * max_size) / original_width)
            else:
                new_height = max_size
                new_width = int((original_width * max_size) / original_height)
            
            watermark = watermark.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Posición en esquina inferior derecha
            margin = 15
            x = img.width - new_width - margin
            y = img.height - new_height - margin
            
            # Pegar marca de agua simple y efectiva
            if watermark.mode == 'RGBA':
                img.paste(watermark, (x, y), watermark)
            else:
                watermark_rgba = watermark.convert('RGBA')
                img.paste(watermark_rgba, (x, y), watermark_rgba)
            
        except Exception as e:
            # Fallback simple
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.text((img.width - 120, img.height - 30), "DiagramsOffline", fill=(150, 150, 150))


# Función de conveniencia para usar el renderer
def render_architecture_diagram(title: str, 
                               nodes: List[BaseNode], 
                               connections: List[Tuple[BaseNode, BaseNode]],
                               sequences: List[List[BaseNode]] = None,
                               filename: str = "architecture.png") -> str:
    """
    Función de conveniencia para renderizar diagramas de arquitectura
    
    Args:
        title: Título del diagrama
        nodes: Lista de nodos
        connections: Lista de conexiones (tuplas de nodos)
        sequences: Lista de secuencias (filas) opcional
        filename: Nombre del archivo de salida
        
    Returns:
        Ruta del archivo generado
    """
    renderer = ArchitectureRenderer()
    return renderer.render_architecture_diagram(title, nodes, connections, sequences, filename)
    return renderer.render_architecture_diagram(title, nodes, connections, filename)