"""
API principal extendida - DiagramsOffline
Alternativa liviana y offline a diagrams.mingrammer.com usando solo Pillow
"""

import os
from typing import Optional, List, Dict, Any, Union, Tuple
from .core.nodes import BaseNode, AWS, GCP, K8s, OnPrem, CustomNode
from .core.edges import Edge, EdgeStyle, EdgeColor
from .core.clusters import Cluster, DiagramContext
from .core.layout import LayoutEngine, LayoutAlgorithm, LayoutDirection, auto_layout, apply_positions
from .main import generate_diagram as generate_flowchart  # Mantener compatibilidad


class Diagram:
    """
    Clase principal para crear diagramas de arquitectura horizontal
    Compatible con la sintaxis de diagrams.mingrammer.com pero usando Pillow
    
    Example:
        >>> with Diagram("Web Services", show=False):
        ...     ELB("lb") >> EC2("web") >> RDS("userdb") >> S3("store")
        ...     ELB("lb") >> EC2("web") >> RDS("userdb") << EC2("stat")
    """
    
    # Variable de clase para manejar el contexto actual
    _current_diagram = None
    
    def __init__(self, 
                 name: str = "Architecture Diagram",
                 show: bool = True,
                 filename: Optional[str] = None,
                 direction: str = "LR",
                 **kwargs):
        """
        Inicializa un nuevo diagrama de arquitectura
        
        Args:
            name: Nombre del diagrama
            show: Si renderizar automáticamente al salir del contexto
            filename: Archivo de salida (opcional)
            direction: Dirección del layout (para futuras extensiones)
            **kwargs: Argumentos adicionales
        """
        self.name = name
        self.show = show
        self.filename = filename or f"{name.lower().replace(' ', '_')}.png"
        self.direction = direction
        
        # Listas para almacenar nodos y conexiones
        self.nodes: List[BaseNode] = []
        self.connections: List[Tuple[BaseNode, BaseNode]] = []
        
        # NUEVO: Sistema para rastrear secuencias/filas separadas
        self.sequences: List[List[BaseNode]] = []  # Cada sublista es una fila
        self.current_sequence: List[BaseNode] = []  # Secuencia actual siendo construida
        self.sequence_started: bool = False  # Flag para saber si ya se inició la secuencia actual
        
        # Cache de nodos por etiqueta para evitar duplicados
        self._node_cache: Dict[str, BaseNode] = {}
        
        # Asegurar que el archivo tenga extensión PNG
        if not self.filename.endswith('.png'):
            base_name = os.path.splitext(self.filename)[0]
            self.filename = f"{base_name}.png"
        
    def __enter__(self):
        """Context manager para uso con 'with'"""
        # Establecer este diagrama como el activo
        Diagram._current_diagram = self
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Salir del context manager y renderizar siempre"""
        # Siempre renderizar el diagrama (show=False solo significa no abrir el archivo)
        self.render()
        # Limpiar el diagrama activo
        Diagram._current_diagram = None
            
    def add_node(self, node: BaseNode) -> BaseNode:
        """Agrega un nodo al diagrama usando cache para evitar duplicados"""
        # Crear clave única basada en etiqueta y tipo
        cache_key = f"{node.label}_{node.node_type}"
        
        # Si ya existe en cache, retornar el existente
        if cache_key in self._node_cache:
            return self._node_cache[cache_key]
        
        # Si no existe, agregarlo al diagrama y cache
        self.nodes.append(node)
        self._node_cache[cache_key] = node
        return node
        
    def add_connection(self, source: BaseNode, target: BaseNode, direction: str = "right"):
        """Agrega una conexión entre nodos con dirección (mantiene compatibilidad)"""
        # Asegurar que ambos nodos estén en el diagrama
        self.add_node(source)
        self.add_node(target)
        
        # Agregar la conexión simple (compatibilidad)
        connection = (source, target)
        if connection not in self.connections:
            self.connections.append(connection)
    
    def start_new_sequence(self):
        """Inicia una nueva secuencia/fila"""
        if self.current_sequence:
            # Guardar la secuencia actual si tiene nodos
            self.sequences.append(self.current_sequence.copy())
        self.current_sequence = []
        self.sequence_started = False
    
    def add_to_current_sequence(self, node: BaseNode):
        """Agrega un nodo a la secuencia actual"""
        # Si el nodo ya está en una secuencia anterior como primer nodo,
        # y ya tenemos una secuencia actual, iniciar nueva secuencia
        if (self.sequence_started and 
            node not in self.current_sequence and 
            any(seq and len(seq) > 0 and seq[0] == node for seq in self.sequences)):
            self.start_new_sequence()
        
        # Agregar nodo a la secuencia actual
        if node not in self.current_sequence:
            self.current_sequence.append(node)
            self.sequence_started = True
    
    def finalize_sequences(self):
        """Finaliza todas las secuencias"""
        if self.current_sequence:
            self.sequences.append(self.current_sequence.copy())
            self.current_sequence = []
        
    def render(self) -> str:
        """
        Renderiza el diagrama usando el ArchitectureRenderer
        """
        from .renderers.architecture_renderer import render_architecture_diagram
        
        # Finalizar las secuencias antes de renderizar
        self.finalize_sequences()
        
        result = render_architecture_diagram(
            title=self.name,
            nodes=self.nodes,
            connections=self.connections,
            sequences=self.sequences,  # Pasar las secuencias
            filename=self.filename
        )
        
        # Mensaje simple y limpio
        print(f"Diagrama: {os.path.basename(self.filename)} generado exitosamente")
        
        return result
        
    @classmethod
    def get_current_diagram(cls):
        """Retorna el diagrama actualmente activo"""
        return cls._current_diagram


# ===== NODOS ESPECÍFICOS PARA ARQUITECTURA =====

class ArchitectureNode(BaseNode):
    """Nodo base para diagramas de arquitectura"""
    
    def __init__(self, label: str, node_type: str = "default"):
        super().__init__(label)
        self.node_type = node_type
        # No auto-registrar aquí, se hará en las funciones de creación
    
    def get_shape_type(self) -> str:
        """Retorna el tipo de forma para este nodo de arquitectura"""
        return "rectangle"  # Los nodos de arquitectura son cuadrados/rectángulos
    
    def __rshift__(self, other):
        """Operador >> para conexiones hacia la derecha"""
        current_diagram = Diagram.get_current_diagram()
        if current_diagram:
            # Agregar nodos a la secuencia actual
            current_diagram.add_to_current_sequence(self)
            if isinstance(other, list):
                # Conexión a múltiples nodos
                for node in other:
                    current_diagram.add_connection(self, node)
                    current_diagram.add_to_current_sequence(node)
                return other
            else:
                # Conexión a un solo nodo
                current_diagram.add_connection(self, other)
                current_diagram.add_to_current_sequence(other)
                return other
        return other
        
    def __lshift__(self, other):
        """Operador << para conexiones hacia la izquierda"""
        current_diagram = Diagram.get_current_diagram()
        if current_diagram:
            # Para simular flecha izquierda, agregar el target primero y luego source
            # Esto hará que en la secuencia aparezcan en orden: other, self
            current_diagram.add_to_current_sequence(other)  # Agregar target primero
            current_diagram.add_to_current_sequence(self)   # Agregar source después
            # La conexión sigue siendo normal para compatibilidad
            current_diagram.add_connection(self, other)
        return other
    
    def __sub__(self, other):
        """Operador - para desconexión (no hace nada, solo devuelve el otro nodo)"""
        return other


# ===== FUNCIONES PARA CREAR NODOS =====

def ELB(label: str = "Load Balancer") -> ArchitectureNode:
    """Crea un nodo Elastic Load Balancer con auto-detección de filas"""
    current_diagram = Diagram.get_current_diagram()
    if current_diagram:
        # AUTO-DETECCIÓN: Si ya hay una secuencia activa y este ELB inicia una nueva expresión
        if (current_diagram.sequence_started and 
            (len(current_diagram.sequences) > 0 or len(current_diagram.current_sequence) > 3)):
            current_diagram.start_new_sequence()
        
        # Crear nodo y usar cache del diagrama
        node = ArchitectureNode(label, "ELB")
        return current_diagram.add_node(node)
    else:
        return ArchitectureNode(label, "ELB")

def EC2(label: str = "Server") -> ArchitectureNode:
    """Crea un nodo EC2 (servidor)"""
    current_diagram = Diagram.get_current_diagram()
    if current_diagram:
        node = ArchitectureNode(label, "EC2")
        return current_diagram.add_node(node)
    else:
        return ArchitectureNode(label, "EC2")

def RDS(label: str = "Database") -> ArchitectureNode:
    """Crea un nodo RDS (base de datos)"""
    current_diagram = Diagram.get_current_diagram()
    if current_diagram:
        node = ArchitectureNode(label, "RDS")
        return current_diagram.add_node(node)
    else:
        return ArchitectureNode(label, "RDS")

def S3(label: str = "Storage") -> ArchitectureNode:
    """Crea un nodo S3 (almacenamiento)"""
    current_diagram = Diagram.get_current_diagram()
    if current_diagram:
        node = ArchitectureNode(label, "S3")
        return current_diagram.add_node(node)
    else:
        return ArchitectureNode(label, "S3")

def Lambda(label: str = "Function") -> ArchitectureNode:
    """Crea un nodo Lambda (función)"""
    node = ArchitectureNode(label, "Lambda")
    return node

# ===== ALIAS PARA COMPATIBILIDAD =====
# Importar clases de nodos para uso directo
from .core.nodes import (
    GenericNode as Node,
    CloudNode as Cloud,
    DatabaseNode as Database,
    ProcessNode as Process,
    DecisionNode as Decision,
    StartEndNode as StartEnd,
    CustomNode as Custom
)

# Alias para edges
from .core.edges import (
    Edge,
    EdgeStyle,
    EdgeColor,
    edge,
    red_edge,
    green_edge,
    blue_edge,
    dashed_edge,
    dotted_edge,
    bold_edge
)


# ===== FUNCIONES DE CONVENIENCIA =====
def create_architecture_diagram(
    name: str = "Architecture",
    filename: Optional[str] = None
) -> Diagram:
    """
    Crea un diagrama de arquitectura con configuración típica
    
    Args:
        name: Nombre del diagrama
        filename: Archivo de salida
        
    Returns:
        Instancia de Diagram configurada
    """
    return Diagram(
        name=name,
        filename=filename,
        show=False  # No renderizar automáticamente
    )


def create_aws_diagram(name: str = "AWS Architecture") -> Diagram:
    """Crea un diagrama optimizado para servicios AWS"""
    return create_architecture_diagram(
        name=name
    )


# ===== EJEMPLO DE USO COMPLETO =====
def example_web_services():
    """
    Ejemplo completo de uso - Sintaxis idéntica a diagrams.mingrammer.com
    """
    
    with Diagram("Web Services", show=False) as diagram:
        # Crear la arquitectura exactamente como en tu ejemplo
        ELB("lb") >> EC2("web") >> RDS("userdb") >> S3("store")
        ELB("lb") >> EC2("web") >> RDS("userdb") << EC2("stat")
    
    return diagram.filename


if __name__ == "__main__":
    # Ejecutar ejemplo
    filename = example_web_services()
    print(f"Diagrama: {os.path.basename(filename)} generado exitosamente")


# ===== ALIASES PARA COMPATIBILIDAD =====
# Importar clases de nodos para uso directo
from .core.nodes import (
    GenericNode as Node,
    CloudNode as Cloud,
    DatabaseNode as Database,
    ProcessNode as Process,
    DecisionNode as Decision,
    StartEndNode as StartEnd,
    CustomNode as Custom
)

# Alias para edges
from .core.edges import (
    Edge,
    EdgeStyle,
    EdgeColor,
    edge,
    red_edge,
    green_edge,
    blue_edge,
    dashed_edge,
    dotted_edge,
    bold_edge
)


# ===== FUNCIONES DE CONVENIENCIA =====
def create_architecture_diagram(
    name: str = "Architecture",
    layout: str = "hierarchical",
    direction: str = "TB",
    filename: Optional[str] = None
) -> Diagram:
    """
    Crea un diagrama de arquitectura con configuración típica
    
    Args:
        name: Nombre del diagrama
        layout: Algoritmo de layout
        direction: Dirección del flujo
        filename: Archivo de salida
        
    Returns:
        Instancia de Diagram configurada
    """
    return Diagram(
        name=name,
        layout_algorithm=layout,
        direction=direction,
        filename=filename,
        show=False  # No renderizar automáticamente
    )


def create_aws_diagram(name: str = "AWS Architecture") -> Diagram:
    """Crea un diagrama optimizado para servicios AWS"""
    return create_architecture_diagram(
        name=name,
        layout="hierarchical",
        direction="TB"
    )


def create_kubernetes_diagram(name: str = "Kubernetes Architecture") -> Diagram:
    """Crea un diagrama optimizado para Kubernetes"""
    return create_architecture_diagram(
        name=name,
        layout="layered",
        direction="LR"
    )


def create_microservices_diagram(name: str = "Microservices Architecture") -> Diagram:
    """Crea un diagrama optimizado para microservicios"""
    return create_architecture_diagram(
        name=name,
        layout="force",
        direction="TB"
    )


# ===== FUNCIONES DE MIGRACIÓN =====
def migrate_from_diagrams(diagrams_code: str) -> str:
    """
    Ayuda a migrar código de diagrams.mingrammer.com a DiagramsOffline
    
    Args:
        diagrams_code: Código usando diagrams.mingrammer.com
        
    Returns:
        Código convertido para DiagramsOffline
    """
    # Mapeo básico de imports
    replacements = {
        'from diagrams import': 'from flujograma import',
        'from diagrams.aws': 'from flujograma.aws',
        'from diagrams.gcp': 'from flujograma.gcp', 
        'from diagrams.k8s': 'from flujograma.k8s',
        'from diagrams.onprem': 'from flujograma.onprem',
        'from diagrams.custom import Custom': 'from flujograma import CustomNode as Custom',
    }
    
    converted_code = diagrams_code
    for old, new in replacements.items():
        converted_code = converted_code.replace(old, new)
        
    return converted_code


def get_compatibility_report() -> Dict[str, Any]:
    """
    Retorna un reporte de compatibilidad con diagrams.mingrammer.com
    
    Returns:
        Diccionario con información de compatibilidad
    """
    return {
        "compatible_features": [
            "Sintaxis 'with Diagram()'",
            "Operadores >> y << para conexiones",
            "Clusters para agrupación",
            "Edges con colores y estilos",
            "Nodos AWS, GCP, K8s básicos",
            "Custom nodes con iconos"
        ],
        "advantages": [
            "No requiere Graphviz (instalación más simple)",
            "Funciona 100% offline",
            "Renderizado más rápido con Pillow",
            "Menor tamaño de instalación",
            "Control total sobre el renderizado"
        ],
        "limitations": [
            "Menor catálogo de iconos (en desarrollo)",
            "Algunos layouts avanzados no implementados",
            "No soporte para formatos DOT nativos"
        ],
        "migration_effort": "Bajo - Principalmente cambios de imports"
    }


# ===== EJEMPLO DE USO COMPLETO =====
def example_aws_architecture():
    """
    Ejemplo completo de uso - Arquitectura AWS
    Equivalente al ejemplo de diagrams.mingrammer.com
    """
    from .core.nodes import AWS
    from .core.edges import Edge, EdgeColor, EdgeStyle
    
    with Diagram("Advanced Web Service", show=False) as diagram:
        # Load balancer
        lb = AWS.ELB("Load Balancer")
        
        # Web servers cluster
        with Cluster("Web Servers"):
            web_servers = [
                AWS.EC2("web1"),
                AWS.EC2("web2"), 
                AWS.EC2("web3")
            ]
            
        # Database cluster
        with Cluster("Database"):
            db_primary = AWS.RDS("primary")
            db_replica = AWS.RDS("replica")
            db_primary >> Edge(color=EdgeColor.BLUE, style=EdgeStyle.DASHED) >> db_replica
            
        # Storage
        storage = AWS.S3("Static Files")
        
        # Serverless functions
        lambda_func = AWS.Lambda("API Handler")
        
        # Connections
        lb >> web_servers
        web_servers >> db_primary
        web_servers >> storage
        lambda_func >> db_primary
        
    return diagram.filename


if __name__ == "__main__":
    # Ejecutar ejemplo
    filename = example_aws_architecture()
    print(f"Diagrama: {os.path.basename(filename)} generado exitosamente")