import ast
from dataclasses import dataclass
from typing import Tuple, Union

@dataclass(frozen=True)
class FunctionMetrics:
    name: str
    cyclomatic_complexity: int
    lines: int
    max_nesting_depth: int

def es_funcion(nodo: ast.AST) -> bool:
    """Verifica si un nodo del AST corresponde a una función síncrona o asíncrona."""
    return isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef))

def analizar_archivo_py(ruta_archivo: str) -> Tuple[FunctionMetrics, ...]:
    """Lee un archivo .py, analiza su AST y extrae métricas por función."""
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    tree = ast.parse(contenido)
    
    return tuple(map(calcular_metricas_funcion, filter(es_funcion, ast.walk(tree))))

def calcular_metricas_funcion(func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> FunctionMetrics:
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
                    
                case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef():
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
