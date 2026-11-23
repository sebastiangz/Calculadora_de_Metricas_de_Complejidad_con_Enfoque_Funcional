"""Integra el análisis por función y lo exporta en formatos de presentación."""
import ast
import json
from dataclasses import asdict, dataclass
from html import escape

from src.analizador import calcular_metricas_funcion, es_funcion
from src.cfg import CFG, construir_cfg
from src.metricas import Halstead, calcular_halstead, complejidad_cognitiva, profundidad
from src.validacion import complejidades_por_posicion
from src.visualizacion import cfg_a_svg


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
    # Valida el contexto de return, break y otras sentencias sin ejecutar el archivo.
    compile(arbol, archivo, "exec", dont_inherit=True)
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
            "Halstead: " + ", ".join(f"{k}={v}" for k, v in asdict(funcion.halstead).items()),
            f"CFG: {len(funcion.cfg.nodos)} nodos, {len(funcion.cfg.aristas)} aristas",
        )
        partes.append(f"\nFunción: {funcion.nombre} (línea {funcion.linea})")
        partes.extend(f"  {dato}" for dato in datos)
    return "\n".join(partes)


def a_html(informe: Informe) -> str:
    resumen = escape(a_texto(informe))
    grafos = []
    for numero, funcion in enumerate(informe.funciones):
        titulo = escape(f"{funcion.nombre} (línea {funcion.linea})")
        svg = cfg_a_svg(funcion.cfg, numero)
        grafos.append(
            f'<details open><summary>CFG de {titulo}</summary>'
            f'<div class="grafo">{svg}</div></details>'
        )
    contenido = "\n".join(grafos)
    return (
        '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Informe de complejidad</title>\n'
        '<style>body{font:1rem system-ui,sans-serif;margin:2rem;color:#0f172a}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f5f9;padding:1rem}'
        'details{margin:1rem 0}summary{cursor:pointer;font-weight:600}'
        '.grafo{overflow-x:auto}svg{display:block;background:white}</style>\n'
        '</head>\n<body>\n<h1>Informe de complejidad</h1>\n'
        f'<pre>{resumen}</pre>\n{contenido}\n</body>\n</html>'
    )
