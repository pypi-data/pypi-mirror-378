"""
Algoritmos de posicionamiento automático (layouts) sin Graphviz
Implementación pura en Python para máximo rendimiento offline
"""

import math
from typing import List, Tuple, Dict, Any, Optional
from enum import Enum
from .nodes import BaseNode
from .clusters import Cluster


class LayoutDirection(Enum):
    """Direcciones de layout disponibles"""
    TOP_BOTTOM = "TB"
    BOTTOM_TOP = "BT"  
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"


class LayoutAlgorithm(Enum):
    """Algoritmos de layout disponibles"""
    HIERARCHICAL = "hierarchical"    # Jerárquico (árbol)
    FORCE_DIRECTED = "force"         # Dirigido por fuerzas
    GRID = "grid"                    # Grilla regular
    CIRCULAR = "circular"            # Circular
    LAYERED = "layered"              # Por capas


class LayoutEngine:
    """
    Motor de posicionamiento automático de nodos
    Alternativa liviana a Graphviz usando algoritmos propios
    """
    
    def __init__(self, 
                 algorithm: LayoutAlgorithm = LayoutAlgorithm.HIERARCHICAL,
                 direction: LayoutDirection = LayoutDirection.TOP_BOTTOM,
                 node_spacing: int = 150,
                 layer_spacing: int = 200):
        """
        Inicializa el motor de layout
        
        Args:
            algorithm: Algoritmo de posicionamiento
            direction: Dirección del flujo
            node_spacing: Espaciado entre nodos
            layer_spacing: Espaciado entre capas/niveles
        """
        self.algorithm = algorithm
        self.direction = direction
        self.node_spacing = node_spacing
        self.layer_spacing = layer_spacing
        
    def layout_nodes(self, nodes: List[BaseNode], edges: List = None) -> Dict[str, Tuple[int, int]]:
        """
        Calcula posiciones para todos los nodos
        
        Args:
            nodes: Lista de nodos a posicionar
            edges: Lista de conexiones entre nodos
            
        Returns:
            Dict[node_id, (x, y)]: Diccionario con posiciones calculadas
        """
        if not nodes:
            return {}
            
        edges = edges or []
        
        # Seleccionar algoritmo
        if self.algorithm == LayoutAlgorithm.HIERARCHICAL:
            return self._hierarchical_layout(nodes, edges)
        elif self.algorithm == LayoutAlgorithm.FORCE_DIRECTED:
            return self._force_directed_layout(nodes, edges)
        elif self.algorithm == LayoutAlgorithm.GRID:
            return self._grid_layout(nodes)
        elif self.algorithm == LayoutAlgorithm.CIRCULAR:
            return self._circular_layout(nodes)
        elif self.algorithm == LayoutAlgorithm.LAYERED:
            return self._layered_layout(nodes, edges)
        else:
            return self._hierarchical_layout(nodes, edges)
            
    def _hierarchical_layout(self, nodes: List[BaseNode], edges: List) -> Dict[str, Tuple[int, int]]:
        """
        Layout jerárquico (tipo árbol)
        Identifica nodos raíz y organiza por niveles
        """
        # Construir grafo de dependencias
        graph = self._build_graph(nodes, edges)
        
        # Encontrar nodos raíz (sin dependencias entrantes)
        root_nodes = [node for node in nodes if not self._has_incoming_edges(node, edges)]
        if not root_nodes:
            root_nodes = [nodes[0]]  # Fallback al primer nodo
            
        # Asignar niveles usando BFS
        levels = self._assign_levels_bfs(root_nodes, graph)
        
        # Calcular posiciones por nivel
        positions = {}
        for level, level_nodes in enumerate(levels):
            level_width = len(level_nodes) * self.node_spacing
            start_x = -level_width // 2
            
            for i, node in enumerate(level_nodes):
                if self.direction in [LayoutDirection.TOP_BOTTOM, LayoutDirection.BOTTOM_TOP]:
                    x = start_x + i * self.node_spacing
                    y = level * self.layer_spacing
                    if self.direction == LayoutDirection.BOTTOM_TOP:
                        y = -y
                else:  # LEFT_RIGHT or RIGHT_LEFT
                    x = level * self.layer_spacing
                    y = start_x + i * self.node_spacing
                    if self.direction == LayoutDirection.RIGHT_LEFT:
                        x = -x
                        
                positions[node.node_id] = (x, y)
                
        return positions
        
    def _force_directed_layout(self, nodes: List[BaseNode], edges: List) -> Dict[str, Tuple[int, int]]:
        """
        Layout dirigido por fuerzas (simulación física)
        Algoritmo tipo Spring-Force
        """
        positions = {}
        
        # Inicializar posiciones aleatorias
        import random
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / len(nodes)
            radius = 100
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            positions[node.node_id] = [x, y]
            
        # Constantes de simulación
        iterations = 100
        attraction_strength = 0.01
        repulsion_strength = 1000
        damping = 0.9
        
        for iteration in range(iterations):
            forces = {node.node_id: [0.0, 0.0] for node in nodes}
            
            # Fuerza de repulsión entre todos los nodos
            for i, node1 in enumerate(nodes):
                for j, node2 in enumerate(nodes[i+1:], i+1):
                    pos1 = positions[node1.node_id]
                    pos2 = positions[node2.node_id]
                    
                    dx = pos1[0] - pos2[0]
                    dy = pos1[1] - pos2[1]
                    distance = math.sqrt(dx*dx + dy*dy) + 0.01  # Evitar división por 0
                    
                    force = repulsion_strength / (distance * distance)
                    fx = force * dx / distance
                    fy = force * dy / distance
                    
                    forces[node1.node_id][0] += fx
                    forces[node1.node_id][1] += fy
                    forces[node2.node_id][0] -= fx
                    forces[node2.node_id][1] -= fy
                    
            # Fuerza de atracción entre nodos conectados
            for edge in edges:
                if hasattr(edge, 'source_node') and hasattr(edge, 'target_node'):
                    source_id = edge.source_node.node_id
                    target_id = edge.target_node.node_id
                    
                    pos1 = positions[source_id]
                    pos2 = positions[target_id]
                    
                    dx = pos2[0] - pos1[0]
                    dy = pos2[1] - pos1[1]
                    distance = math.sqrt(dx*dx + dy*dy) + 0.01
                    
                    force = attraction_strength * distance
                    fx = force * dx / distance
                    fy = force * dy / distance
                    
                    forces[source_id][0] += fx
                    forces[source_id][1] += fy
                    forces[target_id][0] -= fx
                    forces[target_id][1] -= fy
                    
            # Aplicar fuerzas con damping
            for node in nodes:
                pos = positions[node.node_id]
                force = forces[node.node_id]
                
                pos[0] += force[0] * damping
                pos[1] += force[1] * damping
                
        # Convertir a enteros
        return {node_id: (int(pos[0]), int(pos[1])) for node_id, pos in positions.items()}
        
    def _grid_layout(self, nodes: List[BaseNode]) -> Dict[str, Tuple[int, int]]:
        """
        Layout en grilla regular
        Organiza nodos en una cuadrícula
        """
        positions = {}
        grid_size = math.ceil(math.sqrt(len(nodes)))
        
        for i, node in enumerate(nodes):
            row = i // grid_size
            col = i % grid_size
            
            x = col * self.node_spacing
            y = row * self.node_spacing
            
            positions[node.node_id] = (x, y)
            
        return positions
        
    def _circular_layout(self, nodes: List[BaseNode]) -> Dict[str, Tuple[int, int]]:
        """
        Layout circular
        Organiza nodos en un círculo
        """
        positions = {}
        center_x, center_y = 0, 0
        radius = max(100, len(nodes) * 20)
        
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / len(nodes)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            positions[node.node_id] = (int(x), int(y))
            
        return positions
        
    def _layered_layout(self, nodes: List[BaseNode], edges: List) -> Dict[str, Tuple[int, int]]:
        """
        Layout por capas (Sugiyama algorithm simplificado)
        Minimiza cruces de conexiones
        """
        # Usar el layout jerárquico como base
        return self._hierarchical_layout(nodes, edges)
        
    def _build_graph(self, nodes: List[BaseNode], edges: List) -> Dict[str, List[str]]:
        """Construye un grafo de adyacencias"""
        graph = {node.node_id: [] for node in nodes}
        
        for edge in edges:
            if hasattr(edge, 'source_node') and hasattr(edge, 'target_node'):
                source_id = edge.source_node.node_id
                target_id = edge.target_node.node_id
                graph[source_id].append(target_id)
                
        return graph
        
    def _has_incoming_edges(self, node: BaseNode, edges: List) -> bool:
        """Verifica si un nodo tiene conexiones entrantes"""
        for edge in edges:
            if hasattr(edge, 'target_node') and edge.target_node.node_id == node.node_id:
                return True
        return False
        
    def _assign_levels_bfs(self, root_nodes: List[BaseNode], graph: Dict[str, List[str]]) -> List[List[BaseNode]]:
        """Asigna niveles usando BFS"""
        levels = []
        visited = set()
        current_level = root_nodes.copy()
        
        while current_level:
            levels.append(current_level.copy())
            next_level = []
            
            for node in current_level:
                visited.add(node.node_id)
                
                # Agregar nodos hijos al siguiente nivel
                for target_id in graph.get(node.node_id, []):
                    if target_id not in visited:
                        # Encontrar el nodo por ID
                        target_node = None
                        for n in current_level:
                            if n.node_id == target_id:
                                target_node = n
                                break
                                
                        if target_node and target_node not in next_level:
                            next_level.append(target_node)
                            
            current_level = next_level
            
        return levels


class ClusterLayoutEngine:
    """
    Motor de layout específico para clusters
    Posiciona clusters y sus contenidos
    """
    
    def __init__(self, padding: int = 30):
        self.padding = padding
        
    def layout_clusters(self, clusters: List[Cluster]) -> Dict[str, Dict[str, Any]]:
        """
        Calcula posiciones para clusters y sus nodos internos
        
        Returns:
            Dict con información de layout para cada cluster
        """
        cluster_layouts = {}
        
        for i, cluster in enumerate(clusters):
            # Layout interno del cluster
            internal_engine = LayoutEngine(
                algorithm=LayoutAlgorithm.HIERARCHICAL,
                node_spacing=120,
                layer_spacing=150
            )
            
            internal_positions = internal_engine.layout_nodes(cluster.nodes)
            
            # Aplicar posiciones a los nodos
            for node in cluster.nodes:
                if node.node_id in internal_positions:
                    x, y = internal_positions[node.node_id]
                    node.x = x
                    node.y = y
                    
            # Calcular bounds del cluster
            bounds = cluster.calculate_bounds()
            
            cluster_layouts[cluster.label or f"cluster_{i}"] = {
                'cluster': cluster,
                'bounds': bounds,
                'node_positions': internal_positions
            }
            
        return cluster_layouts


# ===== FUNCIONES DE CONVENIENCIA =====
def auto_layout(nodes: List[BaseNode], 
                edges: List = None,
                algorithm: str = "hierarchical",
                direction: str = "TB") -> Dict[str, Tuple[int, int]]:
    """
    Función de conveniencia para layout automático
    
    Args:
        nodes: Lista de nodos
        edges: Lista de conexiones
        algorithm: Tipo de algoritmo ("hierarchical", "force", "grid", "circular")
        direction: Dirección ("TB", "LR", "BT", "RL")
        
    Returns:
        Posiciones calculadas
    """
    layout_alg = LayoutAlgorithm(algorithm)
    layout_dir = LayoutDirection(direction)
    
    engine = LayoutEngine(algorithm=layout_alg, direction=layout_dir)
    return engine.layout_nodes(nodes, edges)


def apply_positions(nodes: List[BaseNode], positions: Dict[str, Tuple[int, int]]):
    """
    Aplica las posiciones calculadas a los nodos
    
    Args:
        nodes: Lista de nodos
        positions: Diccionario de posiciones
    """
    for node in nodes:
        if node.node_id in positions:
            x, y = positions[node.node_id]
            node.x = x
            node.y = y