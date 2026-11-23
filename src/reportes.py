"""Integra el análisis por función y lo exporta en formatos de presentación."""
import ast
import json
from dataclasses import asdict, dataclass
from html import escape

from src.analizador import calcular_metricas_funcion, es_funcion
from src.cfg import CFG, construir_cfg
from src.metricas import Halstead, calcular_halstead, complejidad_cognitiva, profundidad
from src.validacion import complejidades_por_posicion


@dataclass(frozen=True)
class InformeFuncion:
    nombre: str
    linea: int
    cc_propia: int
    cc_radon: int | None
    coincide: bool | None
    lineas: int
    profundidad: int
    altura_ast: int
    cognitiva: int
    halstead: Halstead
    cfg: CFG


@dataclass(frozen=True)
class Informe:
    archivo: str
    funciones: tuple[InformeFuncion, ...]


def analizar(codigo: str, archivo: str = "<fuente>") -> Informe:
    arbol = ast.parse(codigo, filename=archivo)
    radon = complejidades_por_posicion(arbol)
    funciones = sorted(filter(es_funcion, ast.walk(arbol)), key=lambda nodo: nodo.lineno)
    informes = []
    for funcion in funciones:
        propia = calcular_metricas_funcion(funcion)
        referencia = radon.get((funcion.name, funcion.lineno))
        informes.append(InformeFuncion(
            nombre=funcion.name,
            linea=funcion.lineno,
            cc_propia=propia.cyclomatic_complexity,
            cc_radon=referencia,
            coincide=None if referencia is None else propia.cyclomatic_complexity == referencia,
            lineas=propia.lines,
            profundidad=propia.max_nesting_depth,
            altura_ast=profundidad(funcion),
            cognitiva=complejidad_cognitiva(funcion),
            halstead=calcular_halstead(funcion),
            cfg=construir_cfg(funcion),
        ))
    return Informe(archivo, tuple(informes))


def a_json(informe: Informe) -> str:
    return json.dumps(asdict(informe), ensure_ascii=False, indent=2, allow_nan=False)


def a_texto(informe: Informe) -> str:
    partes = [f"Archivo: {informe.archivo}"]
    if not informe.funciones:
        partes.append("No se encontraron funciones.")
    for funcion in informe.funciones:
        radon = "no disponible" if funcion.cc_radon is None else funcion.cc_radon
        coincide = {None: "no comparable", True: "sí", False: "no"}[funcion.coincide]
        datos = (
            f"CC propia: {funcion.cc_propia} | CC Radon: {radon} | Coinciden: {coincide}",
            f"Líneas: {funcion.lineas} | Anidamiento: {funcion.profundidad} | Altura AST: {funcion.altura_ast}",
            f"Complejidad cognitiva: {funcion.cognitiva}",
            "Halstead: " + ", ".join(f"{k}={v:.4g}" for k, v in asdict(funcion.halstead).items()),
            f"CFG: {len(funcion.cfg.nodos)} nodos, {len(funcion.cfg.aristas)} aristas",
        )
        partes.append(f"\nFunción: {funcion.nombre} (línea {funcion.linea})")
        partes.extend(f"  {dato}" for dato in datos)
    return "\n".join(partes)


def a_html(informe: Informe) -> str:
    resumen = escape(a_texto(informe))
    grafos = []
    for funcion in informe.funciones:
        nodos = {n.id: f"{n.tipo} [{n.id}]" for n in funcion.cfg.nodos}
        filas = "\n".join(
            f"{nodos[a.origen]} → {nodos[a.destino]} ({a.etiqueta})"
            for a in funcion.cfg.aristas
        )
        titulo = escape(f"{funcion.nombre} (línea {funcion.linea})")
        grafos.append(f"<details><summary>CFG de {titulo}</summary><pre>{escape(filas)}</pre></details>")
    contenido = "\n".join(grafos)
    return (
        '<!doctype html>\n<html lang="es">\n<meta charset="utf-8">\n'
        '<title>Informe de complejidad</title>\n'
        '<h1>Informe de complejidad</h1>\n'
        f'<pre>{resumen}</pre>\n{contenido}\n</html>'
    )
