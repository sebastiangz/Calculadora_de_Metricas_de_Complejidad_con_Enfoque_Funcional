import ast
import json
import subprocess
import sys
import locale
from html import escape
from math import log2
from pathlib import Path
from textwrap import indent
from xml.etree import ElementTree

import pytest
from radon.metrics import h_visit

from src.analizador import analizar_archivo_py
from src.metricas import calcular_halstead, profundidad
from src.reportes import a_html, a_json, a_texto, analizar

RAIZ = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "cuerpo, cc, radon, cognitiva",
    [
        pytest.param("return 0", 1, 1, 0, id="base"),
        pytest.param("if x: return 1", 2, 2, 1, id="if"),
        pytest.param("if x: return 1\nelse: return 0", 2, 2, 2, id="if-else"),
        pytest.param("if x: return 1\nelif y: return 0", 3, 3, 2, id="elif"),
        pytest.param("if x:\n    if y: return 1", 3, 3, 3, id="if-anidado"),
        pytest.param("for i in x: pass", 2, 2, 1, id="for"),
        pytest.param("while x: continue", 2, 2, 2, id="while-continue"),
        pytest.param("async for i in x: pass", 2, 2, 1, id="async-for"),
        pytest.param("return (x and y) or z", 3, 3, 2, id="and-or"),
        pytest.param("try: return x\nexcept ValueError: return 0", 2, 2, 1, id="except"),
        pytest.param("match x:\n    case 0: return 0\n    case _: return 1", 3, 2, 1, id="match"),
        pytest.param("for i in x: pass\nelse: pass", 2, 3, 2, id="for-else"),
        pytest.param("return lambda y: y and x", 1, 2, 0, id="lambda"),
    ],
)
def test_metricas_por_construccion(cuerpo, cc, radon, cognitiva):
    codigo = "async def f(x, y, z):\n" + indent(cuerpo, "    ")
    resultado, = analizar(codigo).funciones
    assert (resultado.cc_propia, resultado.cc_radon, resultado.cognitiva) == (cc, radon, cognitiva)
    assert resultado.coincide is (cc == radon)


def test_parser_ignora_la_cabecera_y_separa_ambitos(tmp_path):
    codigo = """@decorador or alternativo
def f(x=(1 and 2)):
    def f():
        if x:
            return 1
    return f()
"""
    ruta = tmp_path / "fuente.py"
    ruta.write_text(codigo, encoding="utf-8")
    metricas = analizar_archivo_py(str(ruta))
    assert isinstance(metricas, tuple)
    assert [(m.name, m.cyclomatic_complexity, m.lines, m.max_nesting_depth) for m in metricas] == [
        ("f", 1, 5, 0), ("f", 2, 3, 1),
    ]
    assert [(f.linea, f.cc_radon) for f in analizar(codigo).funciones] == [(2, 1), (3, 2)]
    assert profundidad(ast.parse("if x:\n    pass")) == 4


def test_halstead_formula_y_operadores_repetidos():
    codigo = """def f(x):
    x = x + x
    x += 1
    return -x if 1 < x <= 2 and x and x else 0
"""
    h = calcular_halstead(ast.parse(codigo).body[0])
    assert (h.operadores_distintos, h.operandos_distintos) == (7, 4)
    assert (h.total_operadores, h.total_operandos) == (8, 12)
    assert (h.vocabulario, h.longitud) == (11, 20)
    assert h.volumen == pytest.approx(20 * log2(11))
    assert h.dificultad == pytest.approx(10.5)
    assert h.esfuerzo == pytest.approx(10.5 * 20 * log2(11))


def test_halstead_coincide_con_radon_en_una_suma():
    codigo = "def f(x):\n    return x + 1"
    h = calcular_halstead(ast.parse(codigo).body[0])
    _, referencia = h_visit(codigo).functions[0]
    assert (h.operadores_distintos, h.operandos_distintos) == (referencia.h1, referencia.h2)
    assert (h.total_operadores, h.total_operandos) == (referencia.N1, referencia.N2)
    assert h.volumen == pytest.approx(referencia.volume)


def test_svg_representa_los_mismos_nodos_y_aristas_del_json():
    informe = analizar("""def f(xs):
    for x in xs:
        if x:
            continue
        break
    return 0

def g():
    pass
""", "<&>.py")
    html = a_html(informe)
    assert escape(a_texto(informe)) in html
    assert 'id="flecha-cfg-0"' in html and 'id="flecha-cfg-1"' in html
    svg = ElementTree.fromstring(html[html.index("<svg"):html.index("</svg>") + len("</svg>")])
    datos = json.loads(a_json(informe))["funciones"][0]["cfg"]
    ns = "{http://www.w3.org/2000/svg}"
    grupos = svg.findall(f"{ns}g")
    nodos = [g for g in grupos if "data-nodo" in g.attrib]
    aristas = [g for g in grupos if "data-origen" in g.attrib]

    assert {int(g.attrib["data-nodo"]) for g in nodos} == {n["id"] for n in datos["nodos"]}
    assert {"entrada", "salida", "If · L3", "Return · L6"} <= {
        g.findtext(f"{ns}text") for g in nodos
    }
    assert {
        (int(g.attrib["data-origen"]), int(g.attrib["data-destino"]), g.findtext(f"{ns}title"))
        for g in aristas
    } == {(a["origen"], a["destino"], a["etiqueta"]) for a in datos["aristas"]}
    assert {"verdadero", "falso", "iterar", "break", "continue"} <= {
        g.findtext(f"{ns}title") for g in aristas
    }
    assert all(g.find(f"{ns}path").get("marker-end") == "url(#flecha-cfg-0)" for g in aristas)


@pytest.mark.parametrize(
    "argumentos, estado, mensaje",
    [
        pytest.param([], 2, "Uso:", id="sin-argumentos"),
        pytest.param(["ok.py", "--json", "--html"], 2, "Uso:", id="demasiados"),
        pytest.param(["--json", "--html"], 2, "Uso:", id="sin-archivo"),
        pytest.param(["ausente.py"], 1, "no se encontró", id="inexistente"),
        pytest.param(["otro.txt"], 1, "extensión .py", id="extension"),
        pytest.param(["vacio.py"], 0, "No se encontraron funciones", id="vacio"),
        pytest.param(["sin_funciones.py"], 0, "No se encontraron funciones", id="sin-funciones"),
        pytest.param(["break.py", "--json"], 1, "Error de sintaxis en la línea 2", id="contexto"),
        pytest.param(["invalido.py"], 1, "Error", id="codificacion-invalida"),
        pytest.param(["latin.py", "--json"], 0, '"nombre": "año"', id="codificacion-declarada"),
    ],
)
def test_cli_codigos_y_entradas(tmp_path, argumentos, estado, mensaje):
    for nombre, contenido in {
        "ok.py": b"def f(): pass\n",
        "otro.txt": b"",
        "vacio.py": b"",
        "sin_funciones.py": b"x = 1\n",
        "break.py": b"def f():\n    break\n",
        "invalido.py": bytes([255]),
        "latin.py": "# coding: latin-1\ndef año(): pass\n".encode("latin-1"),
    }.items():
        (tmp_path / nombre).write_bytes(contenido)
    resultado = subprocess.run(
        [sys.executable, str(RAIZ / "main.py"), *argumentos],
        cwd=tmp_path, capture_output=True, text=True, encoding=locale.getpreferredencoding(False),
    )
    assert resultado.returncode == estado
    if estado == 0:
        assert not resultado.stderr
        assert mensaje in resultado.stdout
    else:
        assert not resultado.stdout
        assert mensaje in resultado.stderr
