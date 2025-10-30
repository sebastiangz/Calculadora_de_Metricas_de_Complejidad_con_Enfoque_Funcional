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
