"""
Sistema de nodos genérico inspirado en diagrams.mingrammer.com
Implementación con Pillow para máximo rendimiento offline
"""

import os
from typing import List, Optional, Tuple, Dict, Any
from abc import ABC, abstractmethod
from PIL import Image, ImageDraw, ImageFont


class EdgeBuilder:
    """Clase auxiliar para construcción de edges con estilo"""
    
    def __init__(self, source_node, style_dict):
        self.source_node = source_node
        self.style_dict = style_dict
        
    def __rshift__(self, target_node):
        """Completa la conexión con el nodo destino"""
        return self.source_node.connect_to(target_node, self.style_dict)


class BaseNode(ABC):
    """Clase base para todos los nodos del diagrama"""
    
    def __init__(self, label: str = "", node_id: str = None):
        self.label = label
        self.node_id = node_id or f"node_{id(self)}"
        self.x = 0
        self.y = 0
        self.width = 120
        self.height = 80
        self.connections = []
        self.color = "#4A90E2"
        self.text_color = "#FFFFFF"
        self.icon_path = None
        
    @abstractmethod
    def get_shape_type(self) -> str:
        """Retorna el tipo de forma para el renderer"""
        pass
        
    def connect_to(self, other_node: 'BaseNode', edge_style: Dict = None):
        """Conecta este nodo con otro"""
        from .edges import Edge
        edge = Edge(self, other_node, style=edge_style or {})
        self.connections.append(edge)
        return edge
        
    def __rshift__(self, other):
        """Operador >> para conexiones como en diagrams"""
        if isinstance(other, dict):
            # Si other es un diccionario de estilo, crear un EdgeBuilder
            return EdgeBuilder(self, other)
        elif isinstance(other, list):
            edges = []
            for node in other:
                edges.append(self.connect_to(node))
            return edges
        else:
            return self.connect_to(other)
            
    def __lshift__(self, other):
        """Operador << para conexiones inversas"""
        if isinstance(other, list):
            edges = []
            for node in other:
                edges.append(node.connect_to(self))
            return edges
        else:
            return other.connect_to(self)


class GenericNode(BaseNode):
    """Nodo genérico rectangular"""
    
    def __init__(self, label: str = "", color: str = "#4A90E2"):
        super().__init__(label)
        self.color = color
        
    def get_shape_type(self) -> str:
        return "rectangle"


class CloudNode(BaseNode):
    """Nodo base para servicios en la nube"""
    
    def __init__(self, label: str = "", service_type: str = "generic"):
        super().__init__(label)
        self.service_type = service_type
        self.color = "#FF9900"  # Color AWS por defecto
        
    def get_shape_type(self) -> str:
        return "rectangle"


class DatabaseNode(BaseNode):
    """Nodo para bases de datos"""
    
    def __init__(self, label: str = ""):
        super().__init__(label)
        self.color = "#3498db"
        
    def get_shape_type(self) -> str:
        return "cylinder"


class ProcessNode(BaseNode):
    """Nodo para procesos"""
    
    def __init__(self, label: str = ""):
        super().__init__(label)
        self.color = "#e74c3c"
        
    def get_shape_type(self) -> str:
        return "rectangle"


class DecisionNode(BaseNode):
    """Nodo para decisiones"""
    
    def __init__(self, label: str = ""):
        super().__init__(label)
        self.color = "#f39c12"
        
    def get_shape_type(self) -> str:
        return "diamond"


class StartEndNode(BaseNode):
    """Nodo para inicio/fin"""
    
    def __init__(self, label: str = "", is_start: bool = True):
        super().__init__(label)
        self.is_start = is_start
        self.color = "#2ecc71" if is_start else "#e74c3c"
        
    def get_shape_type(self) -> str:
        return "oval"


# ===== NODOS AWS =====
class AWS:
    """Namespace para nodos de Amazon Web Services"""
    
    class EC2(CloudNode):
        def __init__(self, label: str = "EC2"):
            super().__init__(label, "ec2")
            self.color = "#FF9900"
            self.icon_path = "aws/compute/ec2.png"
            
    class RDS(DatabaseNode):
        def __init__(self, label: str = "RDS"):
            super().__init__(label)
            self.color = "#3498db"
            self.icon_path = "aws/database/rds.png"
            
    class Lambda(CloudNode):
        def __init__(self, label: str = "Lambda"):
            super().__init__(label, "lambda")
            self.color = "#FF9900"
            self.icon_path = "aws/compute/lambda.png"
            
    class S3(CloudNode):
        def __init__(self, label: str = "S3"):
            super().__init__(label, "s3")
            self.color = "#FF9900"
            self.icon_path = "aws/storage/s3.png"
            
    class ELB(CloudNode):
        def __init__(self, label: str = "Load Balancer"):
            super().__init__(label, "elb")
            self.color = "#FF9900"
            self.icon_path = "aws/network/elb.png"


# ===== NODOS GCP =====
class GCP:
    """Namespace para nodos de Google Cloud Platform"""
    
    class ComputeEngine(CloudNode):
        def __init__(self, label: str = "Compute Engine"):
            super().__init__(label, "compute")
            self.color = "#4285F4"
            self.icon_path = "gcp/compute/compute_engine.png"
            
    class CloudSQL(DatabaseNode):
        def __init__(self, label: str = "Cloud SQL"):
            super().__init__(label)
            self.color = "#4285F4"
            self.icon_path = "gcp/database/cloud_sql.png"
            
    class CloudStorage(CloudNode):
        def __init__(self, label: str = "Cloud Storage"):
            super().__init__(label, "storage")
            self.color = "#4285F4"
            self.icon_path = "gcp/storage/cloud_storage.png"


# ===== NODOS KUBERNETES =====
class K8s:
    """Namespace para nodos de Kubernetes"""
    
    class Pod(ProcessNode):
        def __init__(self, label: str = "Pod"):
            super().__init__(label)
            self.color = "#326CE5"
            self.icon_path = "k8s/compute/pod.png"
            
    class Service(ProcessNode):
        def __init__(self, label: str = "Service"):
            super().__init__(label)
            self.color = "#326CE5"
            self.icon_path = "k8s/network/service.png"
            
    class Deployment(ProcessNode):
        def __init__(self, label: str = "Deployment"):
            super().__init__(label)
            self.color = "#326CE5"
            self.icon_path = "k8s/compute/deployment.png"


# ===== NODOS ON-PREMISES =====
class OnPrem:
    """Namespace para nodos on-premises"""
    
    class Server(ProcessNode):
        def __init__(self, label: str = "Server"):
            super().__init__(label)
            self.color = "#34495e"
            self.icon_path = "onprem/compute/server.png"
            
    class Database(DatabaseNode):
        def __init__(self, label: str = "Database"):
            super().__init__(label)
            self.color = "#34495e"
            self.icon_path = "onprem/database/database.png"
            
    class LoadBalancer(ProcessNode):
        def __init__(self, label: str = "Load Balancer"):
            super().__init__(label)
            self.color = "#34495e"
            self.icon_path = "onprem/network/load_balancer.png"


# ===== CUSTOM NODES =====
class CustomNode(BaseNode):
    """Nodo personalizado con icono custom"""
    
    def __init__(self, label: str = "", icon_path: str = None, color: str = "#95a5a6"):
        super().__init__(label)
        self.color = color
        self.icon_path = icon_path
        
    def get_shape_type(self) -> str:
        return "rectangle"


# ===== FUNCIONES DE UTILIDAD =====
def download_icon(url: str, filename: str) -> str:
    """
    Descarga un icono desde una URL y lo guarda localmente
    Inspirado en el ejemplo de RabbitMQ de diagrams
    """
    try:
        from urllib.request import urlretrieve
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")
        os.makedirs(assets_dir, exist_ok=True)
        
        icon_path = os.path.join(assets_dir, filename)
        urlretrieve(url, icon_path)
        return icon_path
    except Exception as e:
        print(f"Error descargando icono: {e}")
        return None


def create_custom_node(label: str, icon_url: str = None, icon_file: str = None, color: str = "#95a5a6") -> CustomNode:
    """
    Crea un nodo personalizado con icono
    """
    icon_path = None
    if icon_url and icon_file:
        icon_path = download_icon(icon_url, icon_file)
    elif icon_file:
        icon_path = icon_file
        
    return CustomNode(label=label, icon_path=icon_path, color=color)