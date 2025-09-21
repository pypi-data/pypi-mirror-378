"""
Representación interna del diagrama de flujo
"""

from typing import List, Dict, Optional, Tuple
from .ast_nodes import FlowNode, StartNode, EndNode, Connection


class FlowDiagram:
    """Clase que representa un diagrama de flujo completo"""
    
    def __init__(self, title: str = "Diagrama de Flujo"):
        self.title = title
        self.nodes: List[FlowNode] = []
        self.connections: List[Connection] = []
        self.start_node: Optional[StartNode] = None
        self.end_nodes: List[EndNode] = []
        self._node_counter = 0
    
    def add_node(self, node: FlowNode) -> FlowNode:
        """Añade un nodo al diagrama"""
        self.nodes.append(node)
        
        # Registrar nodos especiales
        if isinstance(node, StartNode):
            self.start_node = node
        elif isinstance(node, EndNode):
            self.end_nodes.append(node)
        
        return node
    
    def create_node_id(self) -> str:
        """Genera un ID único para un nodo"""
        self._node_counter += 1
        return f"node_{self._node_counter}"
    
    def connect_nodes(self, source_id: str, target_id: str, label: str = "") -> Optional[Connection]:
        """Conecta dos nodos por sus IDs"""
        source = self.get_node_by_id(source_id)
        target = self.get_node_by_id(target_id)
        
        if source and target:
            connection = source.add_connection(target, label)
            self.connections.append(connection)
            return connection
        return None
    
    def get_node_by_id(self, node_id: str) -> Optional[FlowNode]:
        """Busca un nodo por su ID"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_all_connections(self) -> List[Connection]:
        """Obtiene todas las conexiones del diagrama"""
        all_connections = []
        for node in self.nodes:
            all_connections.extend(node.connections)
        return all_connections
    
    def validate(self) -> List[str]:
        """Valida la estructura del diagrama y retorna errores encontrados"""
        errors = []
        
        # Verificar que hay un nodo de inicio
        if not self.start_node:
            errors.append("El diagrama debe tener un nodo de inicio")
        
        # Verificar que hay al menos un nodo de fin
        if not self.end_nodes:
            errors.append("El diagrama debe tener al menos un nodo de fin")
        
        # Verificar que todos los nodos están conectados
        if len(self.nodes) > 1:
            connected_nodes = set()
            if self.start_node:
                self._find_connected_nodes(self.start_node, connected_nodes)
            
            unconnected = [node for node in self.nodes if node not in connected_nodes]
            if unconnected:
                errors.append(f"Nodos desconectados: {[node.id for node in unconnected]}")
        
        return errors
    
    def _find_connected_nodes(self, node: FlowNode, visited: set):
        """Algoritmo DFS para encontrar nodos conectados"""
        if node in visited:
            return
        
        visited.add(node)
        for connection in node.connections:
            self._find_connected_nodes(connection.target, visited)
    
    def calculate_layout(self) -> Dict[str, Tuple[int, int]]:
        """Calcula posiciones para los nodos usando un layout inteligente con ramificaciones"""
        positions = {}
        
        if not self.nodes:
            return positions
        
        # Configuración del layout más compacto
        x_center = 400   # Centro horizontal
        y_start = 80     # Posición inicial más cerca del título
        y_spacing = 120  # Espaciado vertical más compacto
        x_branch_spacing = 350  # Espaciado para ramificaciones
        
        if self.start_node:
            # Usar layout con ramificaciones inteligentes
            self._smart_layout(positions, x_center, y_start, y_spacing, x_branch_spacing)
        else:
            # Fallback simple
            for i, node in enumerate(self.nodes):
                positions[node.id] = (x_center, y_start + i * y_spacing)
        
        # Asignar posiciones calculadas a los nodos
        for node in self.nodes:
            if node.id in positions:
                node.position = positions[node.id]
        
        return positions

    def _smart_layout(self, positions: Dict[str, Tuple[int, int]], 
                     x_center: int, y_start: int, y_spacing: int, x_branch_spacing: int):
        """Layout inteligente que distribuye ramificaciones horizontalmente"""
        visited = set()
        level_counts = {}  # Contador de nodos por nivel
        
        def assign_position(node: FlowNode, x: int, y: int, level: int = 0):
            if node.id in visited:
                return
            
            visited.add(node.id)
            
            # Ajustar x basado en cuántos nodos hay en este nivel
            if level not in level_counts:
                level_counts[level] = 0
            
            # Para nodos de decisión, crear ramificaciones
            if len(node.connections) > 1:
                # Nodo de decisión en el centro
                positions[node.id] = (x, y)
                
                # Distribuir conexiones horizontalmente
                num_branches = len(node.connections)
                if num_branches == 2:
                    # Dos ramas: izquierda y derecha
                    left_x = x - x_branch_spacing // 2
                    right_x = x + x_branch_spacing // 2
                    
                    for i, connection in enumerate(node.connections):
                        branch_x = left_x if i == 0 else right_x
                        assign_position(connection.target, branch_x, y + y_spacing, level + 1)
                else:
                    # Múltiples ramas: distribuir uniformemente
                    total_width = (num_branches - 1) * (x_branch_spacing // 2)
                    start_x = x - total_width // 2
                    
                    for i, connection in enumerate(node.connections):
                        branch_x = start_x + i * (x_branch_spacing // 2)
                        assign_position(connection.target, branch_x, y + y_spacing, level + 1)
            
            elif len(node.connections) == 1:
                # Nodo secuencial
                positions[node.id] = (x, y)
                assign_position(node.connections[0].target, x, y + y_spacing, level + 1)
            
            else:
                # Nodo final
                positions[node.id] = (x, y)
        
        # Comenzar el layout desde el nodo inicial
        assign_position(self.start_node, x_center, y_start)
    
    def _calculate_layers(self) -> List[List[FlowNode]]:
        """Calcula las capas de nodos para el layout"""
        if not self.start_node:
            return []
        
        layers = []
        visited = set()
        current_layer = [self.start_node]
        
        while current_layer:
            layers.append(current_layer[:])
            next_layer = []
            
            for node in current_layer:
                visited.add(node)
                for connection in node.connections:
                    if connection.target not in visited and connection.target not in next_layer:
                        next_layer.append(connection.target)
            
            current_layer = next_layer
        
        return layers
    
    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas del diagrama"""
        from .ast_nodes import NodeType
        
        stats = {
            "total_nodes": len(self.nodes),
            "total_connections": len(self.get_all_connections()),
            "start_nodes": len([n for n in self.nodes if n.type == NodeType.START]),
            "end_nodes": len([n for n in self.nodes if n.type == NodeType.END]),
            "process_nodes": len([n for n in self.nodes if n.type == NodeType.PROCESS]),
            "decision_nodes": len([n for n in self.nodes if n.type == NodeType.DECISION]),
        }
        
        return stats
    
    def __str__(self):
        return f"FlowDiagram('{self.title}', {len(self.nodes)} nodes, {len(self.get_all_connections())} connections)"
    
    def __repr__(self):
        return self.__str__()
