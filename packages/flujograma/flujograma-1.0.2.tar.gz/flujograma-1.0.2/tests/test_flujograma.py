"""
Pruebas unitarias para el generador de diagramas de flujo
"""

import unittest
import sys
import os

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flujograma.core.parser import FlowParser
from flujograma.core.diagram import FlowDiagram
from flujograma.core.ast_nodes import NodeType, StartNode, EndNode, ProcessNode, DecisionNode
from flujograma.languages.es import SpanishRules
from flujograma.languages.en import EnglishRules


class TestLanguageRules(unittest.TestCase):
    """Pruebas para las reglas de idiomas"""
    
    def test_spanish_rules(self):
        """Prueba las reglas en español"""
        rules = SpanishRules()
        
        self.assertIsInstance(rules.get_conditional_patterns(), list)
        self.assertIsInstance(rules.get_loop_patterns(), list)
        self.assertEqual(rules.get_start_text(), "INICIO")
        self.assertEqual(rules.get_end_text(), "FIN")
        self.assertIn("leer", rules.get_input_keywords())
        self.assertIn("imprimir", rules.get_output_keywords())
    
    def test_english_rules(self):
        """Prueba las reglas en inglés"""
        rules = EnglishRules()
        
        self.assertIsInstance(rules.get_conditional_patterns(), list)
        self.assertIsInstance(rules.get_loop_patterns(), list)
        self.assertEqual(rules.get_start_text(), "START")
        self.assertEqual(rules.get_end_text(), "END")
        self.assertIn("read", rules.get_input_keywords())
        self.assertIn("print", rules.get_output_keywords())


class TestASTNodes(unittest.TestCase):
    """Pruebas para los nodos del AST"""
    
    def test_start_node(self):
        """Prueba el nodo de inicio"""
        node = StartNode("start1", "Inicio")
        self.assertEqual(node.type, NodeType.START)
        self.assertEqual(node.text, "Inicio")
        self.assertEqual(node.id, "start1")
    
    def test_process_node(self):
        """Prueba el nodo de proceso"""
        node = ProcessNode("proc1", "Calcular suma")
        self.assertEqual(node.type, NodeType.PROCESS)
        self.assertEqual(node.text, "Calcular suma")
    
    def test_decision_node(self):
        """Prueba el nodo de decisión"""
        node = DecisionNode("dec1", "x > 5")
        self.assertEqual(node.type, NodeType.DECISION)
        self.assertEqual(node.condition, "x > 5")
    
    def test_node_connections(self):
        """Prueba las conexiones entre nodos"""
        node1 = ProcessNode("proc1", "Proceso 1")
        node2 = ProcessNode("proc2", "Proceso 2")
        
        connection = node1.add_connection(node2, "siguiente")
        
        self.assertEqual(len(node1.connections), 1)
        self.assertEqual(connection.source, node1)
        self.assertEqual(connection.target, node2)
        self.assertEqual(connection.label, "siguiente")


class TestFlowDiagram(unittest.TestCase):
    """Pruebas para el diagrama de flujo"""
    
    def setUp(self):
        """Configuración para cada prueba"""
        self.diagram = FlowDiagram("Test Diagram")
    
    def test_empty_diagram(self):
        """Prueba diagrama vacío"""
        self.assertEqual(len(self.diagram.nodes), 0)
        self.assertEqual(self.diagram.title, "Test Diagram")
    
    def test_add_nodes(self):
        """Prueba añadir nodos"""
        start = StartNode("start", "Inicio")
        process = ProcessNode("proc", "Proceso")
        end = EndNode("end", "Fin")
        
        self.diagram.add_node(start)
        self.diagram.add_node(process)
        self.diagram.add_node(end)
        
        self.assertEqual(len(self.diagram.nodes), 3)
        self.assertEqual(self.diagram.start_node, start)
        self.assertIn(end, self.diagram.end_nodes)
    
    def test_node_lookup(self):
        """Prueba búsqueda de nodos"""
        node = ProcessNode("test123", "Test Process")
        self.diagram.add_node(node)
        
        found = self.diagram.get_node_by_id("test123")
        self.assertEqual(found, node)
        
        not_found = self.diagram.get_node_by_id("nonexistent")
        self.assertIsNone(not_found)
    
    def test_diagram_validation(self):
        """Prueba validación del diagrama"""
        # Diagrama vacío debería tener errores
        errors = self.diagram.validate()
        self.assertGreater(len(errors), 0)
        
        # Diagrama con inicio y fin no debería tener errores
        start = StartNode("start", "Inicio")
        end = EndNode("end", "Fin")
        self.diagram.add_node(start)
        self.diagram.add_node(end)
        start.add_connection(end)
        
        errors = self.diagram.validate()
        self.assertEqual(len(errors), 0)


class TestFlowParser(unittest.TestCase):
    """Pruebas para el parser"""
    
    def test_spanish_parser(self):
        """Prueba el parser en español"""
        parser = FlowParser("es")
        self.assertEqual(parser.language, "es")
        self.assertIsNotNone(parser.rules)
    
    def test_english_parser(self):
        """Prueba el parser en inglés"""
        parser = FlowParser("en")
        self.assertEqual(parser.language, "en")
        self.assertIsNotNone(parser.rules)
    
    def test_invalid_language(self):
        """Prueba idioma inválido"""
        with self.assertRaises(ValueError):
            FlowParser("fr")  # Francés no soportado
    
    def test_simple_parse_spanish(self):
        """Prueba parsing simple en español"""
        parser = FlowParser("es")
        text = "Imprimir hola mundo"
        
        diagram = parser.parse(text)
        
        self.assertIsNotNone(diagram)
        self.assertGreater(len(diagram.nodes), 0)
        self.assertIsNotNone(diagram.start_node)
    
    def test_conditional_parse_spanish(self):
        """Prueba parsing de condicional en español"""
        parser = FlowParser("es")
        text = "Si x es mayor a 5, entonces imprimir mensaje sino incrementar contador"
        
        diagram = parser.parse(text)
        
        # Debería haber nodos de decisión
        decision_nodes = [n for n in diagram.nodes if n.type == NodeType.DECISION]
        self.assertGreater(len(decision_nodes), 0)
    
    def test_loop_parse_spanish(self):
        """Prueba parsing de bucle en español"""
        parser = FlowParser("es")
        text = "Mientras contador sea menor a 10, incrementar contador"
        
        diagram = parser.parse(text)
        
        # Debería haber nodos de decisión (para el bucle)
        decision_nodes = [n for n in diagram.nodes if n.type == NodeType.DECISION]
        self.assertGreater(len(decision_nodes), 0)


class TestIntegration(unittest.TestCase):
    """Pruebas de integración"""
    
    def test_full_workflow_spanish(self):
        """Prueba flujo completo en español"""
        from flujograma import parse_text, get_diagram_stats
        
        text = """
        Leer número del usuario.
        Si número es mayor a 0, entonces calcular factorial sino mostrar error.
        Imprimir resultado.
        """
        
        # Parsear
        diagram = parse_text(text, "es")
        self.assertIsNotNone(diagram)
        
        # Obtener estadísticas
        stats = get_diagram_stats(text, "es")
        self.assertIsInstance(stats, dict)
        self.assertIn("total_nodes", stats)
        self.assertGreater(stats["total_nodes"], 0)
    
    def test_full_workflow_english(self):
        """Prueba flujo completo en inglés"""
        from flujograma import parse_text
        
        text = """
        Read user input.
        If input is valid, then process data else show error.
        Display results.
        """
        
        diagram = parse_text(text, "en")
        self.assertIsNotNone(diagram)
        self.assertEqual(diagram.start_node.text, "START")


if __name__ == "__main__":
    print("🧪 Ejecutando pruebas del Flujograma...")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    unittest.main(verbosity=2)
