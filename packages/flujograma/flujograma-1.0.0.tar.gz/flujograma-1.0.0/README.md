# Flujograma

Una librería Python profesional para crear diagramas de arquitectura y flujo con iconos profesionales. Alternativa offline a diagrams.mingrammer.com con soporte completo para AWS, GCP, Kubernetes y más.

## 🚀 Características

- **🔒 100% Offline**: No requiere conexión a internet ni servicios de IA
- **⚡ Ligero**: Sin dependencias pesadas como GraphViz, solo Pillow y Lark
- **🌍 Multiidioma**: Soporte para español, inglés y fácil extensión a otros idiomas
- **🎯 Lenguaje controlado**: Basado en gramáticas simples, no IA completa
- **☁️ Diagramas de arquitectura**: Compatible con diagrams.mingrammer.com para crear diagramas de infraestructura cloud
- **🎨 Iconos profesionales**: Soporte para iconos PNG de AWS, GCP, Kubernetes con fallback automático
- **📐 Layout inteligente**: Detección automática de filas múltiples y flechas direccionales

## 📦 Instalación

### Desde PyPI (Recomendado)
```bash
pip install flujograma
```

### Desde código fuente
```bash
git clone https://github.com/tuusuario/flujograma.git
cd flujograma
pip install -e .
```

### Dependencias del sistema
```bash
# Solo requiere Python 3.8+ y las siguientes dependencias:
# Pillow>=9.0.0 - Para procesamiento de imágenes
# lark>=1.1.0 - Para parsing de gramáticas
```

## 🎯 Uso básico

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

### 🏗️ Diagramas de arquitectura web (Web Services)
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

**🔧 Operadores disponibles:**
- `>>` : Flecha hacia la derecha →
- `<<` : Flecha hacia la izquierda ←

**☁️ Componentes AWS:**
- `ELB("nombre")` : Load Balancer (púrpura)
- `EC2("nombre")` : Servidor/Aplicación (naranja)  
- `RDS("nombre")` : Base de datos (azul)
- `S3("nombre")` : Almacenamiento (verde)

## 📝 Sintaxis soportada

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

## 🏗️ Estructura del proyecto

```
flujograma/
├── src/
│   └── flujograma/
│       ├── core/           # Lógica principal
│       ├── languages/      # Soporte multiidioma
│       ├── renderers/      # Generadores de salida
│       └── assets/         # Iconos y recursos
├── tests/                  # Pruebas unitarias
├── examples/              # Ejemplos de uso
├── requirements.txt       # Dependencias principales
├── requirements-dev.txt   # Dependencias de desarrollo
├── pyproject.toml         # Configuración del proyecto
└── README.md             # Este archivo
```

## 🚀 Ejemplos de uso

### Ejemplo 1: Login de usuario
```python
from flujograma import generate_diagram

text = """
Inicio.
Leer usuario y contraseña.
Si las credenciales son válidas, entonces mostrar dashboard sino mostrar error.
Fin.
"""

generate_diagram(text, "es", "login.png")
```

### Ejemplo 2: Calculadora
```python
text = """
Inicio.
Leer dos números y operación.
Si operación es suma, entonces calcular a + b.
Si operación es resta, entonces calcular a - b.
Si operación es multiplicación, entonces calcular a * b.
Si operación es división y b no es cero, entonces calcular a / b sino mostrar error.
Mostrar resultado.
Fin.
"""

generate_diagram(text, "es", "calculadora.png")
```

### Ejemplo 3: Arquitectura web
```python
from src.flujograma.diagrams_api import Diagram, ELB, EC2, RDS, S3

with Diagram("E-commerce Platform", filename="ecommerce.png"):
    # Frontend tier
    ELB("Load Balancer") >> EC2("Web Frontend") >> S3("Static Assets")
    
    # Backend tier  
    ELB("Load Balancer") >> EC2("API Server") >> RDS("User Database")
    EC2("API Server") >> RDS("Product Database")
    
    # Analytics tier
    EC2("API Server") >> EC2("Analytics") >> RDS("Analytics DB")
```

## 🧪 Ejecutar tests

### Instalar dependencias de desarrollo
```bash
pip install -r requirements-dev.txt
```

### Ejecutar todas las pruebas
```bash
pytest tests/ -v
```

### Ejecutar con cobertura de código
```bash
pytest tests/ --cov=src/flujograma --cov-report=html
```

### Ejecutar tests específicos
```bash
# Solo pruebas de parsers
pytest tests/test_flujograma.py::TestFlowParser -v

# Solo pruebas de nodos AST
pytest tests/test_flujograma.py::TestASTNodes -v

# Solo pruebas de integración
pytest tests/test_flujograma.py::TestIntegration -v
```

## 🛠️ Desarrollo

### Configurar entorno de desarrollo
```bash
# Clonar repositorio
git clone https://github.com/tuusuario/flujograma.git
cd flujograma

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar en modo desarrollo
pip install -e .
pip install -r requirements-dev.txt
```

### Ejecutar ejemplos
```bash
# Ejemplos básicos
python examples/ejemplo_1_login.py
python examples/ejemplo_2_calculadora.py

# Ejemplos de arquitectura
python examples/ejemplos-seb-service.py
python examples/ejemplos_direccionales.py
```

### Scripts avanzados

#### Generar diagramas en lote
```python
import os
from flujograma import generate_diagram

examples_dir = "examples"
for filename in os.listdir(examples_dir):
    if filename.endswith('.py'):
        # Procesar archivo de ejemplo
        with open(os.path.join(examples_dir, filename), 'r') as f:
            content = f.read()
            # Extraer texto del diagrama y generar
            # (lógica personalizada según formato)
```

#### Validar sintaxis
```python
from flujograma.core.parser import FlowParser

parser = FlowParser("es")
text = "Si x > 5, entonces imprimir mensaje"

try:
    diagram = parser.parse(text)
    print("✅ Sintaxis válida")
    print(f"Nodos generados: {len(diagram.nodes)}")
except Exception as e:
    print(f"❌ Error de sintaxis: {e}")
```

## 📊 Estadísticas del proyecto

- **Líneas de código**: ~2,500
- **Tests**: 18 pruebas unitarias
- **Cobertura**: >85%
- **Dependencias**: Solo 2 (Pillow, Lark)
- **Tamaño del paquete**: <50KB

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆚 Comparación con alternativas

| Característica | Flujograma | diagrams.mingrammer.com | Graphviz | Draw.io |
|---------------|------------|-------------------------|----------|---------|
| **Offline** | ✅ | ❌ | ✅ | ❌ |
| **Dependencias ligeras** | ✅ | ❌ | ❌ | N/A |
| **Texto a diagrama** | ✅ | ❌ | ❌ | ❌ |
| **Iconos profesionales** | ✅ | ✅ | ❌ | ✅ |
| **Multi-idioma** | ✅ | ❌ | ❌ | ✅ |
| **API Python** | ✅ | ✅ | ❌ | ❌ |

## 📞 Soporte

- **GitHub Issues**: Para reportar bugs o solicitar features
- **Email**: tu.email@ejemplo.com
- **Documentación**: Ver carpeta `examples/` para más casos de uso

---

**¡Gracias por usar Flujograma! 🎉**

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
