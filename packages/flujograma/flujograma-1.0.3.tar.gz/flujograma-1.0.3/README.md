# Flujograma

<div align="center">

![Pillow](https://img.shields.io/badge/dependency-Pillow%20%E2%89%A5%209.0.0-orange)
![Lark](https://img.shields.io/badge/dependency-Lark%20%E2%89%A5%201.1.0-green)

</div>

Una librería Python para generar diagramas automáticamente a partir de texto en lenguaje controlado.


## Características

-  **100% Offline**: No requiere conexión a internet ni servicios de IA
-  **Ligero**: Sin dependencias pesadas como GraphViz o herramientas externas
-  **Multiidioma**: Soporte para español, inglés y fácil extensión a otros idiomas
-  **Lenguaje controlado**: Basado en gramáticas simples, no IA completa
-  **Diagramas de arquitectura**: Soporte experimental para diagramas de infraestructura

## Instalación

```bash
pip install flujograma
```

## Uso básico

### Diagramas de flujo tradicionales
```python
from flujograma import generate_diagram

# Generar diagrama en español
generate_diagram(
    text="Si la variable es mayor a 5, entonces imprimir mensaje sino incrementar contador",
    language="es",
    filename="mi_diagrama.png"
)

# Generar diagrama en inglés
generate_diagram(
    text="If variable is greater than 5, then print message else increment counter",
    language="en", 
    filename="my_diagram.png"
)
```

### Diagramas de arquitectura web (Web Services) - EXPERIMENTAL
```python
from src.flujograma.diagrams_api import Diagram, ELB, EC2, RDS, S3

# Crear arquitectura básica
with Diagram("Mi Arquitectura", filename="arquitectura.png"):
    ELB("load-balancer") >> EC2("web-server") >> RDS("database") >> S3("storage")

# Arquitectura con múltiples filas y flechas direccionales
with Diagram("Sistema Complejo", filename="sistema.png"):
    # Fila 1: Flujo principal
    ELB("lb") >> EC2("frontend") >> RDS("main-db") >> S3("files")
    # Fila 2: Con feedback (flecha izquierda ←)
    ELB("lb") >> EC2("cache") >> RDS("main-db") << EC2("analytics")
    # Fila 3: Servicios auxiliares
    ELB("lb") >> EC2("api") >> RDS("logs-db")
```

**Operadores disponibles:**
- `>>` : Flecha hacia la derecha →
- `<<` : Flecha hacia la izquierda ←

**Componentes AWS:**
- `ELB("nombre")` : Load Balancer (púrpura)
- `EC2("nombre")` : Servidor/Aplicación (naranja)  
- `RDS("nombre")` : Base de datos (azul)
- `S3("nombre")` : Almacenamiento (verde)

## Sintaxis soportada

### Español
- `Si [condición], entonces [acción]`
- `Si [condición], entonces [acción] sino [acción]`
- `Mientras [condición], [acción]`
- `Para cada [elemento] en [lista], [acción]`
- `Inicio` / `Fin`

### Inglés
- `If [condition], then [action]`
- `If [condition], then [action] else [action]`
- `While [condition], [action]`
- `For each [element] in [list], [action]`
- `Start` / `End`

## Estructura del proyecto

```
flujograma/
├── src/
│   └── flujograma/
│       ├── core/           # Lógica principal
│       ├── languages/      # Soporte multiidioma
│       └── renderers/      # Generadores de salida
├── tests/                  # Pruebas unitarias
├── examples/              # Ejemplos de uso
└── docs/                  # Documentación
```

## Desarrollo

```bash
# Clonar repositorio
git clone https://github.com/CubeFreaKLab/flujograma.git
cd flujograma

# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Ejecutar pruebas
pytest

## Licencia

MIT License
