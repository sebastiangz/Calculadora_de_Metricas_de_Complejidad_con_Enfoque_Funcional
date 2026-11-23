"""Métricas calculadas sobre el cuerpo de una función."""
import ast
from dataclasses import dataclass
from math import log2

AMBITOS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def profundidad(nodo: ast.AST) -> int:
    """Altura del AST en nodos. Una hoja tiene altura 1."""
    return 1 + max(map(profundidad, ast.iter_child_nodes(nodo)), default=0)


def _cognitiva(nodo: ast.AST, nivel: int) -> int:
    match nodo:
        case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef() | ast.Lambda():
            return 0
        case ast.If():
            return _condicional(nodo, nivel, 1 + nivel)
        case ast.For() | ast.AsyncFor() | ast.While():
            return (1 + nivel + _sumar(ast.iter_child_nodes(nodo), nivel + 1)
                    + bool(nodo.orelse))
        case ast.IfExp() | ast.ExceptHandler() | ast.Match():
            return 1 + nivel + _sumar(ast.iter_child_nodes(nodo), nivel + 1)
        case ast.BoolOp() | ast.Break() | ast.Continue():
            return 1 + _sumar(ast.iter_child_nodes(nodo), nivel)
        case _:
            return _sumar(ast.iter_child_nodes(nodo), nivel)


def _sumar(nodos, nivel: int) -> int:
    return sum(_cognitiva(nodo, nivel) for nodo in nodos)


def _condicional(nodo: ast.If, nivel: int, incremento: int) -> int:
    total = incremento + _cognitiva(nodo.test, nivel) + _sumar(nodo.body, nivel + 1)
    if len(nodo.orelse) == 1:
        alternativo = nodo.orelse[0]
        if isinstance(alternativo, ast.If) and alternativo.col_offset == nodo.col_offset:
            return total + _condicional(alternativo, nivel, 1)
    return total + bool(nodo.orelse) + _sumar(nodo.orelse, nivel + 1)


def complejidad_cognitiva(funcion: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Puntúa decisiones, anidamiento y saltos según las reglas del proyecto."""
    return _sumar(funcion.body, 0)


@dataclass(frozen=True)
class Halstead:
    operadores_distintos: int
    operandos_distintos: int
    total_operadores: int
    total_operandos: int
    vocabulario: int
    longitud: int
    volumen: float
    dificultad: float
    esfuerzo: float


def _elementos(nodo: ast.AST):
    if isinstance(nodo, AMBITOS):
        return

    match nodo:
        case ast.BinOp(op=op) | ast.UnaryOp(op=op):
            yield "operador", type(op).__name__
        case ast.BoolOp(op=op, values=valores):
            yield from (("operador", type(op).__name__) for _ in valores[1:])
        case ast.Compare(ops=ops):
            yield from (("operador", type(op).__name__) for op in ops)
        case ast.AugAssign(op=op):
            yield "operador", "Aug" + type(op).__name__
        case ast.Assign() | ast.AnnAssign() | ast.NamedExpr():
            yield "operador", type(nodo).__name__
        case ast.Name(id=nombre):
            yield "operando", ("nombre", nombre)
        case ast.Constant(value=valor):
            yield "operando", (type(valor).__name__, repr(valor))

    for hijo in ast.iter_child_nodes(nodo):
        yield from _elementos(hijo)


def calcular_halstead(funcion: ast.FunctionDef | ast.AsyncFunctionDef) -> Halstead:
    """Aplica las fórmulas de Halstead a las categorías AST del proyecto."""
    elementos = tuple(elemento for nodo in funcion.body for elemento in _elementos(nodo))
    operadores = tuple(valor for tipo, valor in elementos if tipo == "operador")
    operandos = tuple(valor for tipo, valor in elementos if tipo == "operando")
    n1, n2 = len(set(operadores)), len(set(operandos))
    N1, N2 = len(operadores), len(operandos)
    vocabulario, longitud = n1 + n2, N1 + N2
    volumen = longitud * log2(vocabulario) if vocabulario else 0.0
    dificultad = (n1 / 2) * (N2 / n2) if n2 else 0.0
    return Halstead(n1, n2, N1, N2, vocabulario, longitud, volumen, dificultad,
                    dificultad * volumen)
