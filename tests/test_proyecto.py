import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.cfg import construir_cfg
from src.metricas import calcular_halstead, complejidad_cognitiva, profundidad
from src.reportes import a_html, a_json, analizar


def funcion(codigo):
    return ast.parse(codigo).body[0]


def test_cognitiva_anidamiento_y_elif():
    nodo = funcion("""def f(x, y):
    if x:
        while y:
            break
    elif y and x:
        return 1
    else:
        return 0
""")
    assert complejidad_cognitiva(nodo) == 7


def test_metricas_excluyen_ambitos_internos():
    nodo = funcion("""def f():
    def interna(x):
        if x + 1:
            return 1
    pass
""")
    assert complejidad_cognitiva(nodo) == 0
    assert calcular_halstead(nodo).volumen == 0
    assert profundidad(ast.Pass()) == 1
    assert profundidad(ast.parse("pass")) == 2


def test_halstead_valores_y_formulas():
    nodo = funcion("def f(x):\n    return x + x * 2")
    resultado = calcular_halstead(nodo)
    assert (resultado.operadores_distintos, resultado.operandos_distintos) == (2, 2)
    assert (resultado.total_operadores, resultado.total_operandos) == (2, 3)
    assert (resultado.vocabulario, resultado.longitud) == (4, 5)
    assert resultado.volumen == pytest.approx(10)
    assert resultado.dificultad == pytest.approx(1.5)
    assert resultado.esfuerzo == pytest.approx(15)


def test_cfg_secuencia_if_y_retorno():
    grafo = construir_cfg(funcion("""def f(x):
    a = 1
    if x:
        return a
    else:
        a = 2
    return a
"""))
    ids = {n.linea: n.id for n in grafo.nodos if n.linea is not None}
    enlaces = {(a.origen, a.destino, a.etiqueta) for a in grafo.aristas}
    assert enlaces == {
        (grafo.entrada, ids[2], "siguiente"),
        (ids[2], ids[3], "siguiente"),
        (ids[3], ids[4], "verdadero"),
        (ids[3], ids[6], "falso"),
        (ids[4], grafo.salida, "return"),
        (ids[6], ids[7], "siguiente"),
        (ids[7], grafo.salida, "return"),
    }


def test_cfg_bucles_anidados_y_else():
    grafo = construir_cfg(funcion("""def f(xs):
    for x in xs:
        while x:
            if x == 1:
                break
            continue
    else:
        return 1
"""))
    ids = {n.linea: n.id for n in grafo.nodos if n.linea is not None}
    enlaces = {(a.origen, a.destino, a.etiqueta) for a in grafo.aristas}
    assert enlaces == {
        (grafo.entrada, ids[2], "siguiente"),
        (ids[2], ids[3], "iterar"),
        (ids[2], ids[8], "fin del bucle"),
        (ids[3], ids[4], "iterar"),
        (ids[3], ids[2], "fin del bucle"),
        (ids[4], ids[5], "verdadero"),
        (ids[4], ids[6], "falso"),
        (ids[5], ids[2], "break"),
        (ids[6], ids[3], "continue"),
        (ids[8], grafo.salida, "return"),
    }


def test_reporte_json_tiene_metricas_cfg_y_referencias_por_linea():
    informe = analizar("""def f():
    return 1

def f(x):
    if x:
        return 2
""")
    simple, condicional = json.loads(a_json(informe))["funciones"]
    assert [simple["cc_radon"], condicional["cc_radon"]] == [1, 2]
    assert condicional["coincide"] is True
    assert condicional["cognitiva"] == 1
    assert condicional["halstead"]["total_operandos"] == 2
    assert any(a["etiqueta"] == "verdadero" for a in condicional["cfg"]["aristas"])


def test_reporte_html_escapa_el_nombre_del_archivo():
    html = a_html(analizar("def f(): pass", "<script>&.py"))
    assert "&lt;script&gt;&amp;.py" in html
    assert "<script>" not in html
    assert "<summary>CFG de f (línea 1)</summary>" in html


@pytest.mark.parametrize("opcion", [[], ["--json"], ["--html"]])
def test_cli_formatos(tmp_path, opcion):
    archivo = tmp_path / "ejemplo.py"
    archivo.write_text("def f(x):\n    return x + 1\n", encoding="utf-8")
    main = Path(__file__).resolve().parents[1] / "main.py"
    resultado = subprocess.run(
        [sys.executable, str(main), str(archivo), *opcion],
        capture_output=True, text=True, check=True,
    )
    assert not resultado.stderr
    if opcion == ["--json"]:
        assert json.loads(resultado.stdout)["funciones"][0]["coincide"] is True
    elif opcion == ["--html"]:
        assert "<summary>CFG de f (línea 1)</summary>" in resultado.stdout
    else:
        assert "CC propia: 1 | CC Radon: 1 | Coinciden: sí" in resultado.stdout


def test_cli_falla_con_error_de_sintaxis(tmp_path):
    archivo = tmp_path / "mal.py"
    archivo.write_text("def f(:", encoding="utf-8")
    main = Path(__file__).resolve().parents[1] / "main.py"
    resultado = subprocess.run(
        [sys.executable, str(main), str(archivo), "--json"],
        capture_output=True, text=True,
    )
    assert resultado.returncode == 1
    assert not resultado.stdout
    assert "Error de sintaxis en la línea 1" in resultado.stderr


def test_radon_distingue_metodo_y_funcion_interna():
    informe = analizar("""class C:
    def f(self):
        def f(x):
            if x:
                return 1
        return f(True)
""")
    assert [(f.linea, f.cc_radon) for f in informe.funciones] == [(2, 1), (3, 2)]
