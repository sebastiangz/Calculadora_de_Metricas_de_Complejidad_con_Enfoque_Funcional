"""Representación lógica del flujo de control intraprocedimental."""
import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class Nodo:
    id: int
    tipo: str
    linea: int | None


@dataclass(frozen=True)
class Arista:
    origen: int
    destino: int
    etiqueta: str = "siguiente"


@dataclass(frozen=True)
class CFG:
    entrada: int
    salida: int
    nodos: tuple[Nodo, ...]
    aristas: tuple[Arista, ...]


def construir_cfg(funcion: ast.FunctionDef | ast.AsyncFunctionDef) -> CFG:
    """Construye desde la salida. Cada bloque recibe su continuación."""
    entrada, salida = 0, 1
    nodos = [Nodo(entrada, "entrada", None), Nodo(salida, "salida", None)]
    aristas: list[Arista] = []

    def conectar(origen: int, destino: int, etiqueta: str = "siguiente") -> None:
        aristas.append(Arista(origen, destino, etiqueta))

    def bloque(
        sentencias: list[ast.stmt],
        siguiente: int,
        bucle: tuple[int, int] | None = None,
    ) -> int:
        for sentencia in reversed(sentencias):
            actual = len(nodos)
            tipo = type(sentencia).__name__
            if isinstance(sentencia, (ast.Try, ast.Match, ast.With, ast.AsyncWith)):
                tipo = f"opaco:{tipo}"
            elif tipo == "TryStar":
                tipo = "opaco:TryStar"
            nodos.append(Nodo(actual, tipo, sentencia.lineno))

            match sentencia:
                case ast.If():
                    conectar(actual, bloque(sentencia.body, siguiente, bucle), "verdadero")
                    conectar(actual, bloque(sentencia.orelse, siguiente, bucle), "falso")
                case ast.For() | ast.AsyncFor() | ast.While():
                    iteracion = bloque(sentencia.body, actual, (actual, siguiente))
                    normal = bloque(sentencia.orelse, siguiente, bucle)
                    conectar(actual, iteracion, "iterar")
                    conectar(actual, normal, "fin del bucle")
                case ast.Return() | ast.Raise():
                    conectar(actual, salida, tipo.lower())
                case ast.Break() if bucle is not None:
                    conectar(actual, bucle[1], "break")
                case ast.Continue() if bucle is not None:
                    conectar(actual, bucle[0], "continue")
                case _:
                    conectar(actual, siguiente)

            siguiente = actual
        return siguiente

    conectar(entrada, bloque(funcion.body, salida))
    return CFG(entrada, salida, tuple(nodos), tuple(aristas))
