"""
Parser principal para convertir texto en lenguaje natural a diagramas de flujo
"""

import re
from typing import List, Dict, Any, Optional
from .diagram import FlowDiagram
from .ast_nodes import (
    StartNode, EndNode, ProcessNode, DecisionNode, 
    InputOutputNode, ConnectorNode, LoopNode
)
from ..languages.base import LanguageRules


class FlowParser:
    """Parser principal que convierte texto a diagrama de flujo"""
    
    def __init__(self, language: str = "es"):
        self.language = language
        self.rules = self._load_language_rules(language)
        self.diagram = None
        self._node_counter = 0
    
    def _load_language_rules(self, language: str) -> LanguageRules:
        """Carga las reglas del idioma especificado"""
        if language == "es":
            from ..languages.es import SpanishRules
            return SpanishRules()
        elif language == "en":
            from ..languages.en import EnglishRules
            return EnglishRules()
        else:
            raise ValueError(f"Idioma '{language}' no soportado")
    
    def parse(self, text: str) -> FlowDiagram:
        """Convierte texto en lenguaje natural a un diagrama de flujo"""
        self.diagram = FlowDiagram()
        self._node_counter = 0
        
        # Preprocesar el texto
        lines = self._preprocess_text(text)
        
        # Crear nodo de inicio automáticamente
        start_node = StartNode(self._get_next_node_id(), self.rules.get_start_text())
        self.diagram.add_node(start_node)
        current_node = start_node
        
        # Procesar cada línea
        for line in lines:
            if not line.strip():
                continue
            
            new_nodes = self._parse_line(line.strip())
            
            # Conectar con el nodo anterior solo si se crearon nuevos nodos
            if new_nodes and current_node:
                current_node.add_connection(new_nodes[0])
                current_node = new_nodes[-1]  # El último nodo creado
            elif new_nodes:  # Si hay nuevos nodos pero no hay current_node
                current_node = new_nodes[-1]
        
        # Crear nodo de fin automáticamente si no existe
        if not self.diagram.end_nodes:
            end_node = EndNode(self._get_next_node_id(), self.rules.get_end_text())
            self.diagram.add_node(end_node)
            if current_node:
                current_node.add_connection(end_node)
        
        # Calcular layout
        self.diagram.calculate_layout()
        
        return self.diagram
    
    def _preprocess_text(self, text: str) -> List[str]:
        """Preprocesa el texto separándolo en líneas y normalizándolo"""
        # Dividir en líneas
        lines = text.split('\n')
        
        # Limpiar y normalizar
        processed_lines = []
        for line in lines:
            line = line.strip()
            if line:
                # Normalizar espacios
                line = re.sub(r'\s+', ' ', line)
                # Asegurar que termine con punto si no tiene puntuación
                if not line.endswith(('.', ',', ';', ':', '?', '!')):
                    line += '.'
                processed_lines.append(line)
        
        return processed_lines
    
    def _parse_line(self, line: str) -> List[Any]:
        """Parsea una línea individual y retorna los nodos creados"""
        line = line.strip()
        
        # Intentar diferentes patrones en orden de prioridad
        patterns = [
            (self.rules.conditional_patterns, self._parse_conditional),
            (self.rules.loop_patterns, self._parse_loop),
            (self.rules.input_output_patterns, self._parse_input_output),
            (self.rules.start_patterns, self._parse_start),
            (self.rules.end_patterns, self._parse_end),
            (self.rules.process_patterns, self._parse_process),
        ]
        
        for pattern_list, parser_func in patterns:
            for pattern in pattern_list:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return parser_func(match, line)
        
        # Si no coincide con ningún patrón, tratarlo como proceso
        return self._parse_generic_process(line)
    
    def _parse_conditional(self, match, line: str) -> List[Any]:
        """Parsea una estructura condicional (if-then-else)"""
        groups = match.groups()
        
        # Extraer condición y acciones
        condition = groups[0] if groups[0] else ""
        then_action = groups[1] if len(groups) > 1 and groups[1] else ""
        else_action = groups[2] if len(groups) > 2 and groups[2] else ""
        
        # Crear nodo de decisión
        decision_node = DecisionNode(self._get_next_node_id(), condition)
        self.diagram.add_node(decision_node)
        
        nodes_created = [decision_node]
        
        # Crear nodo para la acción "entonces"
        if then_action:
            then_node = ProcessNode(self._get_next_node_id(), then_action)
            self.diagram.add_node(then_node)
            nodes_created.append(then_node)
        
        # Crear nodo para la acción "sino" (si existe)
        else_node = None
        if else_action:
            else_node = ProcessNode(self._get_next_node_id(), else_action)
            self.diagram.add_node(else_node)
            nodes_created.append(else_node)
        
        # Configurar las ramas
        if then_action and else_action:
            decision_node.set_branches(then_node, else_node)
        elif then_action:
            decision_node.set_branches(then_node)
        
        return nodes_created
    
    def _parse_loop(self, match, line: str) -> List[Any]:
        """Parsea una estructura de bucle (while)"""
        groups = match.groups()
        condition = groups[0] if groups[0] else ""
        action = groups[1] if len(groups) > 1 and groups[1] else ""
        
        # Crear nodo de decisión para el bucle
        loop_node = DecisionNode(self._get_next_node_id(), condition)
        self.diagram.add_node(loop_node)
        
        nodes_created = [loop_node]
        
        # Crear nodo de acción del bucle
        if action:
            action_node = ProcessNode(self._get_next_node_id(), action)
            self.diagram.add_node(action_node)
            nodes_created.append(action_node)
            
            # Conectar: decisión -> acción -> decisión (bucle)
            loop_node.add_connection(action_node, "Sí")
            action_node.add_connection(loop_node)
        
        return nodes_created
    
    def _parse_input_output(self, match, line: str) -> List[Any]:
        """Parsea operaciones de entrada/salida"""
        groups = match.groups()
        text = groups[0] if groups[0] else line
        
        # Determinar si es entrada o salida
        is_input = any(keyword in line.lower() for keyword in self.rules.input_keywords)
        
        io_node = InputOutputNode(self._get_next_node_id(), text, is_input)
        self.diagram.add_node(io_node)
        
        return [io_node]
    
    def _parse_process(self, match, line: str) -> List[Any]:
        """Parsea un proceso general"""
        groups = match.groups()
        text = groups[0] if groups[0] else line
        
        process_node = ProcessNode(self._get_next_node_id(), text)
        self.diagram.add_node(process_node)
        
        return [process_node]
    
    def _parse_start(self, match, line: str) -> List[Any]:
        """Parsea un nodo de inicio explícito - retorna vacío si ya existe uno automático"""
        # Si ya hay un nodo de inicio automático, no crear otro
        start_nodes = [node for node in self.diagram.nodes if hasattr(node, 'type') and node.type == 'start']
        if start_nodes:
            # Actualizar el texto del nodo existente para usar mayúsculas
            start_nodes[0].text = self.rules.get_start_text()
            return []  # No crear nuevo nodo
        
        # Si no hay nodo de inicio, crear uno
        start_node = StartNode(self._get_next_node_id(), self.rules.get_start_text())
        self.diagram.add_node(start_node)
        return [start_node]
    
    def _parse_end(self, match, line: str) -> List[Any]:
        """Parsea un nodo de fin"""
        end_node = EndNode(self._get_next_node_id(), self.rules.get_end_text())
        self.diagram.add_node(end_node)
        
        return [end_node]
    
    def _parse_generic_process(self, line: str) -> List[Any]:
        """Parsea cualquier línea como un proceso genérico"""
        # Limpiar la línea
        text = line.rstrip('.')
        
        process_node = ProcessNode(self._get_next_node_id(), text)
        self.diagram.add_node(process_node)
        
        return [process_node]
    
    def _get_next_node_id(self) -> str:
        """Genera el siguiente ID de nodo"""
        self._node_counter += 1
        return f"node_{self._node_counter}"
    
    def get_diagram(self) -> Optional[FlowDiagram]:
        """Retorna el diagrama creado"""
        return self.diagram
