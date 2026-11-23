import sys
import tokenize
from pathlib import Path

from src.reportes import a_html, a_json, a_texto, analizar


def main(argumentos: list[str]) -> int:
    formatos = {"--json": a_json, "--html": a_html}
    if len(argumentos) == 1 and not argumentos[0].startswith("--"):
        exportar = a_texto
    elif (
        len(argumentos) == 2
        and not argumentos[0].startswith("--")
        and argumentos[1] in formatos
    ):
        exportar = formatos[argumentos[1]]
    else:
        print("Uso: python main.py archivo.py [--json | --html]", file=sys.stderr)
        return 2

    ruta = Path(argumentos[0])
    try:
        if not ruta.is_file():
            print(f"Error: no se encontró el archivo «{ruta}».", file=sys.stderr)
            return 1
        if ruta.suffix != ".py":
            print("Error: el archivo debe tener extensión .py.", file=sys.stderr)
            return 1

        with tokenize.open(str(ruta)) as archivo:
            codigo = archivo.read()
        informe = analizar(codigo, str(ruta))
    except SyntaxError as error:
        ubicacion = f" en la línea {error.lineno}" if error.lineno is not None else ""
        print(f"Error de sintaxis{ubicacion}: {error.msg}.", file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as error:
        print(f"Error al leer «{ruta}»: {error}", file=sys.stderr)
        return 1
    except RecursionError:
        print("Error: el código supera el límite de profundidad del análisis.", file=sys.stderr)
        return 1

    print(exportar(informe))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
