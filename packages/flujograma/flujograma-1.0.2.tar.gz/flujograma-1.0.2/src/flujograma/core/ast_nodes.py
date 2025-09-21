"""
Nodos del AST (Abstract Syntax Tree) para representar elementos del diagrama de flujo
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from enum import Enum


class NodeType(Enum):
    """Tipos de nodos en el diagrama de flujo"""
    START = "start"
    END = "end"
    PROCESS = "process"
    DECISION = "decision"
    INPUT_OUTPUT = "input_output"
    CONNECTOR = "connector"


class FlowNode(ABC):
    """Clase base abstracta para todos los nodos del diagrama"""
    
    def __init__(self, node_id: str, text: str = "", node_type: NodeType = NodeType.PROCESS):
        self.id = node_id
        self.text = text
        self.type = node_type
        self.connections: List['Connection'] = []
        self.position: Optional[tuple] = None
    
    def add_connection(self, target_node: 'FlowNode', label: str = ""):
        """Añade una conexión a otro nodo"""
        connection = Connection(self, target_node, label)
        self.connections.append(connection)
        return connection
    
    @abstractmethod
    def accept(self, visitor):
        """Patrón Visitor para renderizado"""
        pass


class StartNode(FlowNode):
    """Nodo de inicio del diagrama"""
    
    def __init__(self, node_id: str, text: str = "Inicio"):
        super().__init__(node_id, text, NodeType.START)
    
    def accept(self, visitor):
        return visitor.visit_start_node(self)


class EndNode(FlowNode):
    """Nodo de fin del diagrama"""
    
    def __init__(self, node_id: str, text: str = "Fin"):
        super().__init__(node_id, text, NodeType.END)
    
    def accept(self, visitor):
        return visitor.visit_end_node(self)


class ProcessNode(FlowNode):
    """Nodo de proceso/acción"""
    
    def __init__(self, node_id: str, text: str):
        super().__init__(node_id, text, NodeType.PROCESS)
    
    def accept(self, visitor):
        return visitor.visit_process_node(self)


class DecisionNode(FlowNode):
    """Nodo de decisión/condición"""
    
    def __init__(self, node_id: str, condition: str):
        super().__init__(node_id, condition, NodeType.DECISION)
        self.condition = condition
        self.true_branch: Optional[FlowNode] = None
        self.false_branch: Optional[FlowNode] = None
    
    def set_branches(self, true_branch: FlowNode, false_branch: FlowNode = None):
        """Establece las ramas verdadera y falsa"""
        self.true_branch = true_branch
        self.false_branch = false_branch
        
        # Añadir conexiones con etiquetas
        self.add_connection(true_branch, "Sí")
        if false_branch:
            self.add_connection(false_branch, "No")
    
    def accept(self, visitor):
        return visitor.visit_decision_node(self)


class InputOutputNode(FlowNode):
    """Nodo de entrada/salida de datos"""
    
    def __init__(self, node_id: str, text: str, is_input: bool = True):
        super().__init__(node_id, text, NodeType.INPUT_OUTPUT)
        self.is_input = is_input
    
    def accept(self, visitor):
        return visitor.visit_input_output_node(self)


class ConnectorNode(FlowNode):
    """Nodo conector para unir flujos"""
    
    def __init__(self, node_id: str, text: str = ""):
        super().__init__(node_id, text, NodeType.CONNECTOR)
    
    def accept(self, visitor):
        return visitor.visit_connector_node(self)


class Connection:
    """Representa una conexión entre dos nodos"""
    
    def __init__(self, source: FlowNode, target: FlowNode, label: str = ""):
        self.source = source
        self.target = target
        self.label = label
    
    def __repr__(self):
        return f"Connection({self.source.id} -> {self.target.id}, '{self.label}')"


class LoopNode(FlowNode):
    """Nodo especial para representar bucles"""
    
    def __init__(self, node_id: str, condition: str, body_nodes: List[FlowNode]):
        super().__init__(node_id, f"Mientras {condition}", NodeType.DECISION)
        self.condition = condition
        self.body_nodes = body_nodes
    
    def accept(self, visitor):
        return visitor.visit_loop_node(self)
