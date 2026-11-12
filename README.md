# 📊 Proyecto 8: Calculadora de Métricas de Complejidad con Enfoque Funcional

## 📋 Descripción del Proyecto

Sistema funcional para analizar código fuente y calcular métricas de complejidad (ciclomática, cognitiva, Halstead), utilizando AST parsing funcional, análisis de grafos y generación de reportes.

**Universidad de Colima - Ingeniería en Computación Inteligente**  
**Materia**: Programación Funcional  
**Profesor**: Gonzalez Zepeda Sebastian  
**Semestre**: Agosto 2025 - Enero 2026

---

## 🎯 Objetivos 

- Implementar **parsers funcionales** para análisis de código
- Desarrollar **calculadores de métricas** mediante funciones puras
- Aplicar **análisis de grafos** funcional para control flow
- Crear **reportes** mediante transformaciones composables
- Utilizar **pattern matching** para análisis sintáctico
- Practicar **recursión** sobre AST (Abstract Syntax Trees)

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje**: Python 3.11+
- **Paradigma**: Programación Funcional
- **Librerías**:
  - `ast` - Abstract Syntax Trees
  - `radon` - Métricas de complejidad
  - `networkx` - Grafos de flujo de control
  - `toolz` - Utilidades funcionales
  - `jinja2` - Templates para reportes

---

## 📦 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/complexity-analyzer.git
cd complexity-analyzer

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### requirements.txt
```
radon>=6.0.0
networkx>=3.2.0
toolz>=0.12.0
jinja2>=3.1.0
graphviz>=0.20.0
pandas>=2.0.0
matplotlib>=3.7.0
```

---

## 🚀 Uso del Sistema

```python
from src.analyzer import CodeAnalyzer
from src.metrics import cyclomatic, cognitive, halstead

# Analizar archivo
analyzer = CodeAnalyzer('path/to/code.py')

# Calcular métricas funcionales
metrics = analyzer.calculate(
    cyclomatic_complexity,
    cognitive_complexity,
    halstead_metrics,
    maintainability_index
)

# Generar reporte
report = analyzer.generate_report(
    format='html',
    include_graphs=True,
    threshold_warnings=True
)

print(f"Complejidad Ciclomática: {metrics['cyclomatic']}")
print(f"Índice de Mantenibilidad: {metrics['maintainability']}")
```

---

## 📂 Estructura del Proyecto

```
complexity-analyzer/
├── src/
│   ├── __init__.py
│   ├── analyzer.py         # Analizador principal
│   ├── parser.py           # Parser funcional de AST
│   ├── metrics/
│   │   ├── cyclomatic.py   # Complejidad ciclomática
│   │   ├── cognitive.py    # Complejidad cognitiva
│   │   ├── halstead.py     # Métricas de Halstead
│   │   └── maintainability.py  # Índice de mantenibilidad
│   ├── graph.py            # Control flow graphs
│   ├── visitors.py         # AST visitors funcionales
│   └── reports.py          # Generación de reportes
├── tests/
│   ├── test_cyclomatic.py
│   ├── test_cognitive.py
│   └── test_integration.py
├── examples/
│   ├── analyze_project.py
│   └── batch_analysis.py
├── templates/
│   ├── report.html
│   └── dashboard.html
├── docs/
│   ├── metrics_reference.md
│   └── api_documentation.md
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🔑 Características Principales

### 1. Parser Funcional de AST
```python
import ast
from typing import Callable, Any, List
from dataclasses import dataclass

@dataclass(frozen=True)
class ASTNode:
    """Nodo del AST inmutable"""
    node_type: str
    children: tuple
    attributes: dict
    
    @staticmethod
    def from_ast(node: ast.AST) -> 'ASTNode':
        """Convertir ast.AST a ASTNode inmutable"""
        return ASTNode(
            node_type=type(node).__name__,
            children=tuple(
                ASTNode.from_ast(child) 
                for child in ast.iter_child_nodes(node)
            ),
            attributes={
                k: v for k, v in node.__dict__.items()
                if not k.startswith('_')
            }
        )
    
    def fold(self, 
             leaf_fn: Callable[[str, dict], Any],
             branch_fn: Callable[[str, dict, List[Any]], Any]) -> Any:
        """Fold funcional sobre el árbol"""
        if not self.children:
            return leaf_fn(self.node_type, self.attributes)
        
        children_results = [
            child.fold(leaf_fn, branch_fn)
            for child in self.children
        ]
        return branch_fn(self.node_type, self.attributes, children_results)

def parse_code(source_code: str) -> ASTNode:
    """Parser funcional de código"""
    tree = ast.parse(source_code)
    return ASTNode.from_ast(tree)
```

### 2. Complejidad Ciclomática Funcional
```python
from typing import Set

def cyclomatic_complexity(ast_node: ASTNode) -> int:
    """
    Calcular complejidad ciclomática funcionalmente.
    CC = E - N + 2P donde:
    E = edges, N = nodes, P = connected components
    """
    decision_nodes = {
        'If', 'While', 'For', 'ExceptHandler',
        'With', 'Assert', 'BoolOp'
    }
    
    def count_decisions(node_type: str, attrs: dict) -> int:
        return 1 if node_type in decision_nodes else 0
    
    def sum_children(node_type: str, attrs: dict, children: List[int]) -> int:
        current = count_decisions(node_type, attrs)
        return current + sum(children)
    
    decisions = ast_node.fold(count_decisions, sum_children)
    return decisions + 1  # Base complexity

def calculate_per_function(ast_node: ASTNode) -> dict:
    """Calcular complejidad por función"""
    functions = {}
    
    def extract_function(node: ASTNode) -> dict:
        if node.node_type == 'FunctionDef':
            name = node.attributes.get('name', 'unknown')
            complexity = cyclomatic_complexity(node)
            functions[name] = complexity
        
        for child in node.children:
            extract_function(child)
        
        return functions
    
    return extract_function(ast_node)
```

### 3. Complejidad Cognitiva Funcional
```python
def cognitive_complexity(ast_node: ASTNode, nesting_level: int = 0) -> int:
    """
    Complejidad cognitiva según SonarSource.
    Penaliza anidamiento y estructuras complejas.
    """
    increment_nodes = {
        'If': lambda: 1 + nesting_level,
        'While': lambda: 1 + nesting_level,
        'For': lambda: 1 + nesting_level,
        'ExceptHandler': lambda: 1 + nesting_level,
        'BoolOp': lambda: 1,  # and, or
    }
    
    nested_structures = {'If', 'While', 'For', 'ExceptHandler', 'With'}
    
    def calculate(node: ASTNode, level: int) -> int:
        complexity = 0
        
        # Incremento base
        if node.node_type in increment_nodes:
            complexity += increment_nodes[node.node_type]()
        
        # Recursión con nuevo nivel de anidamiento
        new_level = level + 1 if node.node_type in nested_structures else level
        
        for child in node.children:
            complexity += calculate(child, new_level)
        
        return complexity
    
    return calculate(ast_node, nesting_level)
```

### 4. Métricas de Halstead
```python
from collections import Counter
from math import log2

@dataclass(frozen=True)
class HalsteadMetrics:
    """Métricas de Halstead"""
    n1: int  # Operadores únicos
    n2: int  # Operandos únicos
    N1: int  # Total operadores
    N2: int  # Total operandos
    
    @property
    def vocabulary(self) -> int:
        """n = n1 + n2"""
        return self.n1 + self.n2
    
    @property
    def length(self) -> int:
        """N = N1 + N2"""
        return self.N1 + self.N2
    
    @property
    def calculated_length(self) -> float:
        """N̂ = n1*log2(n1) + n2*log2(n2)"""
        if self.n1 == 0 or self.n2 == 0:
            return 0
        return self.n1 * log2(self.n1) + self.n2 * log2(self.n2)
    
    @property
    def volume(self) -> float:
        """V = N * log2(n)"""
        if self.vocabulary == 0:
            return 0
        return self.length * log2(self.vocabulary)
    
    @property
    def difficulty(self) -> float:
        """D = (n1/2) * (N2/n2)"""
        if self.n2 == 0:
            return 0
        return (self.n1 / 2) * (self.N2 / self.n2)
    
    @property
    def effort(self) -> float:
        """E = D * V"""
        return self.difficulty * self.volume

def calculate_halstead(ast_node: ASTNode) -> HalsteadMetrics:
    """Calcular métricas de Halstead funcionalmente"""
    operators = Counter()
    operands = Counter()
    
    operator_nodes = {'BinOp', 'UnaryOp', 'Compare', 'BoolOp'}
    operand_nodes = {'Name', 'Num', 'Str', 'Constant'}
    
    def count(node: ASTNode):
        if node.node_type in operator_nodes:
            operators[node.node_type] += 1
        elif node.node_type in operand_nodes:
            value = str(node.attributes.get('id') or 
                       node.attributes.get('value', ''))
            operands[value] += 1
        
        for child in node.children:
            count(child)
    
    count(ast_node)
    
    return HalsteadMetrics(
        n1=len(operators),
        n2=len(operands),
        N1=sum(operators.values()),
        N2=sum(operands.values())
    )
```

### 5. Control Flow Graph
```python
import networkx as nx

def build_cfg(ast_node: ASTNode) -> nx.DiGraph:
    """Construir grafo de flujo de control funcionalmente"""
    graph = nx.DiGraph()
    node_counter = [0]  # Mutable para IDs únicos
    
    def add_node() -> int:
        node_id = node_counter[0]
        node_counter[0] += 1
        graph.add_node(node_id)
        return node_id
    
    def process(node: ASTNode, entry: int) -> int:
        """Procesar nodo y retornar ID de salida"""
        if node.node_type == 'If':
            # Nodo de decisión
            condition = add_node()
            graph.add_edge(entry, condition)
            
            # Rama verdadera
            then_entry = add_node()
            graph.add_edge(condition, then_entry, label='True')
            then_exit = process_children(node.children[:1], then_entry)
            
            # Rama falsa
            else_entry = add_node()
            graph.add_edge(condition, else_entry, label='False')
            else_exit = process_children(node.children[1:], else_entry)
            
            # Nodo de unión
            exit_node = add_node()
            graph.add_edge(then_exit, exit_node)
            graph.add_edge(else_exit, exit_node)
            return exit_node
        
        # Nodo simple
        current = add_node()
        graph.add_edge(entry, current)
        return process_children(node.children, current)
    
    def process_children(children: tuple, entry: int) -> int:
        current = entry
        for child in children:
            current = process(child, current)
        return current
    
    entry = add_node()
    process(ast_node, entry)
    return graph
```

---

## 📊 Funcionalidades Implementadas

### Métricas de Código
- ✅ Complejidad Ciclomática
- ✅ Complejidad Cognitiva
- ✅ Métricas de Halstead
- ✅ Índice de Mantenibilidad
- ✅ Profundidad de anidamiento

### Análisis Estructural
- ✅ Control Flow Graphs
- ✅ Call Graphs
- ✅ Dependency Analysis
- ✅ Code Smells detection

### Reportes
- ✅ HTML interactivo
- ✅ PDF ejecutivo
- ✅ JSON para CI/CD
- ✅ Dashboards con gráficos

### Integración
- ✅ CLI tool
- ✅ Pre-commit hooks
- ✅ CI/CD integration
- ✅ IDE plugins

---

## 🧪 Testing

```bash
# Tests
pytest tests/ -v

# Análisis del propio proyecto
python -m src.analyzer src/

# Benchmarks
pytest tests/ -k "benchmark"
```

---

## 📈 Pipeline de Desarrollo

### Semana 1: Parser y Métricas Básicas (30 Oct - 5 Nov)
- AST parsing funcional
- Complejidad ciclomática
- Estructura base

### Semana 2: Métricas Avanzadas (6 Nov - 12 Nov)
- Complejidad cognitiva
- Halstead metrics
- Control flow graphs

### Semana 3: Reportes y Visualización (13 Nov - 19 Nov)
- Generación de reportes
- Visualizaciones
- Dashboard

---

## 💼 Componente de Emprendimiento

**Aplicación Real**: Herramienta de auditoría de código para empresas

**Propuesta de Valor**:
- Evaluación objetiva de calidad de código
- Identificación de deuda técnica
- Priorización de refactoring
- Integración con flujos DevOps

**Modelo de Negocio**: SaaS + Consultoría

---

## 📚 Referencias

- McCabe, T.J. (1976). *A Complexity Measure*
- Halstead, M.H. (1977). *Elements of Software Science*
- **Radon**: https://radon.readthedocs.io/
- **SonarSource Cognitive Complexity**: https://www.sonarsource.com/

---

## 🏆 Criterios de Evaluación

- **Parser Funcional (25%)**: Corrección, elegancia
- **Métricas (30%)**: Precisión, completitud
- **Grafos (20%)**: CFG correcto, visualización
- **Reportes (25%)**: Claridad, utilidad

---

## 👥 Autor

**Nombre**: [Tu Nombre]  
**Email**: [tu-email@ucol.mx]  
**GitHub**: [@tu-usuario](https://github.com/tu-usuario)

---

## 📄 Licencia

Proyecto académico - Universidad de Colima © 2025


edicion 
proyecto

parte 1** análisis de dato del proyecto**

primeramente explicare de que tratara este proyecto,El  tu nivel de complejidad, utilizando ciertas funciones y agregados para analizar los archivos .py, lo canalizará serás tú aceite de forma recursiva y hará un reporte por la función ciclomatica, también utilizaremos el ast y el match para clasificar los nodos de los archivos y comparando los resultados con el método randon

Un AST (Árbol de Sintaxis Abstracta, o Abstract Syntax Tree en inglés) es una representación en forma de árbol de la estructura de tu código fuente.
En lugar de leer el código como una simple línea de texto, el programa lo transforma en una jerarquía de datos donde cada elemento (una variable, una operación, un bucle) es un nodo.

¿Qué es y para qué sirve?

• Simplificación: Omite detalles innecesarios del código original (como paréntesis, puntos y comas o espacios en blanco) y deja solo la lógica pura.
• Traducción a datos: Convierte el texto del código en un objeto que los programas pueden analizar, modificar o transformar.
• Compiladores e intérpretes: Es el paso intermedio tras leer el texto (analizador léxico/sintáctico) antes de generar código de máquina o código intermedio.
• Herramientas de análisis (SAST / Linters): Permiten a herramientas como ESLint, Babel o analizadores de seguridad revisar el código en busca de errores, malas prácticas o vulnerabilidades.

Bien ya que ahora entendimos qué es el ast y por qué lo vamos a utilizar daremos un pequeño detalle otros dos aspectos que vamos a utilizar en este caso funciones de programación funcional orientadas a la separación y clasificación de componentes

 match
En programación funcional, un match (o pattern matching / coincidencia de patrones) es un mecanismo que permite comparar un valor o estructura de datos contra uno o varios patrones para seleccionar una rama de código y, opcionalmente, descomponer (destructurar) el objeto para extraer sus partes internas.

Características principales

* Comparación estructural: No solo evalúa la igualdad de valores simples (como números o textos), sino que verifica la forma, el tipo o la composición interna de estructuras complejas (como listas, árboles o tipos de datos algebraicos).
* Desestructuración: Permite extraer variables directamente de los datos mientras se evalúa el patrón.
* Evaluación como expresión: A diferencia de una instrucción switch tradicional en lenguajes imperativos, un match suele retornar un valor (es una expresión).
* Patrón comodín (wildcard): Se utiliza un símbolo (como _) para capturar cualquier otro caso que no haya coincidido con los patrones anteriores.

 radon
Radon es una librería de Python que sirve para analizar el código fuente y calcular métricas de calidad y complejidad. Se utiliza principalmente para detectar bloques de código difíciles de leer o mantener y facilitar la refactorización.

Funciones y métricas principales

Puedes usar Radon desde la línea de comandos o integrarla en flujos de trabajo (como CI/CD o linters) para obtener cuatro tipos de análisis:
* Complejidad ciclomática (cc). Cuenta el número de caminos independientes o puntos de decisión (como bucles for o condicionales if) en una función. Califica el código con letras de la A (muy simple) a la F (muy complejo y propenso a errores).
* Índice de mantenibilidad (mi). Calcula una puntuación del 0 al 100 que indica qué tan fácil es mantener un archivo. Combina la complejidad ciclomática, el volumen de código y las líneas de comentarios.
* Métricas sin procesar (raw). Cuenta datos básicos del archivo, como el total de líneas de código (LOC), líneas lógicas (LLOC), comentarios y espacios en blanco.
* Métricas de Halstead (hal). Evalúa la complejidad basándose en la cantidad de operadores (palabras clave, símbolos) y operandos (variables, valores) para estimar el esfuerzo de desarrollo y posibles errores.

import ast
from dataclasses import dataclass
from typing import List

@dataclass
class FunctionMetrics:
    name: str
    cyclomatic_complexity: int
    lines: int
    max_nesting_depth: int

def analizar_archivo_py(ruta_archivo: str) -> List[FunctionMetrics]:
    """Lee un archivo .py, analiza su AST y extrae métricas por función."""
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    tree = ast.parse(contenido)
    resultados = []

    # Recorremos el árbol buscando definiciones de funciones (normales o asíncronas)
    for nodo in ast.walk(tree):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            resultados.append(calcular_metricas_funcion(nodo))
            
    return resultados

def calcular_metricas_funcion(func_node: ast.FunctionDef) -> FunctionMetrics:
    nombre = func_node.name
    
    # Cálculo de líneas de código físicas de la función
    inicio = func_node.lineno
    fin = getattr(func_node, 'end_lineno', inicio)
    lineas = (fin - inicio) + 1
    
    cc = 1  # Complejidad ciclomática base
    max_profundidad = 0

    # Función recursiva interna para recorrer el AST usando 'match'
    def recorrer_nodos(nodo: ast.AST, profundidad_actual: int = 0):
        nonlocal cc, max_profundidad
        
        if profundidad_actual > max_profundidad:
            max_profundidad = profundidad_actual

        for hijo in ast.iter_child_nodes(nodo):
            # Clasificación de nodos usando pattern matching (match-case)
            match hijo:
                case ast.If() | ast.While() | ast.For() | ast.AsyncFor() | ast.ExceptHandler():
                    cc += 1
                    # Estructuras de control que incrementan el anidamiento
                    recorrer_nodos(hijo, profundidad_actual + 1)
                    
                case ast.BoolOp():
                    # Operadores booleanos (and / or) añaden complejidad
                    cc += len(hijo.values) - 1
                    recorrer_nodos(hijo, profundidad_actual)
                    
                case ast.Match():
                    # Estructuras match-case (Python 3.10+)
                    cc += len(hijo.cases)
                    recorrer_nodos(hijo, profundidad_actual + 1)
                    
                case ast.FunctionDef() | ast.ClassDef():
                    # Evitamos descender a funciones o clases internas anidadas en el mismo scope por simplicidad
                    continue
                    
                case _:
                    # Cualquier otro nodo genérico que no altera directamente la CC
                    recorrer_nodos(hijo, profundidad_actual)

    recorrer_nodos(func_node, profundidad_actual=0)

    return FunctionMetrics(
        name=nombre,
        cyclomatic_complexity=cc,
        lines=lineas,
        max_nesting_depth=max_profundidad
    )

# ==========================================
# Ejemplo de uso y prueba local
# ==========================================
if __name__ == "__main__":
    import tempfile
    import os

    # Creamos un archivo de prueba temporal con código de ejemplo
    codigo_prueba = """
def funcion_compleja(x, y):
    if x > 0:
        if y > 0:
            print("Caso 1")
        else:
            print("Caso 2")
    else:
        while y < 10:
            y += 1
    return x + y

def funcion_simple():
    return "Hola mundo"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', encoding='utf-8') as tmp:
        tmp.write(codigo_prueba)
        temp_path = tmp.name

    try:
        print(f"--- Analizando archivo de prueba: {temp_path} ---\n")
        metricas = analizar_archivo_py(temp_path)
        
        for m in metricas:
            print(f"Función: '{m.name}'")
            print(f"  🔹 Complejidad Ciclomática (CC): {m.cyclomatic_complexity}")
            print(f"  🔹 Líneas de Código: {m.lines}")
            print(f"  🔹 Profundidad Máxima de Anidamiento: {m.max_nesting_depth}\n")
    finally:
        os.remove(temp_path)


---

## Parte 2: Validación de resultados con Radon

Después de calcular la complejidad ciclomática mediante el recorrido del AST, es conveniente validar que los resultados obtenidos por nuestro analizador sean consistentes con una herramienta especializada.

Para esta validación utilizamos **Radon**, una librería de Python capaz de calcular diferentes métricas de calidad y complejidad de código.

La comparación permite analizar una misma función mediante dos métodos:

1. Nuestro algoritmo basado en AST y pattern matching.
2. El cálculo realizado por Radon.

Si ambos resultados coinciden, tenemos una evidencia adicional de que nuestro cálculo de complejidad ciclomática está funcionando correctamente.

```python
from radon.complexity import cc_visit


def obtener_complejidad_radon(codigo_fuente: str) -> dict:
    """
    Calcula la complejidad ciclomática de las funciones usando Radon.

    Args:
        codigo_fuente (str): Código Python que se desea analizar.

    Returns:
        dict: Diccionario con el nombre de cada función y su
        complejidad ciclomática.
    """
    bloques = cc_visit(codigo_fuente)

    return {
        bloque.name: bloque.complexity
        for bloque in bloques
    }


def comparar_con_radon(ruta_archivo: str):
    """
    Compara la complejidad calculada por nuestro analizador con Radon.
    """
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        codigo = archivo.read()

    metricas_propias = analizar_archivo_py(ruta_archivo)
    metricas_radon = obtener_complejidad_radon(codigo)

    print("=== COMPARACIÓN CON RADON ===\n")

    for metrica in metricas_propias:
        propia = metrica.cyclomatic_complexity
        resultado_radon = metricas_radon.get(metrica.name)

        print(f"Función: {metrica.name}")
        print(f"  Nuestro analizador: {propia}")
        print(f"  Radon: {resultado_radon}")

        if resultado_radon is None:
            print("  Resultado: función no encontrada por Radon")
        elif propia == resultado_radon:
            print("  Resultado: COINCIDEN")
        else:
            print("  Resultado: NO COINCIDEN")

        print()
