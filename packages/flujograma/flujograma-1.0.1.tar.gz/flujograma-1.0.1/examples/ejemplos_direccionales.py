import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flujograma.diagrams_api import Diagram, ELB, EC2, RDS, S3


# Ejemplo 1: Flujo básico hacia la derecha
print("\n1️ Ejemplo básico (solo >>):")
with Diagram("Ejemplo 1 - Flujo Derecha", show=False, filename="ejemplo1_derecha.png"):
    ELB("load-balancer") >> EC2("app-server") >> RDS("database") >> S3("backup")

print("  ejemplo1_derecha.png - Todas las flechas apuntan hacia la derecha →")

# Ejemplo 2: Flujo con feedback (usando <<)
print("\n2️ Ejemplo con feedback (>> y <<):")
with Diagram("Ejemplo 2 - Con Feedback", show=False, filename="ejemplo2_feedback.png"):
    # Fila 1: Flujo principal
    ELB("api-gateway") >> EC2("auth-service") >> RDS("user-db") >> S3("backups")
    # Fila 2: Con feedback usando flecha izquierda
    ELB("api-gateway") >> EC2("cache-service") >> RDS("user-db") << EC2("cache-service")

print(" ejemplo2_feedback.png - 2 filas: flujo normal + feedback con <<")

# Ejemplo 3: Arquitectura compleja mixta
print("\n3️ Ejemplo complejo (múltiples direcciones):")
with Diagram("Ejemplo 3 - Arquitectura Mixta", show=False, filename="ejemplo3_mixto.png"):
    # Fila 1: Flujo principal hacia la derecha
    ELB("lb") >> EC2("frontend") >> EC2("backend") >> RDS("main-db")
    # Fila 2: Analytics con flujo hacia la izquierda
    ELB("lb") >> EC2("analytics") >> RDS("main-db") << EC2("analytics")
    # Fila 3: Notificaciones
    ELB("lb") >> EC2("notification") >> EC2("backend") >> S3("files")

print(" ejemplo3_mixto.png - 3 filas con múltiples direcciones: analytics ← main-db")

# Ejemplo 4: Microservicios bidireccionales
print("\n4️ Ejemplo microservicios:")
with Diagram("Ejemplo 4 - Microservicios", show=False, filename="ejemplo4_microservicios.png"):
    # Fila 1: Servicio de usuarios
    ELB("api-gateway") >> EC2("user-service") >> RDS("user-data") >> S3("user-files")
    # Fila 2: Servicio de órdenes que consulta usuarios (flecha izquierda)
    ELB("api-gateway") >> EC2("order-service") >> EC2("user-service") << EC2("order-service")

print(" ejemplo4_microservicios.png - 2 filas: user-service ← order-service (comunicación entre microservicios)")

# Ejemplo 5: Pipeline de datos
print("\n5️ Ejemplo pipeline de datos:")
with Diagram("Ejemplo 5 - Data Pipeline", show=False, filename="ejemplo5_pipeline.png"):
    # Fila 1: Ingesta de datos
    S3("raw-data") >> EC2("processor") >> RDS("clean-data") >> S3("archive")
    # Fila 2: Análisis y reporting  
    S3("raw-data") >> EC2("analytics") >> RDS("reports-db") >> S3("reports")
    # Fila 3: Monitoreo
    S3("raw-data") >> EC2("monitor") >> EC2("alert-system") >> S3("logs")

print("    ejemplo5_pipeline.png - 3 filas de pipeline de datos")
