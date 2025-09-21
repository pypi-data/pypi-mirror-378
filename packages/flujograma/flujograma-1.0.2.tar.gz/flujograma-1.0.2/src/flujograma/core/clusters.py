"""
Sistema de agrupación (Clusters) inspirado en diagrams.mingrammer.com
Implementación con Pillow para máximo rendimiento offline
"""

from typing import List, Optional, Dict, Any, Tuple
from .nodes import BaseNode


class Cluster:
    """
    Representa un agrupamiento visual de nodos
    Inspirado en los Clusters de diagrams.mingrammer.com
    """
    
    def __init__(self, 
                 label: str = "",
                 direction: str = "TB",
                 graph_attr: Dict[str, Any] = None,
                 node_attr: Dict[str, Any] = None,
                 edge_attr: Dict[str, Any] = None):
        """
        Inicializa un cluster
        
        Args:
            label: Etiqueta del cluster
            direction: Dirección del layout (TB, LR, BT, RL)
            graph_attr: Atributos del grafo
            node_attr: Atributos por defecto de los nodos
            edge_attr: Atributos por defecto de las conexiones
        """
        self.label = label
        self.direction = direction
        self.nodes: List[BaseNode] = []
        self.subclusters: List['Cluster'] = []
        self.parent_cluster: Optional['Cluster'] = None
        
        # Atributos visuales
        self.graph_attr = graph_attr or {}
        self.node_attr = node_attr or {}
        self.edge_attr = edge_attr or {}
        
        # Propiedades del contenedor visual
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.padding = 20
        self.border_color = "#CCCCCC"
        self.border_width = 2
        self.background_color = "#F8F8F8"
        self.label_color = "#333333"
        self.corner_radius = 10
        
        # Stack de clusters activos (para context manager)
        self._active_clusters_stack = []
        
    def __enter__(self):
        """Context manager para uso con 'with'"""
        # Agregar este cluster al stack global
        if not hasattr(Cluster, '_global_stack'):
            Cluster._global_stack = []
        Cluster._global_stack.append(self)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Salir del context manager"""
        if hasattr(Cluster, '_global_stack') and Cluster._global_stack:
            Cluster._global_stack.pop()
            
    def add_node(self, node: BaseNode) -> BaseNode:
        """Agrega un nodo al cluster"""
        if node not in self.nodes:
            self.nodes.append(node)
            # Aplicar atributos por defecto del cluster al nodo
            if self.node_attr:
                for attr, value in self.node_attr.items():
                    if hasattr(node, attr):
                        setattr(node, attr, value)
        return node
        
    def add_subcluster(self, subcluster: 'Cluster') -> 'Cluster':
        """Agrega un subcluster"""
        if subcluster not in self.subclusters:
            self.subclusters.append(subcluster)
            subcluster.parent_cluster = self
        return subcluster
        
    def get_all_nodes(self) -> List[BaseNode]:
        """Retorna todos los nodos incluyendo los de subclusters"""
        all_nodes = self.nodes.copy()
        for subcluster in self.subclusters:
            all_nodes.extend(subcluster.get_all_nodes())
        return all_nodes
        
    def calculate_bounds(self) -> Tuple[int, int, int, int]:
        """
        Calcula los límites del cluster basado en sus nodos
        Retorna: (x_min, y_min, x_max, y_max)
        """
        if not self.nodes and not self.subclusters:
            return (0, 0, 200, 100)
            
        x_coords = []
        y_coords = []
        
        # Coordenadas de nodos directos
        for node in self.nodes:
            x_coords.extend([node.x, node.x + node.width])
            y_coords.extend([node.y, node.y + node.height])
            
        # Coordenadas de subclusters
        for subcluster in self.subclusters:
            sub_x_min, sub_y_min, sub_x_max, sub_y_max = subcluster.calculate_bounds()
            x_coords.extend([sub_x_min, sub_x_max])
            y_coords.extend([sub_y_min, sub_y_max])
            
        if not x_coords:
            return (0, 0, 200, 100)
            
        x_min = min(x_coords) - self.padding
        y_min = min(y_coords) - self.padding
        x_max = max(x_coords) + self.padding
        y_max = max(y_coords) + self.padding
        
        # Actualizar propiedades del cluster
        self.x = x_min
        self.y = y_min
        self.width = x_max - x_min
        self.height = y_max - y_min
        
        return (x_min, y_min, x_max, y_max)
        
    def get_render_params(self) -> Dict[str, Any]:
        """Retorna parámetros para el renderer"""
        x_min, y_min, x_max, y_max = self.calculate_bounds()
        
        return {
            'label': self.label,
            'x': x_min,
            'y': y_min,
            'width': x_max - x_min,
            'height': y_max - y_min,
            'border_color': self.border_color,
            'border_width': self.border_width,
            'background_color': self.background_color,
            'label_color': self.label_color,
            'corner_radius': self.corner_radius,
            'padding': self.padding
        }


class DiagramContext:
    """
    Contexto principal del diagrama que maneja clusters automáticamente
    Inspirado en el 'with Diagram()' de diagrams.mingrammer.com
    """
    
    def __init__(self, 
                 name: str = "Architecture",
                 direction: str = "TB",
                 filename: Optional[str] = None,
                 show: bool = True,
                 graph_attr: Dict[str, Any] = None,
                 node_attr: Dict[str, Any] = None,
                 edge_attr: Dict[str, Any] = None,
                 outformat: str = "png"):
        """
        Inicializa el contexto del diagrama
        
        Args:
            name: Nombre del diagrama
            direction: Dirección del layout
            filename: Archivo de salida (opcional)
            show: Si mostrar el resultado
            graph_attr: Atributos del grafo
            node_attr: Atributos por defecto de nodos
            edge_attr: Atributos por defecto de edges
            outformat: Formato de salida
        """
        self.name = name
        self.direction = direction
        self.filename = filename or f"{name.lower().replace(' ', '_')}.{outformat}"
        self.show = show
        self.outformat = outformat
        
        self.graph_attr = graph_attr or {}
        self.node_attr = node_attr or {}
        self.edge_attr = edge_attr or {}
        
        self.nodes: List[BaseNode] = []
        self.clusters: List[Cluster] = []
        self.edges = []
        
        # Inicializar stack global si no existe
        if not hasattr(Cluster, '_global_stack'):
            Cluster._global_stack = []
            
    def __enter__(self):
        """Context manager para el diagrama completo"""
        # Limpiar stack global
        Cluster._global_stack = []
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Generar el diagrama al salir del context"""
        if self.show:
            self.render()
            
    def add_node(self, node: BaseNode) -> BaseNode:
        """Agrega un nodo al diagrama o al cluster activo"""
        # Si hay un cluster activo, agregar ahí
        if hasattr(Cluster, '_global_stack') and Cluster._global_stack:
            active_cluster = Cluster._global_stack[-1]
            active_cluster.add_node(node)
        else:
            # Agregar directamente al diagrama
            if node not in self.nodes:
                self.nodes.append(node)
                
        return node
        
    def add_cluster(self, cluster: Cluster) -> Cluster:
        """Agrega un cluster al diagrama"""
        if cluster not in self.clusters:
            self.clusters.append(cluster)
        return cluster
        
    def render(self) -> str:
        """Renderiza el diagrama usando el PillowRenderer extendido"""
        from ..renderers.pillow_renderer import PillowRenderer
        from ..core.diagram import FlowDiagram
        
        # Crear un diagrama compatible
        diagram = FlowDiagram()
        diagram.title = self.name
        
        # Agregar nodos y clusters al diagrama
        # Adaptar FlowDiagram para soportar clusters
        
        renderer = PillowRenderer(diagram)
        return renderer.render(self.filename)


# ===== FUNCIONES DE CONVENIENCIA =====
def auto_node_registration(node: BaseNode) -> BaseNode:
    """
    Registra automáticamente un nodo en el cluster activo
    Se llama automáticamente al crear nodos dentro de un 'with Cluster'
    """
    if hasattr(Cluster, '_global_stack') and Cluster._global_stack:
        active_cluster = Cluster._global_stack[-1]
        active_cluster.add_node(node)
    return node


# Monkey patch para auto-registro de nodos
original_base_node_init = BaseNode.__init__

def patched_base_node_init(self, *args, **kwargs):
    original_base_node_init(self, *args, **kwargs)
    auto_node_registration(self)

BaseNode.__init__ = patched_base_node_init


# ===== EJEMPLOS DE USO =====
"""
Ejemplos de uso inspirados en diagrams.mingrammer.com:

# Diagrama simple con clusters
from flujograma.core.nodes import AWS
from flujograma.core.clusters import DiagramContext, Cluster

with DiagramContext("Clustered Web Services", show=False):
    dns = AWS.Route53("dns")
    lb = AWS.ELB("lb")

    with Cluster("Services"):
        svc_group = [AWS.ECS("web1"),
                     AWS.ECS("web2"), 
                     AWS.ECS("web3")]

    with Cluster("DB Cluster"):
        db_primary = AWS.RDS("userdb")
        db_primary - [AWS.RDS("userdb ro")]

    memcached = AWS.ElastiCache("memcached")

    dns >> lb >> svc_group
    svc_group >> db_primary
    svc_group >> memcached
"""