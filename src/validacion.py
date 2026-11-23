import ast

from radon.complexity import cc_visit
from radon.visitors import Class, ComplexityVisitor, Function


def obtener_complejidad_radon(codigo_fuente: str) -> dict[str, int]:
    """Devuelve la complejidad ciclomática de los bloques de Radon por nombre."""
    bloques = cc_visit(codigo_fuente)
    return {bloque.name: bloque.complexity for bloque in bloques}


def _funciones_radon(bloques):
    for bloque in bloques:
        if isinstance(bloque, Function):
            yield bloque
            yield from _funciones_radon(bloque.closures)
        elif isinstance(bloque, Class):
            yield from _funciones_radon(bloque.methods)
            yield from _funciones_radon(bloque.inner_classes)


def complejidades_por_posicion(arbol: ast.AST) -> dict[tuple[str, int], int]:
    bloques = ComplexityVisitor.from_ast(arbol).blocks
    return {
        (funcion.name, funcion.lineno): funcion.complexity
        for funcion in _funciones_radon(bloques)
    }
