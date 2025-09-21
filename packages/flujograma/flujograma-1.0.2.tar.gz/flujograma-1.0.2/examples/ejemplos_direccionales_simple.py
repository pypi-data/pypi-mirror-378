from flujograma.diagrams_api import Diagram, ELB, EC2, RDS, S3

# Ejemplo 1: Flujo básico hacia la derecha
with Diagram("Ejemplo 1 - Flujo Derecha", show=False, filename="ejemplo1_derecha.png"):
    ELB("load-balancer") >> EC2("app-server") >> RDS("database") >> S3("backup")

# Ejemplo 2: Flujo con feedback (usando <<)
with Diagram("Ejemplo 2 - Con Feedback", show=False, filename="ejemplo2_feedback.png"):
    # Fila 1: Flujo principal
    ELB("api-gateway") >> EC2("auth-service") >> RDS("user-db") >> S3("backups")
    # Fila 2: Con feedback usando flecha izquierda
    ELB("api-gateway") >> EC2("cache-service") >> RDS("user-db") << EC2("cache-service")

# Ejemplo 3: Flujo complejo mixto
with Diagram("Ejemplo 3 - Mixto", show=False, filename="ejemplo3_mixto.png"):
    # Fila 1: Flujo principal hacia la derecha
    ELB("load-balancer") >> EC2("web-server") >> RDS("main-db") >> S3("files")
    # Fila 2: Con doble dirección
    EC2("analytics") << RDS("main-db") >> EC2("reports")
    # Fila 3: Servicios auxiliares  
    EC2("monitor") >> EC2("alerting") >> S3("logs")

# Ejemplo 4: Microservicios bidireccionales
with Diagram("Ejemplo 4 - Microservicios", show=False, filename="ejemplo4_microservicios.png"):
    # Fila 1: Flujo normal
    ELB("api-gateway") >> EC2("user-service") >> RDS("users")
    # Fila 2: Comunicación entre servicios  
    EC2("order-service") << EC2("user-service") >> RDS("orders")

# Ejemplo 5: Pipeline de datos con múltiples direcciones
with Diagram("Ejemplo 5 - Pipeline", show=False, filename="ejemplo5_pipeline.png"):
    # Fila 1: Ingesta
    S3("raw-data") >> EC2("processor") >> RDS("clean-data")
    # Fila 2: Análisis  
    RDS("clean-data") >> EC2("analytics") >> S3("reports")
    # Fila 3: Monitoreo
    EC2("processor") << EC2("monitor")
    EC2("analytics") << EC2("monitor") >> S3("metrics")