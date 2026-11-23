from textwrap import dedent

import pytest

from src.analizador import analizar_archivo_py
from src.validacion import obtener_complejidad_radon


@pytest.mark.parametrize(
    "codigo, complejidad_esperada",
    [
        pytest.param(
            """
            def saludar():
                return "Hola"
            """,
            {"saludar": 1},
            id="funcion-simple",
        ),
        pytest.param(
            """
            def evaluar(x):
                if x > 0:
                    return x
                return 0
            """,
            None,
            id="if",
        ),
        pytest.param(
            """
            def evaluar(x, y):
                if x > 0:
                    if y > 0:
                        return 1
                    return 2
                return 3
            """,
            None,
            id="if-anidado",
        ),
        pytest.param(
            """
            def saludar():
                return "Hola"

            async def contar_positivos(numeros, limite):
                total = 0
                for numero in numeros:
                    if numero > 0 and numero < limite:
                        total += 1
                return total
            """,
            None,
            id="varias-funciones-for-y-booleano",
        ),
    ],
)
def test_complejidad_coincide_con_radon(tmp_path, codigo, complejidad_esperada):
    codigo = dedent(codigo)
    archivo = tmp_path / "codigo_prueba.py"
    archivo.write_text(codigo, encoding="utf-8")

    complejidad_propia = {
        metrica.name: metrica.cyclomatic_complexity
        for metrica in analizar_archivo_py(str(archivo))
    }
    complejidad_radon = obtener_complejidad_radon(codigo)

    assert complejidad_propia == complejidad_radon
    if complejidad_esperada is not None:
        assert complejidad_propia == complejidad_esperada
